# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import os
import bpy
import subprocess

from .utils import (
    open_folder,
    start_process,
    get_blend_file,
    get_export_dir,
    set_render_path,
    ffmpeg_installed,
    get_render_command_list,
    get_ffmpeg_command_list,
)


class RENDER_OT_Save_blend_file(bpy.types.Operator):
    bl_idname = "rmi.save_blend_file"
    bl_label = "Save Blend File"
    bl_description = "Save Blend File"

    def execute(self, context):
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

        return {'FINISHED'}


class RENDER_OT_Render(bpy.types.Operator):
    bl_idname = "rmi.render_animation"
    bl_label = "Render Animation with Instances"
    bl_description = "Render Animation with Instances"

    @classmethod
    def poll(cls, context):
        saved = bpy.context.blend_data.is_saved
        if not saved:
            cls.poll_message_set(
                "Blend file is not saved. Please save the file first.")
        return saved

    def execute(self, context):
        instances = bpy.context.scene.RMI_Props.instances

        cmd = get_render_command_list(context)

        bpy.ops.rmi.save_blend_file()

        for _ in range(instances):
            subprocess.Popen(cmd)

        self.report({'INFO'}, "Render Created")
        return {'FINISHED'}


class RENDER_OT_Flipbook_Viewport(bpy.types.Operator):
    bl_idname = "rmi.flipbook_viewport"
    bl_label = "Flipbook Viewport"
    bl_description = "Flipbook Viewport"

    @classmethod
    def poll(cls, context):
        saved = bpy.context.blend_data.is_saved
        if not saved:
            cls.poll_message_set(
                "Blend file is not saved. Please save the file first.")
        return saved

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

            bpy.ops.rmi.save_blend_file()

            bpy.ops.render.opengl(animation=True)

        except RuntimeError as e:
            self.report({'ERROR'}, f"Failed to save blend file: {e}")
            return {'CANCELLED'}

        finally:
            # Encode flipbook
            if ffmpeg_installed:
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

            bpy.ops.rmi.save_blend_file()

        self.report({'INFO'}, "Flipbook Viewport Created")
        return {'FINISHED'}


class RENDER_OT_Flipbook_Render(bpy.types.Operator):
    bl_idname = "rmi.flipbook_render"
    bl_label = "Flipbook Render"
    bl_description = "Flipbook Render"

    @classmethod
    def poll(cls, context):
        saved = bpy.context.blend_data.is_saved
        if not saved:
            cls.poll_message_set(
                "Blend file is not saved. Please save the file first.")
        return saved

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

            # auto_render = props.auto_render
            instances = props.instances

            cmd = get_render_command_list(context)

            bpy.ops.rmi.save_blend_file()

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
            if ffmpeg_installed:
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

            bpy.ops.rmi.save_blend_file()

        self.report({'INFO'}, "Flipbook Render Created")
        return {'FINISHED'}


class RENDER_OT_ffmpeg_encode(bpy.types.Operator):
    bl_idname = "rmi.ffmpeg_encode"
    bl_label = "Encode rendered frames into video"
    bl_description = "Encode rendered frames into video"

    @classmethod
    def poll(cls, context):
        export_dir = get_export_dir()
        if not export_dir.is_dir():
            cls.poll_message_set(
                f"Export Directory not found:\n{export_dir}")
            return False

        file_ext = str(context.scene.render.image_settings.file_format).lower()
        allowed_ext = file_ext in ('png', 'jpg', 'jpeg')
        if not allowed_ext:
            cls.poll_message_set(
                f"Unsupported file format: {file_ext}")
            return False

        if not ffmpeg_installed:
            cls.poll_message_set(
                "FFmpeg is not installed. Please install FFmpeg first.")
            return False

        saved = bpy.context.blend_data.is_saved
        if not saved:
            cls.poll_message_set(
                "Blend file is not saved. Please save the file first.")
            return False

        return True

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

    @classmethod
    def poll(cls, context):
        saved = bpy.context.blend_data.is_saved
        if not saved:
            cls.poll_message_set(
                "Blend file is not saved. Please save the file first.")
        return saved

    def execute(self, context):

        path = get_blend_file().parent

        if not os.path.isdir(path):
            self.report({'ERROR'}, "Render Directory not found")
            return {'CANCELLED'}

        open_folder(path)

        return {'FINISHED'}


classes = (
    RENDER_OT_Save_blend_file,
    RENDER_OT_Render,
    RENDER_OT_Flipbook_Viewport,
    RENDER_OT_Flipbook_Render,
    RENDER_OT_ffmpeg_encode,
    UI_OT_open_render_dir,
)

register, unregister = bpy.utils.register_classes_factory(classes)
