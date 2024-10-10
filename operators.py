# SPDX-License-Identifier: GPL-3.0-or-later

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
    save_blend_file,  # Add this import
)


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

        success, message = save_blend_file()
        if not success:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

        for _ in range(instances):
            subprocess.Popen(cmd)

        self.report({'INFO'}, "Render Created")
        return {'FINISHED'}


class FlipbookOperatorBase:
    @classmethod
    def poll(cls, context):
        if not bpy.data.is_saved:
            cls.poll_message_set("Blend file is not saved. Please save the file first.")
            return False
        if not ffmpeg_installed:
            cls.poll_message_set("FFmpeg is not installed. Flipbook will be created, but video encoding will be skipped.")
        return True

    def store_render_settings(self, context):
        self.original_settings = {
            'use_stamp': context.scene.render.use_stamp,
            'use_overwrite': context.scene.render.use_overwrite,
            'use_placeholder': context.scene.render.use_placeholder,
            'resolution_percentage': context.scene.render.resolution_percentage,
            'filepath': context.scene.render.filepath,
            'file_format': context.scene.render.image_settings.file_format,
            'frame_start': context.scene.frame_start,
            'frame_end': context.scene.frame_end,
        }

    def restore_render_settings(self, context):
        for key, value in self.original_settings.items():
            if key == 'file_format':
                context.scene.render.image_settings.file_format = value
            elif hasattr(context.scene.render, key):
                setattr(context.scene.render, key, value)
            elif hasattr(context.scene, key):
                setattr(context.scene, key, value)

    def update_render_settings(self, context, props, render_type):
        context.scene.render.use_overwrite = False
        context.scene.render.use_placeholder = True
        context.scene.render.resolution_percentage = props.res_percentage
        context.scene.render.filepath = set_render_path(render_type)
        context.scene.render.image_settings.file_format = props.file_format
        context.scene.render.use_stamp = props.use_stamp
        
        if props.override_range:
            context.scene.frame_start = props.start_frame
            context.scene.frame_end = props.end_frame

    def execute_common(self, context, render_func):
        props = context.scene.RMI_Props
        self.store_render_settings(context)

        try:
            self.update_render_settings(context, props, self.render_type)
            success, message = save_blend_file()
            if not success:
                self.report({'ERROR'}, message)
                return {'CANCELLED'}
            render_func()
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create flipbook: {str(e)}")
            return {'CANCELLED'}
        finally:
            if ffmpeg_installed and props.auto_encode_flipbook:
                bpy.ops.rmi.ffmpeg_encode()
            elif not ffmpeg_installed:
                self.report({'WARNING'}, "FFmpeg is not installed. Video encoding was skipped.")
            elif not props.auto_encode_flipbook:
                self.report({'INFO'}, "Auto encode is disabled. Flipbook images saved without video encoding.")
            self.restore_render_settings(context)
            save_blend_file()

        self.report({'INFO'}, f"Flipbook {self.render_type.capitalize()} Created")
        return {'FINISHED'}


class RENDER_OT_Flipbook_Viewport(FlipbookOperatorBase, bpy.types.Operator):
    bl_idname = "rmi.flipbook_viewport"
    bl_label = "Flipbook Viewport"
    bl_description = "Flipbook Viewport"

    render_type = 'viewport'

    def execute(self, context):
        def render_func():
            bpy.ops.render.opengl(animation=True)

        return self.execute_common(context, render_func)


class RENDER_OT_Flipbook_Render(FlipbookOperatorBase, bpy.types.Operator):
    bl_idname = "rmi.flipbook_render"
    bl_label = "Flipbook Render"
    bl_description = "Flipbook Render"

    render_type = 'render'

    def execute(self, context):
        def render_func():
            props = context.scene.RMI_Props
            instances = props.instances
            cmd = get_render_command_list(context)

            processes = [start_process(cmd) for _ in range(instances)]
            for p in processes:
                p.communicate()
                p.wait()

        return self.execute_common(context, render_func)


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
    RENDER_OT_Render,
    RENDER_OT_Flipbook_Viewport,
    RENDER_OT_Flipbook_Render,
    RENDER_OT_ffmpeg_encode,
    UI_OT_open_render_dir,
)

register, unregister = bpy.utils.register_classes_factory(classes)
