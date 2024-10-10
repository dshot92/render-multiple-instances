# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import shlex
import bpy
import os
import re
import platform
import subprocess
from pathlib import Path
from enum import Enum
import shutil
from typing import Tuple


class OS(Enum):
    WINDOWS = "Windows"
    MACOS = "MacOS"
    LINUX = "Linux"
    UNKNOWN = "Unknown"

    @staticmethod
    def detect_os():
        system = platform.system()
        if system == "Windows":
            return OS.WINDOWS
        elif system == "Darwin":
            return OS.MACOS
        elif system == "Linux":
            return OS.LINUX
        else:
            return OS.UNKNOWN


def is_ffmpeg_installed() -> bool:
    return shutil.which('ffmpeg') is not None


def get_absolute_path(path: str) -> Path:
    return (Path(bpy.path.abspath(path))).resolve()


def set_flipbook_render_output_path(context, render_type: str) -> str:
    props = context.scene.RMI_Props
    base_path = str(get_absolute_path(props.flipbook_dir))

    pattern = re.compile(rf"{render_type}_v(\d{{3}})")
    max_number = -1

    # Find the maximum existing number
    base_path_abs = bpy.path.abspath(base_path)
    if os.path.exists(base_path_abs):
        for entry in os.listdir(base_path_abs):
            match = pattern.search(entry)
            if match:
                number = int(match.group(1))
                if number > max_number:
                    max_number = number

    new_number = max_number + 1
    new_path = os.path.join(base_path, f"{render_type}_v{new_number:03d}/")

    # Ensure the directory exists
    os.makedirs(bpy.path.abspath(new_path), exist_ok=True)

    print(f"Output directory: {new_path}")
    return new_path


def create_frame_list(context: bpy.types.Context, flipbook_dir: str) -> Path:
    flipbook_dir = Path(flipbook_dir)
    frame_list_file = flipbook_dir / "ffmpeg_frame_list.txt"
    duration = 1 / context.scene.render.fps
    image_extensions = ('.png', '.jpg', '.jpeg')
    files = []

    # Collect all valid image files in the directory
    for filename in os.listdir(flipbook_dir):
        if filename.lower().endswith(image_extensions):
            files.append(flipbook_dir / filename)

    # Sort files
    files = sorted(files)

    # Write the frame list with properly quoted full paths
    with open(frame_list_file, "w") as frame_list:
        for file in files:
            quoted_file = shlex.quote(str(file))  # Quote the full file path
            # Full path safely quoted
            frame_list.write(f"file {quoted_file}\n")
            frame_list.write(f"duration {duration}\n")

    return frame_list_file


def get_mp4_output_path(context, flipbook_dir: str) -> Path:
    props = context.scene.RMI_Props
    flipbook_dir = Path(flipbook_dir)
    return flipbook_dir.parent / f"{flipbook_dir.name}_{props.encoder}_{props.quality}.mp4"


def get_platform_terminal_command_list(command_list: list) -> list:
    cmd = []
    match OS.detect_os():
        case OS.WINDOWS:
            cmd = ["start", "cmd", '/c', ] + command_list
        case OS.MACOS:
            cmd = ["open", "-a", "Terminal.app", "--args"] + command_list
        case OS.LINUX:
            cmd = ["x-terminal-emulator", "-e"] + command_list
        case OS.UNKNOWN:
            raise RuntimeError("Unsupported platform")

    print(f"Command list: {cmd}")
    return cmd


def get_ffmpeg_command_list(context, flipbook_dir: Path) -> list:
    props = context.scene.RMI_Props
    encoder = props.encoder
    quality = props.quality
    fps = bpy.context.scene.render.fps
    frame_list_file = create_frame_list(context, flipbook_dir)
    output_file = get_mp4_output_path(context, flipbook_dir)

    ffmpeg_cmd = [
        "ffmpeg",
        "-safe", "0",
        "-r", f"{fps}",
        "-f", "concat",
        "-i", str(frame_list_file),
    ]

    match encoder:
        case "libx264":
            ffmpeg_cmd.extend([
                "-pix_fmt", "yuv420p",
                "-c:v", encoder,
                "-crf", f"{quality}"
            ])
        case "libx265":
            ffmpeg_cmd.extend([
                "-pix_fmt", "yuv420p",
                "-c:v", encoder,
                "-crf", f"{quality}",
                "-tune", "fastdecode",
                "-g", "1"
            ])
        case "libaom-av1":
            ffmpeg_cmd.extend([
                "-c:v", encoder,
                "-crf", f"{quality}"
            ])

    ffmpeg_cmd.append("-y")
    ffmpeg_cmd.append(str(output_file))

    return get_platform_terminal_command_list(ffmpeg_cmd)


def open_folder(path) -> None:
    match OS.detect_os():
        case OS.WINDOWS:
            os.startfile(path)
        case OS.MACOS:
            subprocess.Popen(["open", path])
        case OS.LINUX:
            subprocess.Popen(["xdg-open", path])


def save_blend_file() -> Tuple[bool, str]:
    try:
        if not bpy.data.is_saved:
            return False, "Blend file has never been saved before. Please save the file first."
        bpy.ops.wm.save_mainfile()
        return True, "Blend file saved successfully."
    except Exception as e:
        return False, f"Failed to save blend file: {str(e)}"


def get_encoders() -> list:
    cmd = ["ffprobe", "-encoders"]
    try:
        encoders_list = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError:
        return []

    # List of wanted encoders
    enc = ["libx264", "libx265", "libaom-av1"]

    encoders = []
    for c in enc:
        if c in encoders_list:
            encoders.append((c, c, ""))

    return encoders


ffmpeg_installed = is_ffmpeg_installed()
available_encoders = get_encoders() if ffmpeg_installed else []


def get_blend_file() -> Path:
    return Path(bpy.data.filepath).resolve()
