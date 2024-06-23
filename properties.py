# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy


from .utils import (get_encoders, is_ffmpeg_installed)


class RMI_Props(bpy.types.PropertyGroup):
    # Render Script Property

    start_frame: bpy.props.IntProperty(
        name="start_frame",
        # description="Start Frame",
        default=1,
        soft_min=1,
    )

    end_frame: bpy.props.IntProperty(
        name="end_frame",
        # description="End Frame",
        default=250,
        soft_min=1,
    )

    instances: bpy.props.IntProperty(
        name="instances",
        # description="instances",
        default=3,
        min=1,
        soft_max=64,
    )

    override_range: bpy.props.BoolProperty(
        name="override_range",
        # description="override Frame Range",
        default=False
    )

    res_percentage: bpy.props.IntProperty(
        name="res_percentage",
        # description="Render Resolution Percentage",
        default=50,
        soft_min=1,
        soft_max=100
    )

    quality: bpy.props.IntProperty(
        name="quality",
        # description="Highest = 1, Lowest = 50",
        default=20,
        soft_min=1,
        soft_max=50
    )

    available_encoders = []
    if is_ffmpeg_installed():
        available_encoders = get_encoders()

    encoder: bpy.props.EnumProperty(
        name="encoder",
        # description="Select Encoder",
        items=available_encoders,
    )


classes = (RMI_Props,)


def register():
    for bl_class in classes:
        bpy.utils.register_class(bl_class)
    bpy.types.Scene.RMI_Props = bpy.props.PointerProperty(type=RMI_Props)


def unregister():
    for bl_class in reversed(classes):
        bpy.utils.unregister_class(bl_class)
    del bpy.types.Scene.RMI_Props
