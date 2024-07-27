# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

from . import (
    properties,
    operators,
    panels
)


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


def register():
    properties.register()
    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()
