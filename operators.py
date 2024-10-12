# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy

from bpy.types import Operator

from .utils import (
    open_directory,
    get_blend_file,
    get_absolute_path,
    get_export_dir,
    flipbook_render_output_path,
    ffmpeg_installed,
    get_ffmpeg_command_list,
    save_blend_file,
    start_process,
    rendered_frames_exist,
    start_render_instances,
)


class RenderFlipbookOperatorBase:
    """
    Handle rendering
    Steps:
        1. Store scene settings
        2. Save file
        3. Update settings from properties
        4. Call render
        5. Restore settings
    """

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

    def update_render_settings(self, context, render_type):
        props = context.scene.RMI_Props

        # Flipbook only settings
        if 'flipbook' in render_type:
            context.scene.render.resolution_percentage = props.res_percentage

            self.output_dir = flipbook_render_output_path(context, render_type)
            context.scene.render.filepath = str(self.output_dir)

            context.scene.render.image_settings.file_format = props.file_format
            context.scene.render.use_stamp = props.use_stamp

        # Render and Flipbook shared settings
        context.scene.render.use_overwrite = False
        context.scene.render.use_placeholder = True
        if props.override_range:
            context.scene.frame_start = props.start_frame
            context.scene.frame_end = props.end_frame

    def execute_render(self, context, render_func):
        self.store_render_settings(context)

        try:
            self.update_render_settings(context, self.render_type)

            save_blend_file()

            render_func()

        except Exception as e:
            self.report({'ERROR'}, f"Failed to create flipbook: {str(e)}")
            return {'CANCELLED'}
        finally:
            if ffmpeg_installed and context.scene.RMI_Props.auto_encode and 'flipbook' in self.render_type:
                bpy.ops.rmi.ffmpeg_encode()
            else:
                self.report(
                    {'INFO'}, "FFmpeg not found. Encoding will be skipped.")

            self.restore_render_settings(context)
            save_blend_file()

        self.report({'INFO'}, f"{self.render_type} Created")

        return {'FINISHED'}


class RENDER_OT_Render(RenderFlipbookOperatorBase, Operator):
    bl_idname = "rmi.render_animation"
    bl_label = "Render Animation with Instances"
    bl_description = "Render Animation with Instances"

    render_type = 'render'

    @classmethod
    def poll(cls, context):
        if context.scene.render.filepath == "":
            cls.poll_message_set("Render directory not set.")
            return False

        if not bpy.context.blend_data.is_saved:
            cls.poll_message_set("Blend file is not saved.")
            return False

        return True

    def execute(self, context):

        def render_func():
            start_render_instances(context)

        return self.execute_render(context, render_func)


class RENDER_OT_Flipbook_Viewport(RenderFlipbookOperatorBase, Operator):
    bl_idname = "rmi.flipbook_viewport"
    bl_label = "Flipbook Viewport"
    bl_description = "Flipbook Viewport"

    render_type = 'flipbook_viewport'

    @classmethod
    def poll(cls, context):
        if context.scene.RMI_Props.flipbook_dir == "":
            cls.poll_message_set("Flipbooks directory not set.")
            return False

        if not bpy.context.blend_data.is_saved:
            cls.poll_message_set("Blend file is not saved.")
            return False

        return True

    def execute(self, context):
        def render_func():
            bpy.ops.render.opengl(animation=True, write_still=True)

        return self.execute_render(context, render_func)


class RENDER_OT_Flipbook_Render(RenderFlipbookOperatorBase, Operator):
    bl_idname = "rmi.flipbook_render"
    bl_label = "Flipbook Render"
    bl_description = "Flipbook Render"

    render_type = 'flipbook_render'

    @classmethod
    def poll(cls, context):
        if context.scene.RMI_Props.flipbook_dir == "":
            cls.poll_message_set("Flipbooks directory not set.")
            return False

        if not bpy.context.blend_data.is_saved:
            cls.poll_message_set("Blend file is not saved.")
            return False

        return True

    def execute(self, context):

        def render_func():
            start_render_instances(context)

        return self.execute_render(context, render_func)


class RENDER_OT_ffmpeg_encode(Operator):
    bl_idname = "rmi.ffmpeg_encode"
    bl_label = "Encode rendered frames into video"
    bl_description = "Encode rendered frames into video"

    @classmethod
    def poll(cls, context):
        export_dir = get_export_dir()
        if not export_dir.is_dir():
            export_dir = export_dir.parent
        if not rendered_frames_exist(export_dir):
            cls.poll_message_set("No frames in Export Directory.\n")
            return False

        if not ffmpeg_installed:
            cls.poll_message_set(
                "FFmpeg is not installed. Please install FFmpeg first.")
            return False

        if not bpy.context.blend_data.is_saved:
            cls.poll_message_set("Blend file is not saved.")
            return False

        return True

    def execute(self, context):
        try:
            out_dir = get_absolute_path(context.scene.render.filepath)

            cmd = get_ffmpeg_command_list(context, out_dir)

            _ = start_process(cmd)

            return {'FINISHED'}

        except Exception as e:
            self.report(
                {'ERROR'}, f"An error occurred during encoding: {str(e)}")
            return {'CANCELLED'}


class UI_OT_open_blend_file_dir(Operator):
    bl_idname = "rmi.open_blend_file_dir"
    bl_label = "Open Blend File Directory"
    bl_description = "Open Blend File Directory"

    @classmethod
    def poll(cls, context):
        if not bpy.data.is_saved:
            cls.poll_message_set(
                "Blend file is not saved. Please save the file first.")
            return False
        return True

    def execute(self, context):
        dir_path = get_blend_file().parent

        open_directory(dir_path)

        return {'FINISHED'}


classes = (
    RENDER_OT_Render,
    RENDER_OT_Flipbook_Viewport,
    RENDER_OT_Flipbook_Render,
    RENDER_OT_ffmpeg_encode,
    UI_OT_open_blend_file_dir,
)

register, unregister = bpy.utils.register_classes_factory(classes)
