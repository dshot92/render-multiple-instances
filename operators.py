# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import os
import bpy
import glob
import subprocess
from pathlib import Path

from .utils import (
    get_blender_bin_path,
    get_export_dir,
    get_blend_file,
    get_export_parent_dir,
    get_platform_terminal_command_list,
    open_folder,
)


class RENDER_OT_Flipbook_Render(bpy.types.Operator):
    bl_idname = "rmi.flipbook_render"
    bl_label = "Flipbook Render"
    bl_description = "Flipbook Render"

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
        cmd = [f'{blender_bin_path}', "-b", f'{blend_file_path}',
               "-s", f"{start_frame}", "-e", f"{end_frame}", "-a"]

        # match OperatingSystem.detect_os():
        #     case OperatingSystem.WINDOWS:
        #         cmd = [f'{blender_bin_path}', "-b", f'{blend_file_path}',
        #                "-s", f"{start_frame}", "-e", f"{end_frame}", "-a"]
        #     case OperatingSystem.MACOS:
        #         cmd = [f'{blender_bin_path}', "-b", f'{blend_file_path}',
        #                "-s", f"{start_frame}", "-e", f"{end_frame}", "-a"]
        #     case OperatingSystem.LINUX:
        #         cmd = [f'{blender_bin_path}', "-b", f'{blend_file_path}',
        #                "-s", f"{start_frame}", "-e", f"{end_frame}", "-a"]
        #     case OperatingSystem.UNKNOWN:
        #         self.report({'ERROR'}, "Unknown OS")

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
                    {'WARNING'},
                    "Blend file has never been saved before."
                    + " Please save the file first.")
                return {'CANCELLED'}
            bpy.ops.wm.save_mainfile()
        except RuntimeError as e:
            self.report({'ERROR'}, f"Failed to save blend file: {e}")
            return {'CANCELLED'}

        # auto_render = props.auto_render
        instances = props.instances

        cmd = self.get_render_command_list(context)
        print(cmd)

        for _ in range(instances):
            subprocess.Popen(cmd)
            # match OperatingSystem.detect_os():
            #     case OperatingSystem.WINDOWS:
            #     case OperatingSystem.MACOS:
            #         subprocess.Popen(cmd)
            #     case OperatingSystem.LINUX:
            #         subprocess.Popen(cmd)

        # Restore scene render settings
        context.scene.render.use_overwrite = _use_overwrite
        context.scene.render.use_placeholder = _use_placeholder
        context.scene.render.resolution_percentage = _resolution_percentage

        self.report({'INFO'}, "Render script Created")
        return {'FINISHED'}


class RENDER_OT_Flipbook_Viewport(bpy.types.Operator):
    bl_idname = "rmi.flipbook_viewport"
    bl_label = "Flipbook Viewport"
    bl_description = "Flipbook Viewport"

    def execute(self, context):

        props = bpy.context.scene.Render_Script_Props

        print("viewport")

        # Store scene render settings
        _use_stamp = context.scene.render.use_stamp
        _use_overwrite = context.scene.render.use_overwrite
        _use_placeholder = context.scene.render.use_placeholder
        _resolution_percentage = context.scene.render.resolution_percentage

        context.scene.render.use_stamp = True
        context.scene.render.use_overwrite = False
        context.scene.render.use_placeholder = True
        context.scene.render.resolution_percentage = props.res_percentage

        # Save file to ensure last changes are saved
        try:
            if not bpy.data.is_saved:
                self.report(
                    {'WARNING'},
                    "Blend file has never been saved before."
                    + " Please save the file first.")
                return {'CANCELLED'}
            bpy.ops.wm.save_mainfile()
        except RuntimeError as e:
            self.report({'ERROR'}, f"Failed to save blend file: {e}")
            return {'CANCELLED'}

        bpy.ops.render.opengl(animation=True)

        # Restore scene render settings
        context.scene.render.use_stamp = _use_stamp
        context.scene.render.use_overwrite = _use_overwrite
        context.scene.render.use_placeholder = _use_placeholder
        context.scene.render.resolution_percentage = _resolution_percentage

        return {'FINISHED'}


class RENDER_OT_ffmpeg_encode(bpy.types.Operator):
    bl_idname = "rmi.ffmpeg_encode"
    bl_label = "Encode rendered frames into video"
    bl_description = "Encode rendered frames into video"

    def get_mp4_output_path(self) -> Path:

        props = bpy.context.scene.Render_Script_Props

        encoder = props.encoder
        quality = props.quality

        export_parent_dir = get_export_parent_dir()
        export_dir = get_export_dir()

        mp4_path = export_parent_dir / \
            f"{export_dir.name}_{encoder}_{quality}.mp4"

        return mp4_path

    def get_frame_list_path(self) -> Path:

        duration = 1 / bpy.context.scene.render.fps

        export_dir = get_export_dir()

        frame_list_file = Path(export_dir, "ffmpeg_input.txt")

        files = [file for ext in ['*.png', '*.jpg', '*.jpeg']
                 for file in glob.glob(os.path.join(export_dir, ext))]

        files.sort()

        try:
            with open(frame_list_file, "w") as frame_list:
                for file in files:
                    frame_list.write(f"file '{file}'\n")
                    frame_list.write(f"duration {duration}\n")
        except FileNotFoundError as e:
            print('Error ', e)
            print(f"The {frame_list_file} does not exist")

        return frame_list_file

    def get_ffmpeg_command_list(self) -> list:

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


class UI_OT_open_render_dir(bpy.types.Operator):
    bl_idname = "rmi.open_render_dir"
    bl_label = "Open Render Directory"
    bl_description = "Open Render Directory"

    def execute(self, context):

        path = get_export_parent_dir()

        if not os.path.isdir(path):
            self.report({'ERROR'}, "Render Directory not found")
            return {'CANCELLED'}

        open_folder(path)

        return {'FINISHED'}


classes = (
    RENDER_OT_Flipbook_Render,
    RENDER_OT_Flipbook_Viewport,
    RENDER_OT_ffmpeg_encode,
    UI_OT_open_render_dir,
)

register, unregister = bpy.utils.register_classes_factory(classes)
