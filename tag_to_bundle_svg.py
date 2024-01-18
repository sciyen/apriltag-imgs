#!/usr/bin/env python3

import os
import re
import sys
import argparse
import math
import json
from PIL import Image

# Thanks to https://stackoverflow.com/a/54547257
def dir_path(file_path):
    if os.path.isdir(file_path):
        return file_path
    else:
        raise argparse.ArgumentTypeError(f'Supplied argument "{file_path}" is not a valid file path.')


parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(
    description='A script to convert pre-generated apriltag .png files into SVG format.',
    epilog='Example: "python3 tag_to_bundle_svg.py --tag_folder=tagStandard41h12 --tag_prefix=tag41_12_ --out_folder=outputs --num_bundles=20 --size=90mm --num_tile=2 --stride=0"'
)
parser.add_argument(
    '--tag_folder', type=dir_path, dest="tag_folder",
    help='The path to the folder containing apriltag png you want to convert.'
)
parser.add_argument(
    '--tag_prefix', type=str, dest="tag_prefix",
    help='The tag filename prefix.'
)
parser.add_argument(
    '--out_folder', type=dir_path, dest="out_folder",
    help='The path to the SVG output folder.'
)
parser.add_argument(
    '--num_bundles', type=int, default='1', dest="num_bundles", 
    help='The number of bundles to generate.'
)
parser.add_argument(
    '--start_index', type=int, required=False, default='0', dest="start_index", 
    help='The starting index of bundles.'
)
parser.add_argument(
    '--size', type=str, required=False, default='20mm', dest="svg_size", 
    help='The size (edge length) of the generated svg such as "20mm" "2in" "20px"'
)
parser.add_argument(
    '--num_tile', type=int, required=False, default='1', dest="num_tile", 
    help='The number of tiles in a bundled tag. For example, a num_tile of 3 will generate a 3x3 grid of tags.'
)
parser.add_argument(
    '--stride', type=int, required=False, default='1', dest="stride", 
    help='The number of blank tags between each tag in a bundle. For example, a stride of 1 will generate a 3x3 grid of tags with 1 blank tag between each tag.'
)
parser.add_argument(
    '--margin', type=int, required=False, default='1', dest="tag_margin", 
    help='Number of bits of white margin around each tag.'
)
parser.add_argument(
    '--individual_print', type=str, required=False, default='false', dest="individual", 
    help='Whether the marker in the bundled tag is exported individually.'
)

