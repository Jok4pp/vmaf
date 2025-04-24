import subprocess

def convert_mp4_to_yuv(input_file, output_file, width=3840, height=2160):
    """
    Converts an MP4 file to a raw YUV file using FFmpeg.

    Args:
        input_file (str): Path to the input MP4 file.
        output_file (str): Path to the output YUV file.
        width (int): Width of the video (required for raw YUV).
        height (int): Height of the video (required for raw YUV).
    """
    try:
        command = [
            "ffmpeg",
            "-i", input_file,
            "-pix_fmt", "yuv420p",
            "-s", f"{width}x{height}",
            "-f", "rawvideo",
            output_file
        ]
        subprocess.run(command, check=True)
        print(f"✅ Conversion successful! YUV file saved at: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during conversion: {e}")
    except FileNotFoundError:
        print("⚠️ FFmpeg not found. Please ensure it is installed and in your PATH.")

if __name__ == "__main__":
    input_mp4 = r"C:\Users\jokap\Dokumente\Masterarbeit\vmaf\resource\dataset\LIVE_HDR_Part1\4k_6M_football2.mp4"
    output_yuv = r"C:\Users\jokap\Dokumente\Masterarbeit\vmaf\4k_6M_football2.yuv"
    convert_mp4_to_yuv(input_mp4, output_yuv)
