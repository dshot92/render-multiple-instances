# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

from . import (
    preferences,
    properties,
    operators,
    panels
)
import sys

# bl_info = {
#     "name": "Render Multiple Instances",
#     "version": (2, 6, 0),
#     "author": "DShot92 <dshot92@gmail.com>",
#     "blender": (2, 83, 20),
#     "category": "Render",
#     "location": "Output Properties > Render Multiple Instances",
#     "description": "Render animations faster with multiple instances.",
#     "warning": "",
#     "doc_url": "https://github.com/dshot92/blender_addons",
#     "tracker_url": "",
# }

if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preferences",
        "properties",
        "operators"
        "panels"
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])


def cleanse_modules():
    """search for your plugin modules in blender
    python sys.modules and remove them"""
    for module_name in sorted(sys.modules.keys()):
        if module_name.startswith(__name__):
            del sys.modules[module_name]


def register():
    preferences.register()
    properties.register()
    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()
    preferences.unregister()

    cleanse_modules()
