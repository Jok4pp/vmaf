import subprocess

def convert_mp4_to_yuv(input_file, output_file, width=3840, height=2160, first_frame_only=False):
    """
    Converts an MP4 file to a raw YUV file using FFmpeg.

    Args:
        input_file (str): Path to the input MP4 file.
        output_file (str): Path to the output YUV file.
        width (int): Width of the video (required for raw YUV).
        height (int): Height of the video (required for raw YUV).
        first_frame_only (bool): If True, only the first frame will be converted.
    """
    try:
        command = [
            "ffmpeg",
            "-i", input_file,
            "-pix_fmt", "yuv420p",
            "-s", f"{width}x{height}",
            "-f", "rawvideo",
        ]
        if first_frame_only:
            command.extend(["-frames:v", "1"])  # Add option to extract only the first frame
        command.append(output_file)

        subprocess.run(command, check=True)
        print(f"✅ Conversion successful! YUV file saved at: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during conversion: {e}")
    except FileNotFoundError:
        print("⚠️ FFmpeg not found. Please ensure it is installed and in your PATH.")

if __name__ == "__main__":
    input_mp4 = r"/home/joel-ludwig/Dokumente/Masterarbeit_Ludwig/vmaf/resource/dataset/LIVE_HDR_Public/LIVE_HDR_Part1/4k_15M_firework.mp4"
    output_yuv = r"/home/joel-ludwig/Dokumente/Masterarbeit_Ludwig/vmaf/LIVE-HDR_1/dis/4k_15M_firework.yuv"
    convert_mp4_to_yuv(input_mp4, output_yuv, first_frame_only=True)