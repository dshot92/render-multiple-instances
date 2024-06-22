# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy
import os
import platform
import subprocess
from pathlib import Path
from enum import Enum


class OperatingSystem(Enum):
    WINDOWS = "Windows"
    MACOS = "MacOS"
    LINUX = "Linux"
    UNKNOWN = "Unknown"

    @staticmethod
    def detect_os():
        if os.name == 'nt':
            return OperatingSystem.WINDOWS
        elif os.name == 'posix' and platform.system() == "Darwin":
            return OperatingSystem.MACOS
        elif os.name == 'posix' and platform.system() == "Linux":
            return OperatingSystem.LINUX
        else:
            return OperatingSystem.UNKNOWN


# List of wanter encoders
enc = ["libx264", "libx265", "libaom-av1"]


def open_folder(path) -> None:

    match OperatingSystem.detect_os():
        case OperatingSystem.WINDOWS:
            os.startfile(path)
        case OperatingSystem.MACOS:
            subprocess.Popen(["open", path])
        case OperatingSystem.LINUX:
            subprocess.Popen(["xdg-open", path])


def is_ffmpeg_installed() -> bool:
    try:
        cmd = ["ffprobe", "-version"]
        _ = subprocess.check_output(cmd)
        return True
    except Exception as e:
        print("ERROR ", e)
        return False


def get_encoders() -> list:
    cmd = ["ffprobe", "-encoders"]
    encoders_list = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

    encoders = []
    for c in enc:
        if c in str(encoders_list):
            encoders.append(tuple((c, c, "")))

    return encoders


def get_blender_bin_path() -> Path:
    blender_bin_path = Path(bpy.app.binary_path)
    return blender_bin_path


def get_blend_file() -> Path:
    blend_file = Path(bpy.data.filepath)
    return blend_file


def get_export_dir() -> Path:
    filepath = bpy.path.abspath(bpy.context.scene.render.filepath)
    return Path(filepath).resolve()


def get_export_parent_dir() -> Path:
    export_path = get_export_dir()
    return export_path.parent


def get_platform_terminal_command_list(command_list: list) -> list:
    cmd = []
    match OperatingSystem.detect_os():
        case OperatingSystem.WINDOWS:
            # cmd = ["start", '""'] + command_list
            cmd = ["cmd.exe", "/c", "start"] + command_list
        case OperatingSystem.MACOS:
            cmd = ["open", "-a", "Terminal.app", "--args"] + command_list
        case OperatingSystem.LINUX:
            match os.environ.get('XDG_CURRENT_DESKTOP', ''):
                case 'GNOME':
                    cmd = ["gnome-terminal", "--"] + command_list
                case 'KDE':
                    cmd = ["konsole", "--hold", "-e"] + command_list
                case 'XFCE':
                    cmd = ["xfce4-terminal", "--command"] + command_list
                case _:
                    cmd = ["x-terminal-emulator", "-e"] + command_list
        case OperatingSystem.UNKNOWN:
            raise RuntimeError("Unsupported platform")

    return cmd
