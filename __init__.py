# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

from . import (
    properties,
    operators,
    panels
)
import sys

# bl_info = {
#     "name": "Render Multiple Instances",
#     "version": (3, 0, 0),
#     "author": "DShot92 <dshot92@gmail.com>",
#     "blender": (4, 2, 0),
#     "category": "Render",
#     "location": "Output Properties > Render Multiple Instances",
#     "description": "Render animations faster with multiple instances.",
#     "warning": "",
#     "doc_url": "https://github.com/dshot92/render-multiple-instances",
#     "tracker_url": "",
# }

if "bpy" in locals():
    import importlib

    reloadable_modules = [
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
    properties.register()
    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()

    cleanse_modules()
