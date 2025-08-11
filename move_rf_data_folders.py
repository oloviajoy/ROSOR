import os
import shutil


def move_raw_folders(main_folder: str, destination_folder: str):
    """
    Recursively finds all subfolders ending in '_RAW' within a main folder
    and moves them to a specified destination folder.

    Args:
        main_folder (str): The full path to the top-level folder to search within.
        destination_folder (str): The full path to the folder where the '_RAW'
                                  folders will be moved.
    """
    # 1. Input validation: Check if the main source folder exists.
    if not os.path.isdir(main_folder):
        print(f"Error: The specified main folder does not exist: '{main_folder}'")
        return

    # 2. Ensure the destination folder exists. If not, create it.
    # The exist_ok=True argument prevents an error if the folder is already there.
    try:
        os.makedirs(destination_folder, exist_ok=True)
        print(f"Destination folder is ready: '{destination_folder}'")
    except Exception as e:
        print(f"Error: Could not create destination folder. Reason: {e}")
        return

    print(f"\nStarting search in: '{main_folder}'...")

    # A list to keep track of the folders we identify to move.
    folders_to_move = []

    # 3. Use os.walk() to recursively find all folders to be moved.
    # We do this first to avoid modifying the directory tree while walking it.
    for dirpath, dirnames, _ in os.walk(main_folder):
        for dirname in dirnames:
            if dirname.endswith("_RF"):
                # Construct the full path of the folder to be moved.
                source_path = os.path.join(dirpath, dirname)
                folders_to_move.append(source_path)

    # 4. Now, iterate through the list of found folders and move them.
    if not folders_to_move:
        print("No folders ending in '_RF' were found.")
        return

    print(f"\nFound {len(folders_to_move)} folders to move. Starting operation...")

    for source_path in folders_to_move:
        try:
            # Check if the source path still exists before trying to move it.
            if os.path.isdir(source_path):
                print(f"-> Moving '{source_path}'")

                # shutil.move() will move the entire folder and its contents.
                # It will place the folder *inside* the destination_folder.
                shutil.move(source_path, destination_folder)

                print(f"   -> Success.")
            else:
                print(f"-> Info: Folder '{source_path}' was already moved or deleted. Skipping.")

        except shutil.Error as e:
            # This specific error often means a folder with the same name already exists at the destination.
            print(
                f"   -> Error: Could not move folder. A folder with the same name might already exist at the destination. Details: {e}")
        except Exception as e:
            # Catch any other potential errors (e.g., permissions).
            print(f"   -> Error: An unexpected error occurred. Details: {e}")


if __name__ == "__main__":
    # --- IMPORTANT ---

    # 1. Set the path to the top-level folder you want to search through.
    main_search_folder = r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC"

    # 2. This is the destination where all found '_RAW' folders will be moved.
    destination_archive_folder = r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\RF_DATA"

    # -----------------

    move_raw_folders(main_search_folder, destination_archive_folder)
    print("\nScript finished.")