import os
import shutil


def organize_raw_files(main_folder):
    """
    Recursively searches through all subfolders. For each subdirectory found, it checks
    if it contains both raw and reflectance files. If so, it creates a new sibling
    folder ending in '_RAW' and performs the copy/move operations.

    Args:
        main_folder (str): The full path to the main folder to start the search from.
    """
    if not os.path.isdir(main_folder):
        print(f"Error: Main folder not found at '{main_folder}'")
        return

    # os.walk() will traverse the directory tree from the top down.
    # 'dirpath' is the current folder path we are in.
    # 'dirnames' is a list of subfolders inside dirpath.
    for dirpath, dirnames, _ in os.walk(main_folder):

        print(f"\n--- Scanning inside directory: {dirpath} ---")

        # We need a copy of the list to iterate over, as we will modify the original.
        for subfolder_name in list(dirnames):

            # Skip any folders we might have created in a previous run.
            if subfolder_name.endswith('_RAW'):
                continue

            target_dir_path = os.path.join(dirpath, subfolder_name)

            try:
                # --- NEW LOGIC: Look inside the subdirectory ---
                files_in_subdir = os.listdir(target_dir_path)

                # Main Trigger Condition: The subdirectory must contain a mix of files.
                has_other_files = any("_rf" not in f for f in files_in_subdir)
                has_rf_files = any("_rf" in f for f in files_in_subdir)

                if has_other_files and has_rf_files:
                    print(f"-> Condition met for subfolder: '{subfolder_name}'")

                    # --- "PLAN THEN EXECUTE" LOGIC ---
                    files_to_copy = []
                    files_to_move = []

                    for filename in files_in_subdir:
                        if not os.path.isfile(os.path.join(target_dir_path, filename)):
                            continue
                        if filename.startswith("SBET_"):
                            files_to_copy.append(filename)
                        elif "_rf" in filename:
                            pass
                        else:
                            files_to_move.append(filename)

                    if not files_to_copy and not files_to_move:
                        print("   -> No applicable files to copy or move. Skipping.")
                        continue

                    # Create the new folder as a SIBLING to the one being processed.
                    new_folder_name = f"{subfolder_name}_RAW"
                    new_folder_path = os.path.join(dirpath, new_folder_name)
                    os.makedirs(new_folder_path, exist_ok=True)
                    print(f"   -> Created/verified new folder: {new_folder_path}")

                    # Execute the copy/move actions
                    for filename in files_to_copy:
                        source_path = os.path.join(target_dir_path, filename)
                        dest_path = os.path.join(new_folder_path, filename)
                        print(f"     -> COPYING (SBET): '{filename}'")
                        shutil.copy2(source_path, dest_path)

                    for filename in files_to_move:
                        source_path = os.path.join(target_dir_path, filename)
                        dest_path = os.path.join(new_folder_path, filename)
                        print(f"     -> MOVING  (Other): '{filename}'")
                        shutil.move(source_path, dest_path)

                    # IMPORTANT: Remove the processed folder from the list so os.walk doesn't go into it.
                    dirnames.remove(subfolder_name)

            except PermissionError:
                print(f"-> Permission denied for folder: '{subfolder_name}'. Skipping.")
            except Exception as e:
                print(f"An error occurred while processing subfolder {subfolder_name}: {e}")


if __name__ == "__main__":
    # --- IMPORTANT ---
    # Set this to the top-level folder where you want to start the search.
    # For your example, this path is correct.
    main_folder_to_process = r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC"

    # -----------------

    organize_raw_files(main_folder_to_process)
    print("\n\nScript finished.")