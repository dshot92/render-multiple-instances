# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy
import os
import platform
import subprocess

from .preferences import getPreferences
from .utils import (get_render_path, get_render_command,
                    get_frame_list, get_ffmpeg_command)


class MESH_OT_Save_and_Render(bpy.types.Operator):
    """
    Create render script
    """

    bl_idname = "mesh.save_and_render"
    bl_label = "Save and Render"
    bl_description = "Save blend file and start Renders"

    def execute(self, context):

        file_ext = str(context.scene.render.image_settings.file_format).lower()
        print(f"file_ext : {file_ext}")

        if file_ext not in "png":
            self.report(
                {'ERROR'}, "File sequence must be in .png format")
            return {'CANCELLED'}

        debug = getPreferences().debug
        props = bpy.context.scene.Render_Script_Props

        use_overwrite = context.scene.render.use_overwrite
        use_placeholder = context.scene.render.use_placeholder
        context.scene.render.use_overwrite = False
        context.scene.render.use_placeholder = True

        # Save file to ensure last changes are saved
        try:
            if not bpy.data.is_saved:
                self.report(
                    {'WARNING'}, "Blend file has never been saved before."
                    + "Please save the file first.")
                return {'CANCELLED'}
            bpy.ops.wm.save_mainfile()
        except RuntimeError as e:
            self.report({'ERROR'}, f"Failed to save blend file: {e}")
            return {'CANCELLED'}

        context.scene.render.use_overwrite = use_overwrite
        context.scene.render.use_placeholder = use_placeholder

        blender_path = bpy.app.binary_path  # Blender Executable Path
        blend_file_path = bpy.data.filepath  # Blender File Path

        start_frame = context.scene.frame_start
        end_frame = context.scene.frame_end
        override_range = props.override_range

        if override_range:
            start_frame = props.start_frame
            end_frame = props.end_frame

        auto_render = props.auto_render
        instances = props.instances

        if debug:
            print("\n\nDebug MESH_OT_Create_script_file\n")
            print(f"Blender path: {blender_path}")
            print(f"Blender File path: {blend_file_path}")

        command = get_render_command(
            blend_file_path,
            blender_path,
            start_frame,
            end_frame
        )

        if (auto_render):
            for _ in range(instances):
                os.system(command)

        context.scene.render.use_overwrite = use_overwrite
        context.scene.render.use_placeholder = use_placeholder

        self.report({'INFO'}, "Render script Created")
        return {'FINISHED'}


class MESH_OT_ffmpeg_renders(bpy.types.Operator):
    """
    Create render script
    """

    bl_idname = "mesh.ffmpeg_renders"
    bl_label = "Create video from frames"
    bl_description = "Create video from frames"

    def execute(self, context):

        debug = getPreferences().debug
        props = bpy.context.scene.Render_Script_Props

        # https://stackoverflow.com/questions/31201164/ffmpeg-error-pattern-type-glob-was-selected-but-globbing-is-not-support-ed-by

        parent_render_path, render_filename, render_folder = get_render_path()
        encoder = props.encoder
        quality = props.quality
        fps = bpy.context.scene.render.fps
        duration = 1 / bpy.context.scene.render.fps
        output_file_path = props.mp4_file

        if output_file_path == "":
            output_file_path = os.path.join(
                parent_render_path,
                render_filename + f"_{encoder}_{quality}.mp4")

        path_exists = os.path.isdir(render_folder)

        if not path_exists:
            self.report({'ERROR'}, "Render folder not found")
            return {'CANCELLED'}

        ffmpeg_command = get_ffmpeg_command(
            render_folder,
            duration,
            fps,
            encoder,
            quality,
            output_file_path
        )

        os.system(ffmpeg_command)

        if debug:
            print("\n\nDebug MESH_OT_ffmpeg_renders\n")
            print(f"Parent Render Path: {parent_render_path}")
            print(f"Render Filename: {render_filename}")
            print(f"Render Folder: {render_folder}")
            print(f"Output File: {output_file_path}")
            print(f"Encoder : {encoder}")
            print(f"Command: {ffmpeg_command}")

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

        path, _, _ = get_render_path()

        path_exists = os.path.isdir(path)

        if path_exists:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        else:
            self.report({'ERROR'}, "Render folder not found")

        return {'FINISHED'}


classes = (MESH_OT_Save_and_Render,
           MESH_OT_ffmpeg_renders,
           MESH_OT_open_render_folder,)

register, unregister = bpy.utils.register_classes_factory(classes)
