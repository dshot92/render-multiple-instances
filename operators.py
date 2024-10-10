# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy
import subprocess

from pathlib import Path

from .utils import (
    open_folder,
    get_blend_file,
    set_flipbook_render_output_path,
    is_ffmpeg_installed,
    get_ffmpeg_command_list,
    save_blend_file,
)


class RenderFlipbookOperatorBase:
    @classmethod
    def poll(cls, context):
        if not bpy.data.is_saved:
            cls.poll_message_set(
                "Blend file is not saved. Please save the file first.")
            return False
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

        # Store the output directory as an attribute of the operator
        self.output_dir = set_flipbook_render_output_path(context, render_type)
        context.scene.render.filepath = str(self.output_dir)

        context.scene.render.image_settings.file_format = props.file_format
        context.scene.render.use_stamp = props.use_stamp

        if props.override_range:
            context.scene.frame_start = props.start_frame
            context.scene.frame_end = props.end_frame

    def execute_render(self, context, render_func):
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
            self.restore_render_settings(context)
            save_blend_file()

        self.report({'INFO'},
                    f"Flipbook {self.render_type.capitalize()} Created in {self.output_dir}")
        return {'FINISHED'}


class RENDER_OT_Render(bpy.types.Operator):
    bl_idname = "rmi.render_animation"
    bl_label = "Render Animation with Instances"
    bl_description = "Render Animation with Instances"

    render_type = 'render'

    def execute(self, context):
        pass
        # def render_func():
        #     instances = context.scene.RMI_Props.instances
        #     cmd = get_render_command_list(context, is_flipbook=False)
        #
        #     for i in range(instances):
        #         return_code, stdout, stderr = run_command(cmd)
        #         if return_code != 0:
        #             self.report({'ERROR'},
        #                         f"Render process {i+1} failed. Error: {stderr}")
        #         else:
        #             print(f"Render process {i+1} completed successfully")
        #
        # return self.execute_render(context, render_func)


class RENDER_OT_Flipbook_Viewport(RenderFlipbookOperatorBase, bpy.types.Operator):
    bl_idname = "rmi.flipbook_viewport"
    bl_label = "Flipbook Viewport"
    bl_description = "Flipbook Viewport"

    render_type = 'flipbook_viewport'

    def execute(self, context):
        def render_func():

            bpy.ops.render.opengl(animation=True, write_still=True)

            if context.scene.RMI_Props.auto_encode_flipbook:
                bpy.ops.rmi.ffmpeg_encode()
            else:
                self.report(
                    {'INFO'},
                    "Auto encode is disabled. Flipbook images saved without video encoding.")

        return self.execute_render(context, render_func)


class RENDER_OT_Flipbook_Render(RenderFlipbookOperatorBase, bpy.types.Operator):
    bl_idname = "rmi.flipbook_render"
    bl_label = "Flipbook Render"
    bl_description = "Flipbook Render"

    render_type = 'flipbook_render'

    def execute(self, context):
        def render_func():
            bpy.ops.render.render(animation=True, write_still=True)
        return self.execute_render(context, render_func)


class RENDER_OT_ffmpeg_encode(bpy.types.Operator):
    bl_idname = "rmi.ffmpeg_encode"
    bl_label = "Encode rendered frames into video"
    bl_description = "Encode rendered frames into video"

    @classmethod
    def poll(cls, context):
        if not is_ffmpeg_installed():
            cls.poll_message_set(
                "FFmpeg is not installed. Please install FFmpeg first.")
            return False

        if not bpy.data.is_saved:
            cls.poll_message_set(
                "Blend file is not saved. Please save the file first.")
            return False

        return True

    def execute(self, context):
        try:
            output_dir = Path(context.scene.render.filepath)

            cmd = get_ffmpeg_command_list(context, output_dir)

            _ = subprocess.Popen(cmd, shell=True)

            return {'FINISHED'}
        except Exception as e:
            self.report(
                {'ERROR'}, f"An error occurred during encoding: {str(e)}")
            return {'CANCELLED'}


class UI_OT_open_render_dir(bpy.types.Operator):
    bl_idname = "rmi.open_render_dir"
    bl_label = "Open Render Directory"
    bl_description = "Open Render Directory"

    @classmethod
    def poll(cls, context):
        if not bpy.data.is_saved:
            cls.poll_message_set(
                "Blend file is not saved. Please save the file first.")
            return False
        return True

    def execute(self, context):
        path = get_blend_file().parent

        if not path.is_dir():
            self.report({'ERROR'}, "Render Directory not found")
            return {'CANCELLED'}

        open_folder(str(path))
        return {'FINISHED'}


classes = (
    RENDER_OT_Render,
    RENDER_OT_Flipbook_Viewport,
    RENDER_OT_Flipbook_Render,
    RENDER_OT_ffmpeg_encode,
    UI_OT_open_render_dir,
)

register, unregister = bpy.utils.register_classes_factory(classes)
