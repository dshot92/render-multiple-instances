# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import os
import bpy
import glob
import subprocess

from .utils import (
    OperatingSystem,
    get_blender_bin_path,
    get_export_dir,
    get_blend_file,
    get_export_parent_dir,
    get_platform_terminal_command_list,
    open_folder,
)


class MESH_OT_Save_and_Render(bpy.types.Operator):
    """
    Create render script
    """

    bl_idname = "mesh.save_and_render"
    bl_label = "Save and Render"
    bl_description = "Save blend file and start Renders"

    def get_render_command_list(self, context):

        props = bpy.context.scene.Render_Script_Props

        blender_bin_path = get_blender_bin_path()

        blend_file_path = get_blend_file()

        start_frame = context.scene.frame_start
        end_frame = context.scene.frame_end

        # override_range = props.override_range

        # Override if start_frame > end_frame and are > 0
        if props.start_frame > props.end_frame:
            start_frame = props.start_frame
            end_frame = props.end_frame

        cmd = []

        match OperatingSystem.detect_os():
            case OperatingSystem.WINDOWS:
                cmd = [f'"{blender_bin_path}"', "-b",
                       f'"{blend_file_path}"', "-s", f"{start_frame}", "-e",
                       f"{end_frame}", "-a"]
            case OperatingSystem.MACOS:
                cmd = [f'{blender_bin_path}', "--args", "-b",
                       f'{blend_file_path}', "-s", f"{start_frame}", "-e",
                       f"{end_frame}", "-a"]
            case OperatingSystem.LINUX:
                cmd = [f'{blender_bin_path}', "-b",
                       f'{blend_file_path}', "-s", f"{start_frame}", "-e",
                       f"{end_frame}", "-a"]
            case OperatingSystem.UNKNOWN:
                self.report({'ERROR'}, "Unknown OS")

        return get_platform_terminal_command_list(cmd)

    def execute(self, context):

        file_ext = str(context.scene.render.image_settings.file_format).lower()

        if file_ext != "png" and file_ext != "jpg" and file_ext != "jpeg":
            self.report({'ERROR'},
                        "Export extension must be .png/.jpg")
            return {'CANCELLED'}

        props = bpy.context.scene.Render_Script_Props

        # Store scene render settings
        _use_overwrite = context.scene.render.use_overwrite
        _use_placeholder = context.scene.render.use_placeholder
        _resolution_percentage = context.scene.render.resolution_percentage

        context.scene.render.use_overwrite = False
        context.scene.render.use_placeholder = True
        context.scene.render.resolution_percentage = props.res_percentage

        # Save file to ensure last changes are saved
        try:
            if not bpy.data.is_saved:
                self.report(
                    {'WARNING'}, "Blend file has never been saved before. Please save the file first.")
                return {'CANCELLED'}
            bpy.ops.wm.save_mainfile()
        except RuntimeError as e:
            self.report({'ERROR'}, f"Failed to save blend file: {e}")
            return {'CANCELLED'}

        auto_render = props.auto_render
        instances = props.instances

        cmd = self.get_render_command_list(context)

        if auto_render:
            try:
                for _ in range(instances):
                    subprocess.Popen(cmd)
            except Exception as e:
                self.report(
                    {'ERROR'}, f"Failed to launch Blender instances: {e}")
                return {'CANCELLED'}

        # Restore scene render settings
        context.scene.render.use_overwrite = _use_overwrite
        context.scene.render.use_placeholder = _use_placeholder
        context.scene.render.resolution_percentage = _resolution_percentage

        self.report({'INFO'}, "Render script Created")
        return {'FINISHED'}


