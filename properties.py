# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy


from .utils import (get_encoders, is_ffmpeg_installed)


class Render_Script_Props(bpy.types.PropertyGroup):
    # Render Script Property

    start_frame: bpy.props.IntProperty(
        name="Start Frame",
        description="Start Frame",
        default=0,
    )

    end_frame: bpy.props.IntProperty(
        name="End Frame",
        description="End Frame",
        default=0,
    )

    instances: bpy.props.IntProperty(
        name="Instances",
        description="Instances",
        default=3,
        min=1,
        soft_max=64,
    )

    override_range: bpy.props.BoolProperty(
        name="Override Frame Range",
        description="Override Frame Range",
        default=False
    )

    auto_render: bpy.props.BoolProperty(
        name="Auto Render",
        description="Auto Render",
        default=True
    )

    res_percentage: bpy.props.IntProperty(
        name="Resolution Percentage",
        description="Render Resolution Percentage",
        default=100,
        soft_min=1,
        soft_max=100
    )

    quality: bpy.props.IntProperty(
        name="Quality",
        description="Highest = 1, Lowest = 50",
        default=20,
        soft_min=1,
        soft_max=50
    )

    available_encoders = []
    if is_ffmpeg_installed():
        available_encoders = get_encoders()

    encoder: bpy.props.EnumProperty(
        name="encoder",
        description="Select Encoder",
        items=available_encoders,
    )

    mp4_file: bpy.props.StringProperty(
        name="mp4_file",
        description="Select an output path. If left blank the file"
        + "will be created automatically in the export folder.",
        subtype='FILE_PATH', default=r"")


classes = (Render_Script_Props,)


def register():
    for bl_class in classes:
        bpy.utils.register_class(bl_class)
    bpy.types.Scene.Render_Script_Props = bpy.props.PointerProperty(
        type=Render_Script_Props)


def unregister():
    for bl_class in reversed(classes):
        bpy.utils.unregister_class(bl_class)
    del bpy.types.Scene.Render_Script_Props
