import os
import shutil


def organize_flight_data(source_folder):
    """
    Organizes files named like 'raw_13000_rd_rf_igm' and their corresponding
    '.hdr' files into new folders based on the last three digits of the
    number in the filename.

    Args:
        source_folder (str): The path to the folder containing the files.
    """
    if not os.path.isdir(source_folder):
        print(f"Error: The source folder '{source_folder}' does not exist.")
        return

    for filename in os.listdir(source_folder):

        # --- MODIFIED CONDITION ---
        # We now look for files that end in '_igm' but NOT '_igm.hdr'.
        # This ensures we start with the primary data file.
        is_primary_file = (
                os.path.isfile(os.path.join(source_folder, filename)) and
                filename.startswith("raw_") and
                filename.endswith("_igm") and
                not filename.endswith(".hdr")
        )

        if is_primary_file:
            try:
                # Extract the numerical part of the filename
                parts = filename.split('_')
                if len(parts) > 1:
                    number_str = parts[1]
                    flight_group = number_str[-3:]

                    # Create the new folder name and path
                    new_folder_name = f"Flight_{flight_group}"
                    new_folder_path = os.path.join(source_folder, new_folder_name)
                    os.makedirs(new_folder_path, exist_ok=True)

                    # --- LOGIC TO MOVE BOTH FILES ---

                    # 1. Move the primary '_igm' file
                    source_file_path = os.path.join(source_folder, filename)
                    destination_file_path = os.path.join(new_folder_path, filename)
                    shutil.move(source_file_path, destination_file_path)
                    print(f"Moved '{filename}' to '{new_folder_name}'")

                    # 2. Look for and move the corresponding '.hdr' file
                    header_filename = filename + ".hdr"
                    header_source_path = os.path.join(source_folder, header_filename)

                    # Check if the header file actually exists
                    if os.path.exists(header_source_path):
                        header_destination_path = os.path.join(new_folder_path, header_filename)
                        shutil.move(header_source_path, header_destination_path)
                        print(f"Moved '{header_filename}' to '{new_folder_name}'")

            except (IndexError, ValueError) as e:
                print(f"Could not process file '{filename}': {e}")


if __name__ == "__main__":
    # --- IMPORTANT ---
    # Replace this with the actual path to your folder
    folder_to_organize = r"\\RosorFieldNas1\Home\TECK_WHITE_EARTH\TECK_HYPERSPEC\0706\T2_VNIR\TECK_T2_F9_F10_2025_07_06_17_35_17_980"
    # -----------------

    organize_flight_data(folder_to_organize)
    print("\nFile organization complete.")