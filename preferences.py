# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy

addon_idname = __package__


def getPreferences(context=None):
    if context is None:
        context = bpy.context
    preferences = context.preferences
    addon_preferences = preferences.addons[addon_idname].preferences
    return addon_preferences


class CreateRenderScriptPreferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = addon_idname

    debug: bpy.props.BoolProperty(
        name="Debug",
        default=False,
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Enable Console Debug Print")
        box.prop(self, "debug")

    terminal_emulator: bpy.props.EnumProperty(
        name="terminal_emulator",
        description="Select Terminal",
        items=[
            ("konsole -e", "Konsole", ""),
            ("gnome-terminal --", "Gnome-terminal", "")]
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Terminal Emulator")
        box.prop(self, "terminal_emulator")


classes = (CreateRenderScriptPreferences,)

register, unregister = bpy.utils.register_classes_factory(classes)