class MESH_OT_ffmpeg_renders(bpy.types.Operator):
    """
    Create render script
    """

    bl_idname = "mesh.ffmpeg_renders"
    bl_label = "Create video from frames"
    bl_description = "Create video from frames"

    def get_mp4_output_path(self):

        props = bpy.context.scene.Render_Script_Props

        encoder = props.encoder
        quality = props.quality

        mp4_path = bpy.context.scene.Render_Script_Props.mp4_file
        export_parent_dir = get_export_parent_dir()

        blend_file = get_blend_file()
        blend_file = os.path.splitext(blend_file)[0]

        if mp4_path == "":
            mp4_path = os.path.join(
                export_parent_dir,
                blend_file + f"_{encoder}_{quality}.mp4")

        return mp4_path

    def get_frame_list_path(self):

        duration = 1 / bpy.context.scene.render.fps

        export_dir = get_export_dir()
        # export_path = utils.get_export_path()
        frame_list_file = os.path.join(export_dir, "ffmpeg_input.txt")

        # Use list comprehension to get both .png and .jpg files
        files = [file for ext in ['*.png', '*.jpg']
                 for file in glob.glob(os.path.join(export_dir, ext))]

        files.sort()

        try:
            with open(frame_list_file, "w+") as outfile:
                for file in files:
                    outfile.write(f"file '{file}'\n")
                    outfile.write(f"duration {duration}\n")
            outfile.close()
        except FileNotFoundError as e:
            print('Error ', e)
            print(f"The {frame_list_file} does not exist")

        return frame_list_file

    def get_ffmpeg_command_list(self):

        # https://stackoverflow.com/questions/31201164/ffmpeg-error-pattern-type-glob-was-selected-but-globbing-is-not-support-ed-by
        props = bpy.context.scene.Render_Script_Props

        encoder = props.encoder
        quality = props.quality
        fps = bpy.context.scene.render.fps

        frame_list_file = self.get_frame_list_path()
        output_file = self.get_mp4_output_path()

        cmd = []
        # https://ntown.at/de/knowledgebase/cuda-gpu-accelerated-h264-h265-hevc-video-encoding-with-ffmpeg/
        match encoder:
            case "libx264":
                # ffmpeg_command = f'ffmpeg -safe 0 -r {fps} -f concat
                # -i "{frame_list_file}" -pix_fmt yuv420p -c:v {encoder}
                # -crf {quality} -tune fastdecode "{output_file}" -y'
                cmd = ["ffmpeg", "-safe", "0", "-r", f"{fps}", "-f",
                       "concat", "-i", f'"{frame_list_file}"',
                       "-pix_fmt", "yuv420p", "-c:v",
                       f"{encoder}", "-crf", f"{quality}",
                       f'"{output_file}"', "-y"]
            case "libx265":
                # ffmpeg -i input.mov -pix_fmt yuv420p -c:v libx265
                # -crf 18 -tune fastdecode -g 1 output.mp4
                cmd = ["ffmpeg", "-safe", "0", "-r", f"{fps}", "-f",
                       "concat", "-i", f'"{frame_list_file}"', "-pix_fmt",
                       "yuv420p", "-c:v", f"{encoder}", "-crf",
                       f"{quality}", "-tune", "fastdecode", "-g", "1",
                       f'"{output_file}"', "-y"]
            case "libaom-av1":
                # ffmpeg -i input.mov -pix_fmt yuv420p -c:v libx265 -crf 18
                # -tune fastdecode -g 1 output.mp4
                cmd = ["ffmpeg", "-strict", "-2", "-safe", "0", "-r",
                       f"{fps}", "-f", "concat", "-i",
                       f'"{frame_list_file}"', "-c:v", f"{encoder}",
                       "-strict", "-2", "-crf", f"{quality}",
                       f'"{output_file}"', "-y"]

        return get_platform_terminal_command_list(cmd)

    def execute(self, context):

        if not os.path.isdir(get_export_dir()):
            self.report({'ERROR'}, "Render folder not found")
            return {'CANCELLED'}

        cmd = self.get_ffmpeg_command_list()

        os.system(' '.join(cmd))

        self.report({'INFO'}, "Video .mp4 encoded")
        return {'FINISHED'}


class MESH_OT_open_render_folder(bpy.types.Operator):
    """
    Create render script
    """

    bl_idname = "mesh.open_render_folder"
    bl_label = "Open render folder"
    bl_description = "Open render folder"

    def execute(self, context):

        path = get_export_dir()

        if not os.path.isdir(path):
            self.report({'ERROR'}, "Render folder not found")
            return {'CANCELLED'}

        open_folder(path)

        return {'FINISHED'}


classes = (MESH_OT_Save_and_Render,
           MESH_OT_ffmpeg_renders,
           MESH_OT_open_render_folder,)

register, unregister = bpy.utils.register_classes_factory(classes)
