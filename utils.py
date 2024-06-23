# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy
import os
import re
import platform
import subprocess
from pathlib import Path
from enum import Enum

last_path = None


class OS(Enum):
    WINDOWS = "Windows"
    MACOS = "MacOS"
    LINUX = "Linux"
    UNKNOWN = "Unknown"

    @staticmethod
    def detect_os():
        if os.name == 'nt':
            return OS.WINDOWS
        elif os.name == 'posix' and platform.system() == "Darwin":
            return OS.MACOS
        elif os.name == 'posix' and platform.system() == "Linux":
            return OS.LINUX
        else:
            return OS.UNKNOWN


# List of wanter encoders
enc = ["libx264", "libx265", "libaom-av1"]


def open_folder(path) -> None:

    match OS.detect_os():
        case OS.WINDOWS:
            os.startfile(path)
        case OS.MACOS:
            subprocess.Popen(["open", path])
        case OS.LINUX:
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


def set_render_path(path_type):
    """
    Set the render path based on the given path type, and automatically increment if the number already exists.

    :param path_type: 'render' or 'viewport'
    :return: The formatted render path
    """
    global last_path

    base_path = "//flipbook/"

    if path_type not in ['render', 'viewport']:
        raise ValueError("Invalid path_type. Choose 'render' or 'viewport'.")

    pattern = re.compile(rf"{path_type}_(\d{{3}})")
    max_number = -1

    # Find the maximum existing number for the given path_type
    base_path_abs = bpy.path.abspath(base_path)
    if os.path.exists(base_path_abs):
        for entry in os.listdir(base_path_abs):
            match = pattern.search(entry)
            if match:
                number = int(match.group(1))
                if number > max_number:
                    max_number = number

    # Start with the next number after the maximum found
    new_number = max_number + 1
    new_path = os.path.join(base_path, f"{path_type}_{new_number:03d}/")

    last_path = new_path
    print(f"Render path: {new_path}")
    print(f"Render number: {new_number}")

    return new_path


def get_export_dir() -> Path:
    filepath = bpy.path.abspath(bpy.context.scene.render.filepath)
    return Path(filepath).resolve()


def get_export_parent_dir() -> Path:
    export_path = get_export_dir()
    return export_path.parent


def get_platform_terminal_command_list(command_list: list) -> list:
    """
    - Windows: cmd.exe /c start
    - MacOS: open -a Terminal.app --args
    - Linux: x-terminal-emulator -e

    On Linux you can choose your default terminal with
    sudo update-alternatives --config x-terminal-emulator
    """
    cmd = []
    match OS.detect_os():
        case OS.WINDOWS:
            # cmd = ["start", '""'] + command_list
            cmd = ["cmd.exe", "/c", "start"] + command_list
        case OS.MACOS:
            cmd = ["open", "-a", "Terminal.app", "--args"] + command_list
        case OS.LINUX:
            cmd = ["x-terminal-emulator", "-e"] + command_list
            # match os.environ.get('XDG_CURRENT_DESKTOP', ''):
            # case 'GNOME':
            #     cmd = ["gnome-terminal", "--"] + command_list
            # case 'KDE':
            #     cmd = ["konsole", "--hold", "-e"] + command_list
            # case 'XFCE':
            #     cmd = ["xfce4-terminal", "--command"] + command_list
            # case _:
            #     cmd = ["x-terminal-emulator", "-e"] + command_list
        case OS.UNKNOWN:
            raise RuntimeError("Unsupported platform")

    return cmd
