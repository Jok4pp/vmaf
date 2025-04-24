import os
import csv
import json

def find_yuv_files_and_csv(directory):
    """
    Find all .yuv files and the corresponding .csv file in the given directory.

    Args:
        directory (str): Path to the directory.

    Returns:
        tuple: List of .yuv files and the path to the .csv file.
    """
    yuv_files = []
    csv_file = None

    for file in os.listdir(directory):
        if file.endswith(".yuv"):
            yuv_files.append(file)
        elif file.endswith(".csv"):
            csv_file = os.path.join(directory, file)

    return yuv_files, csv_file


def parse_csv(csv_file):
    """
    Parse the CSV file to extract metadata.

    Args:
        csv_file (str): Path to the CSV file.

    Returns:
        dict: A dictionary mapping file names to metadata (e.g., DMOS scores).
    """
    metadata = {}
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Assuming the CSV has columns: "file_name", "dmos"
            file_name = row["video"]
            dmos = float(row["sureal_bright_mos"])
            metadata[file_name] = dmos
    return metadata


def generate_dataset(directory, yuv_files, metadata, output_file):
    """
    Generate a dataset file in the format of NFLX_dataset_public.py.

    Args:
        directory (str): Path to the directory containing the .yuv files.
        yuv_files (list): List of .yuv files.
        metadata (dict): Metadata extracted from the CSV file.
        output_file (str): Path to the output dataset file.
    """
    dataset_name = os.path.basename(directory)
    ref_dir = os.path.join(directory, "ref")
    dis_dir = os.path.join(directory, "dis")

    ref_videos = []
    dis_videos = []

    for idx, yuv_file in enumerate(yuv_files):
        file_path = os.path.join(directory, yuv_file)
        content_id = idx
        if "ref" in yuv_file.lower():
            ref_videos.append({
                "content_id": content_id,
                "content_name": os.path.splitext(yuv_file)[0],
                "path": file_path
            })
        else:
            dmos = metadata.get(yuv_file, None)
            if dmos is not None:
                dis_videos.append({
                    "asset_id": idx,
                    "content_id": content_id,
                    "dmos": dmos,
                    "path": file_path
                })

    # Write the dataset to a Python file
    with open(output_file, mode="w", encoding="utf-8") as f:
        f.write(f"dataset_name = '{dataset_name}'\n")
        f.write("yuv_fmt = 'yuv420p'\n")
        f.write("width = 3840\n")
        f.write("height = 2160\n\n")
        f.write(f"ref_dir = '{ref_dir}'\n")
        f.write(f"dis_dir = '{dis_dir}'\n\n")
        f.write("ref_videos = ")
        f.write(json.dumps(ref_videos, indent=2))
        f.write("\n\ndis_videos = ")
        f.write(json.dumps(dis_videos, indent=2))
        f.write("\n")


if __name__ == "__main__":
    # Define the directory containing .yuv and .csv files
    directory = r"C:\Users\jokap\OneDrive\Dokumente\Masterarbeit\vmaf\resource\dataset\LIVE_HDR_Part1"

    # Find .yuv files and the .csv file
    yuv_files, csv_file = find_yuv_files_and_csv(directory)

    if not csv_file:
        print("Error: No CSV file found in the directory.")
        exit(1)

    # Parse the CSV file for metadata
    metadata = parse_csv(csv_file)

    # Generate the dataset file
    output_file = os.path.join(directory, "generated_dataset.py")
    generate_dataset(directory, yuv_files, metadata, output_file)

    print(f"Dataset file generated: {output_file}")