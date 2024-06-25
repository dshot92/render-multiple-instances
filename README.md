# Render Multiple Instances (RMI) Addon for Blender

The Render Multiple Instances (RMI) addon for Blender provides a convenient way to render animations faster by utilizing multiple instances in background. Here are the key features of the addon:

## Render Animation with Instances
- Renders the animation using the specified number of instances, reducing rendering time
- Uses the Blender scene's render output settings for the animation rendering
- Encode exported frames to MP4 video using FFmpeg (if PNG of JPG output is selected)

## Flipbook Viewport
- Renders a flipbook animation in the viewport
- Allows overriding the frame range and adjusting resolution percentage
- Automatically encodes the rendered frames into an MP4 video using FFmpeg
- Uses a custom incremental directory for the flipbook rendering based on the addon settings

## Flipbook Render
- Renders a flipbook animation using the specified number of instances
- Supports overriding the frame range and adjusting resolution percentage
- Automatically encodes the rendered frames into an MP4 video using FFmpeg
- Uses a custom incremental directory for the flipbook rendering based on the addon settings

## Open Render Directory
- Provides a button to quickly open the render directory

## Settings
- Allows setting the number of instances to use for rendering
- Provides options to select the encoder and adjust the quality
- Includes settings for the flipbook rendering, such as frame range override and resolution percentage

The addon is designed to work seamlessly with Blender 4.2 and later versions. It simplifies the process of rendering animations by leveraging multiple instances, resulting in faster rendering times. The flipbook features enable quick previews of animations, while the FFmpeg encoding ensures the final output is ready to use.

Even when using just a single instance, the RMI addon can improve rendering speed by rendering the animation in the background, allowing you to continue working in Blender while the rendering is in progress.

The Render Multiple Instances (RMI) panel is located in
```Output Properties > Render Multiple Instances```

## Requirement for FFmpeg encoding
Note that the FFmpeg encoding features of the addon require FFmpeg to be installed on the machine for them to function properly.
