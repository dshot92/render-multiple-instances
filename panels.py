# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy
from .utils import ffmpeg_installed

class RENDER_PT_RenderScriptInstances(bpy.types.Panel):

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_label = "Render Multiple Instances"
    bl_category = "Render Multiple Instances"

    def draw(self, context):
        props = context.scene.RMI_Props
        layout = self.layout
        layout.use_property_split = True

        # Normal Render Operations
        header, panel = layout.panel("panel_render", default_closed=False)
        header.label(text="Render Operations", icon="RENDER_ANIMATION")

        if panel:
            col = panel.column(align=True)
            col.operator("rmi.render_animation", text="Render Animation", icon="RENDER_ANIMATION")
            col.operator("rmi.ffmpeg_encode", text="FFmpeg Encode Render", icon="FILE_MOVIE")
            col.operator("rmi.open_render_dir", text="Open Render Directory", icon="FILE_FOLDER")

        # Flipbook Operations
        header, panel = layout.panel("panel_flipbook", default_closed=False)
        header.label(text="Flipbook Operations", icon="SEQUENCE")

        if panel:
            col = panel.column(align=True)
            col.operator("rmi.flipbook_viewport", text="Flipbook Viewport", icon="RESTRICT_VIEW_OFF")
            col.operator("rmi.flipbook_render", text="Flipbook Render", icon="RENDER_ANIMATION")

        # Render Settings
        header, panel = layout.panel("panel_render_settings", default_closed=False)
        header.label(text="Render Settings", icon="SETTINGS")
        # Flipbook Folder
        panel.prop(props, "flipbook_dir")

        if panel:
            col = panel.column(align=True)
            col.prop(props, "instances", text="Instances")
            col.prop(props, "res_percentage", text="Resolution %")
            col.prop(props, "file_format", text="File Format")
            col.prop(props, "use_stamp", text="Use Stamp")

        # Frame Range Settings
        header, panel = layout.panel("panel_frame_range", default_closed=False)
        header.label(text="Frame Range", icon="TIME")

        if panel:
            col = panel.column(align=True)
            col.prop(props, "override_range", text="Override Scene Range")
            sub = col.column(align=True)
            sub.active = props.override_range
            sub.prop(props, "start_frame", text="Start Frame")
            sub.prop(props, "end_frame", text="End Frame")

        # Encoding Settings
        header, panel = layout.panel("panel_encoding", default_closed=False)
        header.label(text="Encoding Settings", icon="MODIFIER")

        if panel:
            col = panel.column(align=True)
            col.prop(props, "auto_encode_flipbook", text="Auto Encode Flipbook")
            col.prop(props, "encoder", text="Encoder")
            col.prop(props, "quality", text="Quality")


classes = (
    RENDER_PT_RenderScriptInstances,
)

register, unregister = bpy.utils.register_classes_factory(classes)
