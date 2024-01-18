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


## To Build A Large Marker
The following command generate a 11 by 11 grid of tags. With the `individual_print` flag, each tag is exported individually and one obtains 61 svg file. 
```bash
python3 tag_to_bundle_svg.py --tag_folder=tagStandard41h12  --out_folder=outputs --num_bundles=1 --size=180mm --num_tile=11 --stride=1 --margin=1 --individual_print=true
```

After obtaining the svg files, you can use [inkscape](https://inkscape.org/) to convert them into pdf. Using the solution from [Johannski](https://alpha.inkscape.org/vectors/www.inkscapeforum.com/viewtopic7a7e.html?t=16743#), put all svg files in a folder and create a batch file (e.g. `convert.bat`) with the following content:
```bat
@Echo off

set count=0
set validInput1=svg
set validInput2=pdf
set validInput3=eps
set validOutput1=eps
set validOutput2=pdf
set validOutput3=png

echo This script allows you to convert all files in this folder from one file type to another.

set valid=0
echo Allowed file types for source: %validInput1%, %validInput2%, %validInput3%

:whileInNotCorrect
    set /p sourceType=What file type do you want to use as a source?
    if "%sourceType%" EQU "%validInput1%" set valid=1
   if "%sourceType%" EQU "%validInput2%" set valid=1
   if "%sourceType%" EQU "%validInput3%" set valid=1
   if %valid% EQU 0 (
        echo Invalid input! Please use one of the following: %validInput1%, %validInput2%, %validInput3%
      goto :whileInNotCorrect
      )

set valid=0
echo Allowed file types for output: %validOutput1%, %validOutput2%, %validOutput3%      
:whileOutNotCorrect
    set /p outputType=What file type do you want to convert to?
    if "%outputType%" EQU "%validOutput1%" set valid=1
   if "%outputType%" EQU "%validOutput2%" set valid=1
   if "%outputType%" EQU "%validOutput3%" set valid=1
   if %valid% EQU 0 (
        echo Invalid input! Please use one of the following: %validOutput1%, %validOutput2%, %validOutput3%   
      goto :whileOutNotCorrect
      )
      
set /p dpi=With what dpi should it be exported (e.g. 300)?

for %%i in (.\*.%sourceType%) do (
   echo %%i.%outputType%
   inkscape %%i --export-type=%outputType% --export-filename=%%i.%outputType% --export-dpi=%dpi%
   )
   
pause
```
Note that this script requires [Inkscape](https://inkscape.org/) to be installed and added to the path. After obtaining pdf files, you can combine them into a single pdf file using pdf tools.