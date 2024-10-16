# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import importlib

from . import preference, properties, operators, panels

modules = [
    preference,
    properties,
    operators,
    panels,
]


if "bpy" in locals():
    importlib.reload(preference)
    importlib.reload(properties)
    importlib.reload(operators)
    importlib.reload(panels)


def register():
    for module in modules:
        importlib.reload(module)
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()