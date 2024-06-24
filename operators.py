# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import os
import bpy
import subprocess

from .utils import (
    ffmpeg_installed,
    get_export_dir,
    get_blend_file,
    set_render_path,
    get_render_command_list,
    get_ffmpeg_command_list,
    open_folder,
)


class RENDER_OT_Render(bpy.types.Operator):
    bl_idname = "rmi.render_animation"
    bl_label = "Render Animation with Instances"
    bl_description = "Render Animation with Instances"

    def execute(self, context):

        file_ext = str(context.scene.render.image_settings.file_format).lower()

        if file_ext != "png" and file_ext != "jpg" and file_ext != "jpeg":
            self.report({'ERROR'},
                        "Export extension must be .png/.jpg")
            return {'CANCELLED'}

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

        instances = bpy.context.scene.RMI_Props.instances

        cmd = get_render_command_list(context)

        for _ in range(instances):
            subprocess.Popen(cmd)

        self.report({'INFO'}, "Render Created")
        return {'FINISHED'}


class RENDER_OT_Flipbook_Viewport(bpy.types.Operator):
    bl_idname = "rmi.flipbook_viewport"
    bl_label = "Flipbook Viewport"
    bl_description = "Flipbook Viewport"

    def execute(self, context):

        try:
            props = bpy.context.scene.RMI_Props

            # Store scene render settings
            _use_stamp = context.scene.render.use_stamp
            _use_overwrite = context.scene.render.use_overwrite
            _use_placeholder = context.scene.render.use_placeholder
            _resolution_percentage = context.scene.render.resolution_percentage
            _export_dir = context.scene.render.filepath
            _file_ext = context.scene.render.image_settings.file_format
            _start_frame = bpy.context.scene.frame_start
            _end_frame = bpy.context.scene.frame_end

            context.scene.render.use_stamp = True
            context.scene.render.use_overwrite = False
            context.scene.render.use_placeholder = True
            context.scene.render.resolution_percentage = props.res_percentage
            context.scene.render.filepath = set_render_path('viewport')
            context.scene.render.image_settings.file_format = 'JPEG'
            context.scene.render.image_settings.file_format = 'JPEG'
            if props.override_range:
                start_frame = props.start_frame
                end_frame = props.end_frame
                bpy.context.scene.frame_start = start_frame
                bpy.context.scene.frame_end = end_frame

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

        except RuntimeError as e:
            self.report({'ERROR'}, f"Failed to save blend file: {e}")
            return {'CANCELLED'}

        finally:
            # Encode flipbook
            bpy.ops.rmi.ffmpeg_encode()

            # Restore scene render settings
            context.scene.render.use_stamp = _use_stamp
            context.scene.render.use_overwrite = _use_overwrite
            context.scene.render.use_placeholder = _use_placeholder
            context.scene.render.resolution_percentage = _resolution_percentage
            context.scene.render.filepath = _export_dir
            context.scene.render.image_settings.file_format = _file_ext
            if props.override_range:
                bpy.context.scene.frame_start = _start_frame
                bpy.context.scene.frame_end = _end_frame

        self.report({'INFO'}, "Flipbook Viewport Created")
        return {'FINISHED'}


class RENDER_OT_Flipbook_Render(bpy.types.Operator):
    bl_idname = "rmi.flipbook_render"
    bl_label = "Flipbook Render"
    bl_description = "Flipbook Render"

    def execute(self, context):

        try:
            props = bpy.context.scene.RMI_Props

            # Store scene render settings
            _use_overwrite = context.scene.render.use_overwrite
            _use_placeholder = context.scene.render.use_placeholder
            _resolution_percentage = context.scene.render.resolution_percentage
            _export_dir = context.scene.render.filepath
            _file_ext = context.scene.render.image_settings.file_format
            _start_frame = bpy.context.scene.frame_start
            _end_frame = bpy.context.scene.frame_end

            context.scene.render.use_overwrite = False
            context.scene.render.use_placeholder = True
            context.scene.render.resolution_percentage = props.res_percentage
            context.scene.render.filepath = set_render_path('render')
            context.scene.render.image_settings.file_format = 'JPEG'
            if props.override_range:
                start_frame = props.start_frame
                end_frame = props.end_frame
                bpy.context.scene.frame_start = start_frame
                bpy.context.scene.frame_end = end_frame

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

            cmd = get_render_command_list(context)

            # List to store all subprocess objects
            # TODO: On windows, shell=True is necessary to show the terminal
            # on linux it will not correctly work it it is on True
            # This works okay, but could be better

            processes = []
            for _ in range(instances):
                p = start_process(cmd)
                processes.append(p)

            for p in processes:
                p.communicate()
                p.wait()

        except RuntimeError as e:
            self.report({'ERROR'}, f"Failed to Encode flipbook: {e}")
            return {'CANCELLED'}

        finally:
            # Encode flipbook
            bpy.ops.rmi.ffmpeg_encode()

            # Restore scene render settings
            context.scene.render.use_overwrite = _use_overwrite
            context.scene.render.use_placeholder = _use_placeholder
            context.scene.render.resolution_percentage = _resolution_percentage
            context.scene.render.filepath = _export_dir
            context.scene.render.image_settings.file_format = _file_ext
            if props.override_range:
                bpy.context.scene.frame_start = _start_frame
                bpy.context.scene.frame_end = _end_frame

        self.report({'INFO'}, "Flipbook Render Created")
        return {'FINISHED'}


class RENDER_OT_ffmpeg_encode(bpy.types.Operator):
    bl_idname = "rmi.ffmpeg_encode"
    bl_label = "Encode rendered frames into video"
    bl_description = "Encode rendered frames into video"

    @classmethod
    def poll(cls, context):
        export_dir_exist = os.path.isdir(get_export_dir())
        return ffmpeg_installed and export_dir_exist

    def execute(self, context):

        cmd = get_ffmpeg_command_list()

        os.system(' '.join(cmd))

        # TODO: this does not work on windows
        # os.remove(get_frame_list_path())

        self.report({'INFO'}, "Video .mp4 encoded")
        return {'FINISHED'}


class UI_OT_open_render_dir(bpy.types.Operator):
    bl_idname = "rmi.open_render_dir"
    bl_label = "Open Render Directory"
    bl_description = "Open Render Directory"

    def execute(self, context):

        path = get_blend_file().parent

        if not os.path.isdir(path):
            self.report({'ERROR'}, "Render Directory not found")
            return {'CANCELLED'}

        open_folder(path)

        return {'FINISHED'}


classes = (
    RENDER_OT_Render,
    RENDER_OT_Flipbook_Viewport,
    RENDER_OT_Flipbook_Render,
    RENDER_OT_ffmpeg_encode,
    UI_OT_open_render_dir,
)

register, unregister = bpy.utils.register_classes_factory(classes)
