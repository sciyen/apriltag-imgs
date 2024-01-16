AprilTag-imgs
=============

Images of all tags from all the pre-generated [AprilTag 3](https://github.com/AprilRobotics/apriltags) families. You can generate your own layouts or images of tags using our other repo, [AprilTag-generation](https://github.com/AprilRobotics/apriltag-generation).

If the format of the markers is very small (ex : by default, 9x9 pixels), you'll need to rescale them. To do so, you may use the following imagemagick command (Unix) : 

~~~
convert <small_marker>.png -scale <scale_chosen_in_percent>% <big_marker>.png
~~~

Alternately, you can use the supplied native Python 3 script `tag_to_svg.py` to create a SVG (Scalable Vector Graphics) Version of a tag. For example:
~~~
python3 tag_to_svg.py tagStandard52h13/tag52_13_00007.png tag52_13_00007.svg --size=20mm
~~~

## Batched AprilTag Bundles Generation
You can also use the script `tag_to_bundle_svg.py` to create batch of bundle of tags. For example:
```bash
python3 tag_to_bundle_svg.py \
    --tag_folder=tagStandard41h12 --tag_prefix=tag41_12_ \
    --out_folder=outputs --num_bundles=20 \
    --size=90mm --num_tile=2 --stride=0
```
This script will generate 20 svg files and a description in json in `outputs` folder. Each svg file contains 4 tags (2x2) with a size of 90mm. The description file matches the one used by [apriltag_ros](https://github.com/AprilRobotics/apriltag_ros), which is defined in [apriltag_ros/config
/tags.yaml](https://github.com/AprilRobotics/apriltag_ros/blob/master/apriltag_ros/config/tags.yaml).