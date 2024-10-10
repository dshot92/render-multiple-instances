# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy

from bpy.types import Operator

from .utils import (
    open_folder,
    get_blend_file,
    get_absolute_path,
    get_export_dir,
    get_render_command_list,
    set_flipbook_render_output_path,
    ffmpeg_installed,
    get_ffmpeg_command_list,
    save_blend_file,
    start_process,
)


class RENDER_OT_Render(Operator):
    bl_idname = "rmi.render_animation"
    bl_label = "Render Animation with Instances"
    bl_description = "Render Animation with Instances"

    def store_render_settings(self, context):
        self.original_settings = {
            'use_overwrite': context.scene.render.use_overwrite,
            'use_placeholder': context.scene.render.use_placeholder,
        }

    def restore_render_settings(self, context):
        for key, value in self.original_settings.items():
            if key == 'file_format':
                context.scene.render.image_settings.file_format = value
            elif hasattr(context.scene.render, key):
                setattr(context.scene.render, key, value)
            elif hasattr(context.scene, key):
                setattr(context.scene, key, value)

    def update_render_settings(self, context, props):
        context.scene.render.use_overwrite = False
        context.scene.render.use_placeholder = True

    def execute(self, context):
        props = context.scene.RMI_Props
        self.store_render_settings(context)

        try:
            self.update_render_settings(context, props)
            success = save_blend_file()
            if not success:
                self.report({'ERROR'}, ), "Blend file is not saved."
                return {'CANCELLED'}
            instances = props.instances

            cmd = get_render_command_list(context)

            processes = []
            for _ in range(instances):
                p = start_process(cmd)
                processes.append(p)
            for p in processes:
                p.wait()

        except Exception as e:
            self.report({'ERROR'}, f"Failed to create flipbook: {str(e)}")
            return {'CANCELLED'}
        finally:
            self.restore_render_settings(context)
            save_blend_file()

        self.report({'INFO'}, "Render Created")
        return {'FINISHED'}


class RenderFlipbookOperatorBase:
    """
    Handle rendering flipbooks
    Steps:
        1. Store scene settings
        2. Save file
        3. Update settings from properties
        4. Call render
        5. Restore settings
    """
    @classmethod
    def poll(cls, context):
        if not bpy.data.is_saved:
            cls.poll_message_set("Blend file is not saved.")
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
            success = save_blend_file()
            if not success:
                self.report({'ERROR'}, ), "Blend file is not saved."
                return {'CANCELLED'}

            render_func()

            if context.scene.RMI_Props.auto_encode_flipbook:
                bpy.ops.rmi.ffmpeg_encode()
            else:
                self.report(
                    {'INFO'},
                    "Auto encode is disabled. Flipbook images saved without video encoding.")

        except Exception as e:
            self.report({'ERROR'}, f"Failed to create flipbook: {str(e)}")
            return {'CANCELLED'}
        finally:
            self.restore_render_settings(context)
            save_blend_file()

        self.report(
            {'INFO'}, f"Flipbook {self.render_type.capitalize()} Created in {self.output_dir}")
        return {'FINISHED'}


class RENDER_OT_Flipbook_Viewport(RenderFlipbookOperatorBase, Operator):
    bl_idname = "rmi.flipbook_viewport"
    bl_label = "Flipbook Viewport"
    bl_description = "Flipbook Viewport"

    render_type = 'flipbook_viewport'

    def execute(self, context):
        def render_func():
            bpy.ops.render.opengl(animation=True, write_still=True)

        return self.execute_render(context, render_func)


class RENDER_OT_Flipbook_Render(RenderFlipbookOperatorBase, Operator):
    bl_idname = "rmi.flipbook_render"
    bl_label = "Flipbook Render"
    bl_description = "Flipbook Render"

    render_type = 'flipbook_render'

    def execute(self, context):
        def render_func():
            props = bpy.context.scene.RMI_Props
            out_dir = str(self.output_dir)
            context.scene.render.filepath = out_dir
            instances = props.instances

            cmd = get_render_command_list(context, out_dir)

            save_blend_file()

            processes = []
            for _ in range(instances):
                p = start_process(cmd)
                processes.append(p)
            for p in processes:
                p.wait()

        return self.execute_render(context, render_func)


class RENDER_OT_ffmpeg_encode(Operator):
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


class UI_OT_open_render_dir(Operator):
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
