import os
import shutil


def merge_folders(folder_a: str, folder_b: str):
    """
    Looks for subfolders with matching names in Folder A and Folder B.
    For each match, it moves the contents from the subfolder in B into the
    subfolder in A, skipping any files that already exist in the destination.

    Args:
        folder_a (str): The primary folder (destination).
        folder_b (str): The secondary folder (source).
    """
    # --- Step 1: Validate Inputs ---
    print("--- Initializing ---")
    if not os.path.isdir(folder_a):
        print(f"Error: Folder A does not exist at '{folder_a}'")
        return
    if not os.path.isdir(folder_b):
        print(f"Error: Folder B does not exist at '{folder_b}'")
        return

    print(f"Destination (A): {folder_a}")
    print(f"Source (B):      {folder_b}")

    # --- Step 2: Iterate through subfolders in Folder A ---
    print("\n--- Searching for matching subfolders ---")

    found_match = False
    for subfolder_name in os.listdir(folder_a):
        # Construct the full path for the subfolder in Folder A
        path_in_a = os.path.join(folder_a, subfolder_name)

        # We are only interested in directories, not loose files in Folder A
        if os.path.isdir(path_in_a):
            # Construct the path for the potential matching subfolder in Folder B
            path_in_b = os.path.join(folder_b, subfolder_name)

            # --- Step 3: Check if a matching subfolder exists in Folder B ---
            if os.path.isdir(path_in_b):
                found_match = True
                print(f"\n✅ Found match: '{subfolder_name}'. Preparing to move contents.")

                # --- Step 4: Move contents from B's subfolder to A's subfolder ---
                # Iterate through every file and folder within the matched subfolder in B
                for item_name in os.listdir(path_in_b):
                    source_item_path = os.path.join(path_in_b, item_name)
                    destination_item_path = os.path.join(path_in_a, item_name)

                    # --- Step 5: Skip files that have the same name ---
                    # Check if a file or folder with the same name already exists in the destination
                    if os.path.exists(destination_item_path):
                        print(f"  -> SKIPPING: '{item_name}' already exists in the destination.")
                        continue  # Move to the next item

                    # If it doesn't exist, proceed with the move
                    try:
                        print(f"  -> MOVING:   '{item_name}'")
                        shutil.move(source_item_path, destination_item_path)
                    except Exception as e:
                        print(f"  -> ERROR: Could not move '{item_name}'. Reason: {e}")
            else:
                # This subfolder from A did not have a match in B
                pass

    if not found_match:
        print("No subfolders with matching names were found.")


if __name__ == "__main__":
    # --- IMPORTANT ---
    # Set the paths to your two input folders.
    # Use raw strings (r"...") for Windows paths to avoid issues with backslashes.

    # Folder A: The main folder that will RECEIVE the files.
    FOLDER_A_PATH = r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\RAW_DATA"

    # Folder B: The secondary folder whose contents will be MOVED.
    FOLDER_B_PATH = r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\0708\T6_VNIR\capturedData\captured"
    # -----------------

    merge_folders(FOLDER_A_PATH, FOLDER_B_PATH)
    print("\n\nScript finished.")