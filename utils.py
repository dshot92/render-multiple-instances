# SPDX-License-Identifier: GPL-2.0-or-later

# ----------------------------------------------------------
# Author: Daniele Stochino (dshot92)
# ----------------------------------------------------------

import bpy
import os
import glob
import platform
import subprocess

from .preferences import getPreferences


def isWindows():
    return os.name == 'nt'


def isMacOS():
    return os.name == 'posix' and platform.system() == "Dawriw"


def isLinux():
    return os.name == 'posix' and platform.system() == "Linux"


# List of wanter encoders
enc = ["libx264", "libx265", "libaom-av1"]


def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)


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


def get_render_path():
    path_render = (os.path.realpath(
        bpy.path.abspath(bpy.context.scene.render.filepath)))

    last_char = bpy.context.scene.render.filepath[-1]
    if last_char in "/\\":
        path_render += os.sep
        render_filename = path_render.split(os.sep)[-2]
        parent_render_path = os.path.dirname(path_render)
        parent_render_path = os.path.dirname(parent_render_path)
    else:
        render_filename = path_render.split(os.sep)[-2]
        path_render = os.path.dirname(path_render)
        parent_render_path = os.path.split(path_render)[0]

    return parent_render_path, render_filename, path_render


def get_render_command(blend_file_path, blender_path, start_frame, end_frame):

    if isWindows():
        command = ["start", '""', f'"{blender_path}"', "-b",
                   f'"{blend_file_path}"', "-s", f"{start_frame}", "-e",
                   f"{end_frame}", "-a"]
    elif isMacOS():
        command = ["open", "-a", f'"{blender_path}"', "--args", "-b",
                   f'"{blend_file_path}"', "-s", f"{start_frame}", "-e",
                   f"{end_frame}", "-a"]
    elif isLinux():
        term = getPreferences().terminal_emulator.split(" ")
        term = " ".join(term)
        command = [f"{term}", f"{blender_path}", "-b", f'"{blend_file_path}"',
                   "-s", f"{start_frame}", "-e", f"{end_frame}", "-a", "&"]

    return ' '.join(command)


def get_frame_list(render_folder, duration):

    frame_list_file = os.path.join(render_folder, "ffmpeg_input.txt")

    files = []
    for file in glob.glob(render_folder + os.sep + "*.png"):
        files.append(file)

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


def get_ffmpeg_command(render_folder, duration, fps, encoder, quality, output_file):

    frame_list_file = os.path.join(render_folder, "ffmpeg_input.txt")

    files = []
    for file in glob.glob(render_folder + os.sep + "*.png"):
        files.append(file)

    files.sort()

    try:
        with open(frame_list_file, "w+") as outfile:
            for file in files:
                outfile.write(f"file '{file}'\n")
                outfile.write(f"duration {duration}\n")
        outfile.close()
    except FileNotFoundError:
        print(f"The {frame_list_file} does not exist")

    output_file = (os.path.realpath(bpy.path.abspath(output_file)))
    if ".mp4" not in output_file:
        output_file += ".mp4"

    # https://ntown.at/de/knowledgebase/cuda-gpu-accelerated-h264-h265-hevc-video-encoding-with-ffmpeg/

    if encoder == "libx264":
        # ffmpeg_command = f'ffmpeg -safe 0 -r {fps} -f concat
        # -i "{frame_list_file}" -pix_fmt yuv420p -c:v {encoder}
        # -crf {quality} -tune fastdecode "{output_file}" -y'
        ffmpeg_command = ["ffmpeg", "-safe", "0", "-r", f"{fps}", "-f",
                          "concat", "-i", f'"{frame_list_file}"',
                          "-pix_fmt", "yuv420p", "-c:v",
                          f"{encoder}", "-crf", f"{quality}",
                          f'"{output_file}"', "-y"]

    elif encoder == "libx265":
        # ffmpeg -i input.mov -pix_fmt yuv420p -c:v libx265
        # -crf 18 -tune fastdecode -g 1 output.mp4
        ffmpeg_command = ["ffmpeg", "-safe", "0", "-r", f"{fps}", "-f",
                          "concat", "-i", f'"{frame_list_file}"', "-pix_fmt",
                          "yuv420p", "-c:v", f"{encoder}", "-crf",
                          f"{quality}", "-tune", "fastdecode", "-g", "1",
                          f'"{output_file}"', "-y"]

    elif encoder == "libaom-av1":
        # ffmpeg -i input.mov -pix_fmt yuv420p -c:v libx265 -crf 18
        # -tune fastdecode -g 1 output.mp4
        ffmpeg_command = ["ffmpeg", "-strict", "-2", "-safe", "0", "-r",
                          f"{fps}", "-f", "concat", "-i",
                          f'"{frame_list_file}"', "-c:v", f"{encoder}",
                          "-strict", "-2", "-crf", f"{quality}",
                          f'"{output_file}"', "-y"]

    # Convert list to string
    ffmpeg_command = ' '.join(ffmpeg_command)

    if isWindows():
        ffmpeg_command = 'start "" ' + ffmpeg_command
    elif isMacOS():
        ffmpeg_command = 'open -a Terminal.app --args ' + ffmpeg_command
    elif isLinux():
        ffmpeg_command = ffmpeg_command + " &"

    return ffmpeg_command
