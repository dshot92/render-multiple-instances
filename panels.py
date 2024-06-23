# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy

from .utils import is_ffmpeg_installed


class RENDER_PT_RenderScriptInstances_4_2(bpy.types.Panel):

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_label = "Render Multiple Instances"
    bl_category = "Render Multiple Instances"

    def draw(self, context):
        props = context.scene.Render_Script_Props
        layout = self.layout
        layout.use_property_split = True

        header, panel = layout.panel("panel_render", default_closed=False)
        header.label(text="Render")

        if panel:
            panel.operator(
                "rmi.render",
                text="Render",
                icon="RENDER_ANIMATION",
            )
            if not is_ffmpeg_installed():
                panel.label(text="FFmpeg is NOT installed")
                panel.label(text="Check Addon README.md for more info.")
            else:
                panel.operator(
                    "rmi.ffmpeg_encode",
                    text="FFmpeg Encode Render",
                    icon="SEQUENCE",
                )

        header, panel = layout.panel("panel_flipbook", default_closed=False)
        header.label(text="Flipbook")

        if panel:
            panel.operator(
                "rmi.flipbook_viewport",
                text="Flipbook Viewport",
                icon="RESTRICT_VIEW_OFF",
            )
            panel.operator(
                "rmi.flipbook_render",
                text="Flipbook Render",
                icon="RENDER_ANIMATION",
            )

        # Open render foldore button
        layout.operator(
            "rmi.open_render_dir",
            text="Open Directory",
            icon="FILE_FOLDER")
        # Frame Range Override panel
        header, panel = layout.panel("panel_frames", default_closed=True)
        header.label(text="Settings")

        if panel:
            panel.prop(props, "override_range", text="Flipbook Range")
            row = panel.row()
            row.active = props.override_range
            row.prop(props, "start_frame", text="Flip Start")
            row = panel.row()
            row.active = props.override_range
            row.prop(props, "end_frame", text="Flip End")
            panel.prop(props, "res_percentage", text="Resolution %")
            panel.prop(props, "instances", text="Instances")

            if not is_ffmpeg_installed():
                panel.label(text="FFmpeg is NOT installed")
                panel.label(text="Check Addon README.md for more info.")
            else:
                panel.prop(props, "encoder", text="Encoder")
                panel.prop(props, "quality", text="Quality")
                # panel.prop(props, "mp4_file", text="Mp4 save path")


classes = (
    RENDER_PT_RenderScriptInstances_4_2,
)


register, unregister = bpy.utils.register_classes_factory(classes)