class BundledTag:
    def __init__(self, args) -> None:
        self.tag_folder = args.tag_folder
        self.out_folder = args.out_folder
        self.tag_prefix = args.tag_prefix

        self.svg_size = args.svg_size   # size with unit
        self.num_tile = args.num_tile   # integer
        self.stride = args.stride       # integer (number of tiles between each tag)

        # Parsing svg size
        self.size = int(re.search(r'[0-9]+', self.svg_size).group(0))   # integer
        self.unit = re.search(r'[a-zA-Z]+', self.svg_size).group(0)     # string (mm / in / px)
        assert self.unit in ['mm', 'in', 'px'], 'Error: Invalid unit. Supported units are "mm", "in", "px".'
        print(f'Generating bundled tags with size: {self.size}{self.unit}')
        

        self.individual = args.individual

    def get_tag_filename(self, tag_id):
        return os.path.join(self.tag_folder, f'{self.tag_prefix}{tag_id:05d}.png')
    
    def gen_bundled_tag(self, start_tag_id):
        """
        Generate a bundled tag.
        @param start_tag_id: The id of the first tag in the bundle.
        @return: svg_text: The SVG text of the bundled tag.
        @return: bundle_desc: a dictionary containing the basic information of a bundled tag {name, layout}
        """
        def gen_apriltag_svg(width, height, pixel_array, size, pos_x, pos_y):
            """
            Generate an SVG from a single apriltag image.
            @param width: The width of the original apriltag image.
            @param height: The height of the original apriltag image.
            @param pixel_array: The pixel array of the original apriltag image.
            @param size: The size of the SVG to generate.
            """
            def gen_rgba(rbga):
                (_r, _g, _b, _raw_a) = rbga
                _a = _raw_a / 255
                return f'rgba({_r}, {_g}, {_b}, {_a})'

            def gen_gridsquare(row_num, col_num, pixel):
                _rgba = gen_rgba(pixel)
                _id = f'box{row_num}-{col_num}'
                return f'\t<rect width="1" height="1" x="{row_num}" y="{col_num}" fill="{_rgba}" id="{_id}"/>\n'
            
            svg_text = f'<g>\n<svg x="{pos_x}" y="{pos_y}" width="{size}" height="{size}"  viewBox="0,0,{width},{height}">\n'
            # print(f'Generating tag at ({pos_x}, {pos_y}) with size: {size}')
            # print(f'width: {width}, height: {height}')
            for _y in range(height):
                for _x in range(width):
                    svg_text += gen_gridsquare(_x, _y, pixel_array[_x, _y])
            svg_text += '</svg>\n</g>\n\n'
            return svg_text
        
        def gen_apriltag_description(id, size, pos_x, pos_y, unit):
            """
            Generate an SVG description for a single apriltag image.
            @param id: The id of the apriltag.
            @param size: The size of the generated tag.
            @param pos_x: The x position of the tag.
            @param pos_y: The y position of the tag.
            @param unit: The unit of size, pos_x, and pos_y.
            """
            scale = 1
            if unit == 'mm':
                scale = 0.001
            elif unit == 'in':
                scale = 0.0254
            
            description = {
                "id": id,
                "size": size * scale,
                "x": pos_x * scale,
                "y": pos_y * scale,
                "qw": 1,
                "qx": 0,
                "qy": 0,
                "qz": 0
            }
            return description

        svg_text = ''
        desc = []
        count = 0

        center_x = (self.size * self.num_tile + self.tag_margin * (self.num_tile - 1)) / 2
        center_y = (self.size * self.num_tile + self.tag_margin * (self.num_tile - 1)) / 2
        for _y in range(self.num_tile):
            for _x in range(self.num_tile):
                tag_id = _y * self.num_tile + _x
                actual_tag_id = count + start_tag_id

                if tag_id % (self.stride + 1) == 0:
                    tag_file = self.get_tag_filename(actual_tag_id)
                    print(f'Generating tag: {tag_file}')
                    with Image.open(tag_file, 'r') as im:
                        width, height = im.size
                        pixel_array = im.load()
                        pos_x = _x * (self.size + self.tag_margin)
                        pos_y = _y * (self.size + self.tag_margin)

                        if self.individual == 'true':
                            svg_text = ''
                            svg_text += gen_apriltag_svg(width, height, pixel_array, self.svg_size, 
                                                         f'{0}{self.unit}', f'{0}{self.unit}')
                        else:
                            svg_text += gen_apriltag_svg(width, height, pixel_array, self.svg_size, 
                                                         f'{pos_x}{self.unit}', f'{pos_y}{self.unit}')
                            
                        desc.append(gen_apriltag_description(
                            actual_tag_id, self.size, 
                            pos_x - center_x, pos_y - center_y, 
                            self.unit))
                    
                        if self.individual == 'true':
                            svg = self.svg_wrapper(svg_text, self.svg_size, self.svg_size)
                            self.svg_save(svg, os.path.join(self.out_folder, f'{self.tag_prefix}{actual_tag_id:05d}_{_x}-{_y}.svg'))
                        
                        count += 1

        bundle_desc = {
            "name": f'{self.tag_prefix}bundle_{start_tag_id:05d}-{self.num_tile}x{self.num_tile}',
            "layout": desc
        }

        margin_size = self.tag_margin * (self.num_tile - 1)
        bundle_size = f'{self.size * self.num_tile + margin_size}{self.unit}'
        svg_text = self.svg_wrapper(svg_text, bundle_size, bundle_size)
        return svg_text, bundle_desc

    def svg_wrapper(self, content, width, height):
        # svg_text = '<?xml version="1.0" standalone="yes"?>\n'
        svg_text = ''
        svg_text += f'<svg width="{width}" height="{height}" viewBox="0,0,{width},{height}" xmlns="http://www.w3.org/2000/svg">\n'
        svg_text += content
        svg_text += '</svg>\n'
        return svg_text
    
    def svg_save(self, svg_text, filename):
        with open(filename, 'w') as fp:
            fp.write(svg_text)
        print(f'Output SVG file: {filename}.')
    
    def gen_batch_bundles(self, start_tag_id, num_bundle):
        bundle_desc = []
        for i in range(num_bundle):
            tag_in_bundle = self.num_tile * self.num_tile - self.stride * math.floor(self.num_tile * self.num_tile / (self.stride + 1))
            svg, desc = self.gen_bundled_tag(start_tag_id + i * tag_in_bundle)
            bundle_desc.append(desc)
            if self.individual != 'true':
                self.svg_save(svg, os.path.join(self.out_folder, f'{desc["name"]}.svg'))
        return bundle_desc

def main():
    args = parser.parse_args()
    bundled_tag = BundledTag(args)

    # TODO: maximum number check
    desc = bundled_tag.gen_batch_bundles(args.start_index, args.num_bundles)
    with open(os.path.join(args.out_folder, 'bundle_description.json'), 'w') as fp:
        json.dump(desc, fp, indent=4)

if __name__ == "__main__":
    main()
