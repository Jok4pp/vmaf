import subprocess

def convert_mp4_to_yuv(input_file, output_file,
                       width=3840, height=2160,
                       first_frame_only=False,
                       output_format='yuv'):
    """
    Converts an MP4 file to either raw YUV or TIFF (YUV420) using FFmpeg.

    Args:
        input_file (str): Path to input MP4.
        output_file (str): Path to output file.
        width (int), height (int): Needed for raw YUV.
        first_frame_only (bool): Extract only the very first frame.
        output_format (str): 'yuv' (default) or 'tiff'
    """
    try:
        if output_format == 'yuv':
            # raw YUV420p
            cmd = [
                "ffmpeg",
                "-i", input_file,
                "-pix_fmt", "yuv444p10le",
                "-s", f"{width}x{height}"
            ]
            if first_frame_only:
                cmd += ["-frames:v", "1"]
            cmd += ["-f", "rawvideo", output_file]

        elif output_format == 'tiff':
            # single‐frame or multi‐frame TIFF(s) with YUV420p colorspace
            cmd = [
                "ffmpeg",
                "-i", input_file,
                "-pix_fmt", "yuv420p10le",
                "-s", f"{width}x{height}"
            ]
            if first_frame_only:
                cmd += ["-frames:v", "1"]
                # output_file should end in .tiff
                cmd += ["-f", "image2", "-vcodec", "tiff", output_file]
            else:
                # to dump all frames as frame0001.tiff, frame0002.tiff, ...
                base, ext = output_file.rsplit('.', 1)
                cmd += ["-f", "image2", "-vcodec", "tiff", base + "_%04d.tiff"]
        else:
            raise ValueError("output_format must be 'yuv' or 'tiff'")

        subprocess.run(cmd, check=True)
        print(f"✅ Conversion to {output_format} successful: {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"❌ ffmpeg error: {e}")
    except FileNotFoundError:
        print("⚠️ FFmpeg not found. Install it or add to PATH.")

if __name__ == "__main__":
    mp4 = "resource/dataset/LIVE_HDR_Public/LIVE_HDR_Part1/4k_ref_firework.mp4"
    # raw YUV:

    convert_mp4_to_yuv(mp4,
                      "LIVE-HDR_1/ref/4k_ref_firework2.yuv",
                      first_frame_only=True,
                      output_format='yuv')
    
    # single‐frame YUV420 TIFF:
    # convert_mp4_to_yuv(mp4,
    #                   "LIVE-HDR_tiff/dis/4k_15M_football3.tiff",
    #                   first_frame_only=True,
    #                   output_format='tiff')