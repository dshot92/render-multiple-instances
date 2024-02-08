# Render Script Addon

4.1 Panel api wont work for 4.0 and lesser version.
checkout the 4.0 tag

## Installation

1. In blender, go to: Edit -> Preferences -> Add-ons -> Install.
2. Select the downloaded file and click on -> Install Add-on.
3. Enable it by clicking on checkbox.
4. Once enabled is located in Output Properties -> Render Multiple Instances

## Usage

The addon works based on the blender render output folder.

You can either use the relative or absolute paths scheme.

Example of relative output folder:
`//export_folder/sequences/seq_001/`

or with a specific file name:
`//export_folder/sequences/seq_001/frame_####`
<br>
<br>

### The panel is subdivided in 4 subpanels

-   Frame Range Override
    -   Self Explaining
-   Render Instances
    -   Select the number of instances that maximize the resources of your machine
    -   Save and Render button will actually save the project to ensure all instances are getting the up to date file to render
-   Sequence to .mp4
    -   Will only show up if FFmpeg is installed
    -   Quality 1 is lossless, while 50 is low quality
    -   You can choose to set .mp4 path or leave it black to get a file with the folder name, encoder and quality as name
-   Open render folder - Quick access to the rendered files

<br>
<br>
<hr />

## FFmpeg Install

[Windows Install](https://github.com/dshot92/blender_addons/blob/4fac9db4c59f75dda544a32dee6b2986f6d725e5/Render_Script/readme.md#L27)

[Linux Install](https://linuxize.com/post/how-to-install-ffmpeg-on-debian-9/)
