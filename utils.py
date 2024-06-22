

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy
import os
import glob
import platform
import subprocess
from pathlib import Path


def is_windows():
    return os.name == 'nt'


def is_macos():
    return os.name == 'posix' and platform.system() == "Dawriw"


def is_linux():
    return os.name == 'posix' and platform.system() == "Linux"


# List of wanter encoders
enc = ["libx264", "libx265", "libaom-av1"]


def open_folder(path):
    if is_windows():
        os.startfile(path)
    elif is_macos():
        subprocess.Popen(["open", path])
    elif is_linux():
        subprocess.Popen(["xdg-open", path])


def is_ffmpeg_installed():
    try:
        cmd = ["ffprobe", "-version"]
        _ = subprocess.check_output(cmd)
        return True
    except Exception as e:
        print("ERROR ", e)
        return False


def get_encoders():
    cmd = ["ffprobe", "-encoders"]
    encoders_list = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

    encoders = []
    for c in enc:
        if c in str(encoders_list):
            encoders.append(tuple((c, c, "")))

    return encoders


def get_blend_file():
    blend_file = bpy.data.filepath
    return blend_file


def get_export_dir():
    filepath = bpy.path.abspath(bpy.context.scene.render.filepath)
    return Path(filepath).resolve()


def get_export_parent_dir():
    export_path = get_export_dir()
    return export_path.parent

# Example of how to use these functions:


def get_render_path():
    export_parent_dir = get_export_dir()
    blend_file = get_blend_file()
    export_path = get_export_dir()
    return export_parent_dir, blend_file, export_path


def get_platform_terminal_command_list(command_list):
    """Append command to platform and distro temirnal launching command"""
    if is_windows():
        return ["start", '""'] + command_list
    elif is_macos():
        return ["open", "-a", "Terminal.app", "--args"] + command_list
    elif is_linux():
        desktop_environment = os.environ.get('XDG_CURRENT_DESKTOP', '')
        if desktop_environment == 'GNOME':
            return ["gnome-terminal", "--"] + command_list
        elif desktop_environment == 'KDE':
            return ["konsole", "--hold", "-e"] + command_list
        elif desktop_environment == 'XFCE':
            return ["xfce4-terminal", "--command"] + command_list
        else:
            return ["x-terminal-emulator", "-e"] + command_list
    else:
        raise RuntimeError("Unsupported platform")


def get_frame_list(render_folder, duration):

    frame_list_file = os.path.join(render_folder, "ffmpeg_input.txt")

    # Use list comprehension to get both .png and .jpg files
    files = [file for ext in ['*.png', '*.jpg']
             for file in glob.glob(os.path.join(render_folder, ext))]

    files.sort()

    try:
        with open(frame_list_file, "w+") as outfile:
            for file in files:
                outfile.write(f"file '{file}'\n")
                outfile.write(f"duration {duration}\n")
        outfile.close()
    except FileNotFoundError as e:
        print('Error ', e)
        print(f"The {frame_list_file} does not exist")

    return frame_list_file
