# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy

from .utils import (available_encoders)


class RMI_Props(bpy.types.PropertyGroup):
    # Render Script Property

    start_frame: bpy.props.IntProperty(
        name="start_frame",
        description="Start Frame Override",
        default=1,
        soft_min=1,
    )

    end_frame: bpy.props.IntProperty(
        name="end_frame",
        description="End Frame Override",
        default=250,
        soft_min=1,
    )

    instances: bpy.props.IntProperty(
        name="instances",
        description="Num Instances",
        default=3,
        min=1,
        soft_max=64,
    )

    override_range: bpy.props.BoolProperty(
        name="override_range",
        description="Override Frame Range",
        default=False
    )

    res_percentage: bpy.props.IntProperty(
        name="res_percentage",
        description="Render Resolution Percentage",
        default=50,
        soft_min=1,
        soft_max=100
    )

    quality: bpy.props.IntProperty(
        name="quality",
        description="Highest = 1, Lowest = 50",
        default=20,
        soft_min=1,
        soft_max=50
    )

    encoder: bpy.props.EnumProperty(
        name="encoder",
        description="Select Encoder",
        items=available_encoders,
    )

    use_stamp: bpy.props.BoolProperty(
        name="Use Stamp",
        description="Add stamp to rendered images",
        default=True
    )

    file_format: bpy.props.EnumProperty(
        name="File Format",
        description="Choose the file format for flipbook renders",
        items=[
            ('JPEG', "JPEG", "Save as JPEG format"),
            ('PNG', "PNG", "Save as PNG format"),
        ],
        default='PNG'
    )

    auto_encode: bpy.props.BoolProperty(
        name="Auto Encode",
        description="Automatically encode to video after rendering",
        default=True
    )

    flipbook_dir: bpy.props.StringProperty(
        name="Flipbook Directory",
        description="Directory to store flipbook renders",
        default="//flipbooks/",
        subtype='DIR_PATH'
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
