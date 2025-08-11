import os
import shutil


def organize_rf_files(main_folder):
    """
    Recursively searches through all subfolders.
    If a subfolder contains both _rf and _igm files,
    it creates a sibling folder ending in '_RF' and moves
    only the _rf or rf.hdr files into it.
    """
    if not os.path.isdir(main_folder):
        print(f"Error: Main folder not found at '{main_folder}'")
        return

    for dirpath, dirnames, _ in os.walk(main_folder):
        print(f"\n--- Scanning inside directory: {dirpath} ---")

        for subfolder_name in list(dirnames):
            if subfolder_name.endswith('_RF'):
                continue  # Skip already processed folders

            target_dir_path = os.path.join(dirpath, subfolder_name)

            try:
                files_in_subdir = os.listdir(target_dir_path)

                has_rf_files = any(
                    f.lower().endswith("_rf") or f.lower().endswith("rf.hdr")
                    for f in files_in_subdir
                )
                has_igm_files = any("_igm" in f.lower() for f in files_in_subdir)

                if has_rf_files and has_igm_files:
                    print(f"-> Condition met for subfolder: '{subfolder_name}'")

                    # Collect only _rf or rf.hdr files
                    files_to_move = [
                        f for f in files_in_subdir
                        if os.path.isfile(os.path.join(target_dir_path, f)) and
                           (f.lower().endswith("_rf") or f.lower().endswith("rf.hdr") or f.lower().endswith("rf.bin"))
                    ]

                    if not files_to_move:
                        print("   -> No matching _rf or rf.hdr files to move. Skipping.")
                        continue

                    # Create the new _RF folder
                    new_folder_name = f"{subfolder_name}_RF"
                    new_folder_path = os.path.join(dirpath, new_folder_name)
                    os.makedirs(new_folder_path, exist_ok=True)
                    print(f"   -> Created/verified new folder: {new_folder_path}")

                    # Move the files
                    for filename in files_to_move:
                        source_path = os.path.join(target_dir_path, filename)
                        dest_path = os.path.join(new_folder_path, filename)
                        print(f"     -> MOVING: '{filename}'")
                        shutil.move(source_path, dest_path)

                    # Prevent descending into the processed folder
                    dirnames.remove(subfolder_name)

            except PermissionError:
                print(f"-> Permission denied for folder: '{subfolder_name}'. Skipping.")
            except Exception as e:
                print(f"An error occurred while processing subfolder {subfolder_name}: {e}")


if __name__ == "__main__":
    main_folder_to_process = r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC"
    organize_rf_files(main_folder_to_process)
    print("\n\nScript finished.")
