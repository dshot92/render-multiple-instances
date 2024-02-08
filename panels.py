# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy

from .utils import is_ffmpeg_installed


class RENDER_PT_RenderScriptInstances(bpy.types.Panel):

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_label = "Render Multiple Instances"
    bl_category = "Render Multiple Instances"

    def draw(self, context):
        props = context.scene.Render_Script_Props
        layout = self.layout
        layout.use_property_split = True

        # Frame Range Override panel
        header, panel = layout.panel("panel_frames", default_closed=True)
        header.label(text="Frame Range")

        if panel:

            panel.prop(props, "override_range", text="Override Frame Range")
            panel.active = props.override_range
            panel.prop(props, "start_frame")
            panel.prop(props, "end_frame")

        # Render Instances panel
        header, panel = layout.panel("panel_render", default_closed=False)
        header.label(text="Render Instances")

        if panel:
            panel.prop(props, "instances", text="Num Instances")
            panel.operator(
                'mesh.save_and_render',
                text="Save and Render",
                icon="RENDER_ANIMATION",
            )

        # Sequence to mp4 panel
        header, panel = layout.panel("panel_sequence", default_closed=False)
        header.label(text="Sequence to .mp4")

        if panel:
            if not is_ffmpeg_installed():
                panel.label(text="FFmpeg is NOT installed")
                panel.label(text="Check Addon README.md for more info.")
            else:
                panel.prop(props, "quality", text="Quality")
                panel.prop(props, 'encoder', text="Encoder")
                panel.prop(props, "mp4_file", text="Mp4 save path")

                panel.operator(
                    'mesh.ffmpeg_renders',
                    text="Create video from frames",
                    icon="SEQUENCE")

        # Open render foldore button
        layout.operator(
            'mesh.open_render_folder',
            text="Open render folder",
            icon="FILE_FOLDER")


classes = (
    RENDER_PT_RenderScriptInstances,
)

register, unregister = bpy.utils.register_classes_factory(classes)
