import os
import shutil


def sync_metadata_files_recursively(folder_a: str, folder_b: str):
    """
    Recursively scans Folder A and Folder B to find matching subfolder pairs
    (where Folder B's subfolder name is Folder A's name + '_RAW'). It then
    copies all .txt files AND any file containing 'sceneWhiteReference' from
    the Folder B subfolder into the corresponding Folder A subfolder,
    skipping existing files.

    Args:
        folder_a (str): The primary folder path (destination).
        folder_b (str): The secondary folder path (source, containing '_RAW' folders).
    """
    # --- Step 1: Validate Inputs ---
    print("--- Initializing Script ---")
    if not os.path.isdir(folder_a):
        print(f"Error: Folder A (destination) does not exist at '{folder_a}'")
        return
    if not os.path.isdir(folder_b):
        print(f"Error: Folder B (source) does not exist at '{folder_b}'")
        return

    print(f"Destination (Folder A): {folder_a}")
    print(f"Source (Folder B):      {folder_b}")

    # --- Step 2: Index all subfolders ---
    print("\n--- Indexing all subfolders. This may take a moment... ---")
    subfolders_in_a = {dirname: os.path.join(dirpath, dirname) for dirpath, dirnames, _ in os.walk(folder_a) for dirname
                       in dirnames}
    subfolders_in_b = {dirname: os.path.join(dirpath, dirname) for dirpath, dirnames, _ in os.walk(folder_b) for dirname
                       in dirnames}
    print(f"Found {len(subfolders_in_a)} subfolders in Folder A and {len(subfolders_in_b)} subfolders in Folder B.")

    # --- Step 3: Find matches and process ---
    print("\n--- Starting Search for Matching Folders and Copying Files ---")
    found_any_matches = False
    for subfolder_name_a, path_in_a in subfolders_in_a.items():
        matching_subfolder_name_b = f"RAW_{subfolder_name_a}"

        if matching_subfolder_name_b in subfolders_in_b:
            found_any_matches = True
            path_in_b = subfolders_in_b[matching_subfolder_name_b]

            print(f"\n✅ Found a match:")
            print(f"  -> Destination: '{path_in_a}'")
            print(f"  -> Source:      '{path_in_b}'")

            # --- Step 4: Copy specified files from B to A with DETAILED LOGGING ---
            try:
                # --- NEW DIAGNOSTIC LOGIC ---
                files_in_source = os.listdir(path_in_b)
                if not files_in_source:
                    print("    -> Source folder is empty. Nothing to copy.")
                    continue

                print(f"    -> Found {len(files_in_source)} items in source. Checking each...")
                copied_count = 0

                for filename in files_in_source:
                    is_target_file = (
                            filename.lower().endswith(".txt") or
                            "sceneWhiteReference" in filename
                    )

                    if is_target_file:
                        source_file_path = os.path.join(path_in_b, filename)
                        destination_file_path = os.path.join(path_in_a, filename)

                        if os.path.exists(destination_file_path):
                            print(f"      -> SKIPPING: '{filename}' (already exists).")
                        else:
                            try:
                                print(f"      -> COPYING:  '{filename}'")
                                shutil.copy2(source_file_path, destination_file_path)
                                copied_count += 1
                            except Exception as e:
                                print(f"      -> ERROR: Could not copy '{filename}'. Reason: {e}")
                    else:
                        # This tells us about files that were seen but didn't match the criteria.
                        print(f"      -> IGNORING: '{filename}' (does not match criteria).")

                print(f"    -> Finished processing. Copied {copied_count} file(s) for this pair.")

            except Exception as e:
                print(f"  -> ERROR: Could not access files in '{path_in_b}'. Reason: {e}")

    if not found_any_matches:
        print("\nNo matching subfolder pairs were found anywhere in the directory trees.")


if __name__ == "__main__":
    FOLDER_A_PATH = r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC"
    FOLDER_B_PATH = r"\\TRUENAS\Vault_1\2025_projects\Teck White earth\RAW_DATA\RAW_still need to add more raw data"

    sync_metadata_files_recursively(FOLDER_A_PATH, FOLDER_B_PATH)
    print("\n\nScript finished.")