import os
import shutil
import re
from collections import defaultdict


def sync_sbet_files_recursively(main_folder: str):
    """
    Recursively scans a main folder, identifying all flight data folders (VNIR and SWIR)
    at any nesting level. It groups them by a common key (e.g., TECK_T#_F#_Date).
    For each matched pair, it copies ALL files starting with "SBET" from the
    VNIR folder to the corresponding SWIR folder.

    Args:
        main_folder (str): The full path to the top-level directory to be processed.
    """
    if not os.path.isdir(main_folder):
        print(f"Error: The specified main folder does not exist: '{main_folder}'")
        return

    print(f"Recursively scanning main folder: {main_folder}")

    # --- Step 1: Index ALL data folders by a robust common key ---
    data_index = defaultdict(list)
    match_pattern = re.compile(r"(TECK_[tT]\d+(?:_F\d+)+_\d{4}_\d{2}_\d{2})", re.IGNORECASE)

    print("--- Indexing all potential data folders... ---")
    for dirpath, dirnames, _ in os.walk(main_folder):
        for dirname in dirnames:
            match = match_pattern.search(dirname)
            if match:
                key = match.group(1).upper()
                full_path = os.path.join(dirpath, dirname)
                data_index[key].append(full_path)

    print(f"Found {len(data_index)} unique flight data groups.")

    # --- Step 2: Process each group of matched folders ---
    print("\n--- Processing matched groups and copying files ---")
    if not data_index:
        print("No data folders matching the pattern were found. Nothing to do.")
        return

    for key, path_list in data_index.items():
        print(f"\nProcessing group for key: '{key}'")

        vnir_path = next((p for p in path_list if "VNIR" in p.upper()), None)
        swir_path = next((p for p in path_list if "SWIR" in p.upper()), None)

        if not vnir_path or not swir_path:
            print("  -> Warning: Could not find a complete VNIR/SWIR pair for this group. Skipping.")
            print(f"     Found paths: {path_list}")
            continue

        print(f"  -> Found VNIR: '{os.path.basename(vnir_path)}'")
        print(f"  -> Found SWIR: '{os.path.basename(swir_path)}'")

        # --- MODIFIED SBET FILE LOGIC ---

        # 1. Create a list to hold ALL SBET files found.
        sbet_files_to_copy = []
        try:
            for filename in os.listdir(vnir_path):
                if filename.lower().startswith('sbet'):
                    # 2. Add every matching file to the list.
                    sbet_files_to_copy.append(filename)
            # 3. The 'break' statement is removed.

        except FileNotFoundError:
            print(f"  -> Error: Could not access folder '{vnir_path}'. Skipping.")
            continue

        # 4. Check if the LIST is empty.
        if not sbet_files_to_copy:
            print("  -> No SBET files found in VNIR folder. Skipping.")
            continue

        print(f"  -> Found {len(sbet_files_to_copy)} SBET file(s): {', '.join(sbet_files_to_copy)}")

        # 5. Loop through the LIST of found files and copy each one.
        for sbet_filename in sbet_files_to_copy:
            source_path = os.path.join(vnir_path, sbet_filename)
            destination_path = os.path.join(swir_path, sbet_filename)

            try:
                print(f"    -> Copying '{sbet_filename}' to SWIR folder...")
                shutil.copy2(source_path, destination_path)
                print(f"    -> Success: Copied to destination.")
            except Exception as e:
                print(f"    -> Error: Failed to copy file '{sbet_filename}'. Reason: {e}")


if __name__ == "__main__":
    main_folder_path = r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC"
    sync_sbet_files_recursively(main_folder_path)
    print("\nScript finished.")