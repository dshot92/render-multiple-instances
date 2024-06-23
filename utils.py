# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy
import os
import re
import platform
import glob
import subprocess
from pathlib import Path
from enum import Enum


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


def set_render_path(path_type):
    """
    Set the render path based on the given path type, and automatically increment if the number already exists.

    :param path_type: 'render' or 'viewport'
    :return: The formatted render path
    """

    base_path = "//flipbooks/"

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

    return new_path


def get_render_command_list(context: bpy.types.Context) -> list:

    props = bpy.context.scene.Render_Script_Props

    blender_bin_path = get_blender_bin_path()
    blend_file_path = get_blend_file()

    start_frame = context.scene.frame_start
    end_frame = context.scene.frame_end

    # Override if start_frame > end_frame and are > 0
    if props.start_frame > props.end_frame:
        start_frame = props.start_frame
        end_frame = props.end_frame

    cmd = [f'{blender_bin_path}', "-b", f'{blend_file_path}',
           "-s", f"{start_frame}", "-e", f"{end_frame}", "-a"]

    return get_platform_terminal_command_list(cmd)


def get_mp4_output_path() -> Path:

    props = bpy.context.scene.Render_Script_Props

    encoder = props.encoder
    quality = props.quality

    export_parent_dir = get_export_parent_dir()
    export_dir = get_export_dir()

    mp4_path = export_parent_dir / \
        f"{export_dir.name}_{encoder}_{quality}.mp4"
    return mp4_path


def get_frame_list_path() -> Path:

    duration = 1 / bpy.context.scene.render.fps

    export_dir = get_export_dir()

    frame_list_file = Path(export_dir, "ffmpeg_frame_list.txt")

    files = [file for ext in ['*.png', '*.jpg', '*.jpeg']
             for file in glob.glob(os.path.join(export_dir, ext))]

    files.sort()

    try:
        with open(frame_list_file, "w") as frame_list:
            for file in files:
                frame_list.write(f"file '{file}'\n")
                frame_list.write(f"duration {duration}\n")
    except FileNotFoundError:
        print("Could not create frame list file")

    return frame_list_file


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


def get_ffmpeg_command_list() -> list:

    # https://stackoverflow.com/questions/31201164/ffmpeg-error-pattern-type-glob-was-selected-but-globbing-is-not-support-ed-by
    props = bpy.context.scene.Render_Script_Props

    encoder = props.encoder
    quality = props.quality
    fps = bpy.context.scene.render.fps

    frame_list_file = get_frame_list_path()
    output_file = get_mp4_output_path()

    cmd = []
    # https://ntown.at/de/knowledgebase/cuda-gpu-accelerated-h264-h265-hevc-video-encoding-with-ffmpeg/
    match encoder:
        case "libx264":
            # ffmpeg_command = f'ffmpeg -safe 0 -r {fps} -f concat
            # -i "{frame_list_file}" -pix_fmt yuv420p -c:v {encoder}
            # -crf {quality} -tune fastdecode "{output_file}" -y'
            cmd = ["ffmpeg", "-safe", "0", "-r", f"{fps}", "-f",
                   "concat", "-i", f'"{frame_list_file}"',
                   "-pix_fmt", "yuv420p", "-c:v",
                   f"{encoder}", "-crf", f"{quality}",
                   f'"{output_file}"', "-y"]
        case "libx265":
            # ffmpeg -i input.mov -pix_fmt yuv420p -c:v libx265
            # -crf 18 -tune fastdecode -g 1 output.mp4
            cmd = ["ffmpeg", "-safe", "0", "-r", f"{fps}", "-f",
                   "concat", "-i", f'"{frame_list_file}"', "-pix_fmt",
                   "yuv420p", "-c:v", f"{encoder}", "-crf",
                   f"{quality}", "-tune", "fastdecode", "-g", "1",
                   f'"{output_file}"', "-y"]
        case "libaom-av1":
            # ffmpeg -i input.mov -pix_fmt yuv420p -c:v libx265 -crf 18
            # -tune fastdecode -g 1 output.mp4
            cmd = ["ffmpeg", "-strict", "-2", "-safe", "0", "-r",
                   f"{fps}", "-f", "concat", "-i",
                   f'"{frame_list_file}"', "-c:v", f"{encoder}",
                   "-strict", "-2", "-crf", f"{quality}",
                   f'"{output_file}"', "-y"]

    return get_platform_terminal_command_list(cmd)


def open_folder(path) -> None:

    match OS.detect_os():
        case OS.WINDOWS:
            os.startfile(path)
        case OS.MACOS:
            subprocess.Popen(["open", path])
        case OS.LINUX:
            subprocess.Popen(["xdg-open", path])
