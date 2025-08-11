import os
import shutil

# User-provided input folder
input_folder = r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\0714"
input_folder = input_folder.rstrip(os.sep)

# Build the output folder path by appending "_extracted"
output_folder = input_folder + "_extracted"
os.makedirs(output_folder, exist_ok=True)

for root, dirs, files in os.walk(input_folder):
    # Find all CSV files in this folder (case‑insensitive)
    csv_files = [f for f in files if f.lower().endswith(".csv")]
    if not csv_files:
        continue  # skip folders without CSVs

    # Pick the most recently modified CSV
    latest_csv = max(
        csv_files,
        key=lambda fn: os.path.getmtime(os.path.join(root, fn))
    )
    src_path = os.path.join(root, latest_csv)

    # Name the destination file after its parent folder
    parent_folder = os.path.basename(root)
    dest_path = os.path.join(output_folder, f"{parent_folder}.csv")

    shutil.copy2(src_path, dest_path)
    print(f"Copied CSV: {src_path} → {dest_path}")
