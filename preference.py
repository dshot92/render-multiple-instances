# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy


def getPreferences(context=None):
    if context is None:
        context = bpy.context
    preferences = context.preferences
    addon_preferences = preferences.addons[__package__].preferences
    return addon_preferences


class RMI_Preferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__


    debug_prints: bpy.props.BoolProperty(
        name="Debug Prints",
        description="Enable debug prints",
        default=False
    )

    def draw(self, context):
        layout = self.layout

        # box = layout.box() 
        header, panel = layout.panel("panel_debug", default_closed=False)
        header.label(text="Debugging", icon="SETTINGS")
        if panel:
            # col = panel.column(align=True)
            panel.prop(self, "debug_prints")


classes = (RMI_Preferences,)

register, unregister = bpy.utils.register_classes_factory(classes)