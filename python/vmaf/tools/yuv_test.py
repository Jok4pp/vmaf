import numpy as np

def read_yuv_value(yuv_file, width, height, x, y, bitdepth=10):
    """
    Reads the Y, U, and V values at (x,y) from a planar YUV420 file
    with arbitrary bitdepth (8 or 10).

    :param yuv_file: Path to the YUV file
    :param width: Width of the YUV frame
    :param height: Height of the YUV frame
    :param x: X-coordinate (column)
    :param y: Y-coordinate (row)
    :param bitdepth: Bit depth of the YUV samples (default: 10)
    :return: Tuple of (Y, U, V) values
    """
    # number of bytes per sample
    sample_bytes = (bitdepth + 7) // 8
    # mask to extract only 'bitdepth' bits
    mask = (1 << bitdepth) - 1

    # plane dimensions
    y_stride = width * sample_bytes
    uv_width = width // 2
    uv_height = height // 2
    uv_stride = uv_width * sample_bytes

    with open(yuv_file, 'rb') as f:
        # --- Y plane ---
        y_offset = (y * width + x) * sample_bytes
        f.seek(y_offset)
        raw = f.read(sample_bytes)
        y_val = np.frombuffer(raw, dtype=f'<u{sample_bytes}')[0] & mask

        # --- U plane ---
        u_plane_start = width * height * sample_bytes
        u_offset = u_plane_start + ((y // 2) * uv_width + (x // 2)) * sample_bytes
        f.seek(u_offset)
        raw = f.read(sample_bytes)
        u_val = np.frombuffer(raw, dtype=f'<u{sample_bytes}')[0] & mask

        # --- V plane ---
        v_plane_start = u_plane_start + uv_width * uv_height * sample_bytes
        v_offset = v_plane_start + ((y // 2) * uv_width + (x // 2)) * sample_bytes
        f.seek(v_offset)
        raw = f.read(sample_bytes)
        v_val = np.frombuffer(raw, dtype=f'<u{sample_bytes}')[0] & mask

    return int(y_val), int(u_val), int(v_val)


# Example usage
if __name__ == "__main__":
    yuv_file_path = "LIVE-HDR_1/ref/4k_ref_firework.yuv"  # Replace with your YUV file path
    frame_width = 3840  # Replace with the width of your YUV frame
    frame_height = 2160  # Replace with the height of your YUV frame
    x_coord = 0
    y_coord = 0

    y, u, v = read_yuv_value(
        yuv_file_path,
        frame_width, frame_height,
        x_coord, y_coord,
        bitdepth=10
    )
    print(f"Y: {y}, U: {u}, V: {v}")