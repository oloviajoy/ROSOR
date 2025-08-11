import os
import pandas as pd
import shutil
from datetime import datetime


def process_flight_data(main_folder):
    """
    Main function to process flight data folders recursively.

    This script searches for a central 'GPS_data' folder. It then recursively
    walks through the entire main_folder directory tree to find every
    'imu_gps.txt' file. For each one found, it determines a time range,
    finds the corresponding .T04 files from the central folder, and copies
    them into a new 'gps_data' subfolder alongside the 'imu_gps.txt'.
    """
    # Step 1: Locate the central GPS data source folder
    gps_source_folder_name = "GPS_data"
    gps_source_path = os.path.join(main_folder, gps_source_folder_name)

    if not os.path.isdir(gps_source_path):
        print(f"Error: The central '{gps_source_folder_name}' folder was not found directly inside '{main_folder}'.")
        return

    # Step 2: Read and parse all .T04 files from the source folder once for efficiency
    try:
        all_files_in_gps_source = os.listdir(gps_source_path)
        t04_files = sorted([f for f in all_files_in_gps_source if f.endswith(".T04")])
        if not t04_files:
            print(f"Warning: No .T04 files were found in '{gps_source_path}'. The script cannot continue.")
            return

        t04_file_times = []
        for f in t04_files:
            time_str = f[-8:-4]
            if time_str.isdigit():
                t04_file_times.append((f, int(time_str)))
    except Exception as e:
        print(f"Error reading or parsing files from '{gps_source_path}': {e}")
        return

    # Step 3: Recursively walk through the entire main_folder directory tree
    # This will check every subfolder at every level.
    print(f"\nStarting recursive search for 'imu_gps.txt' in '{main_folder}'...")
    for dirpath, _, filenames in os.walk(main_folder):
        # Check if an 'imu_gps.txt' file exists in the current directory
        if "imu_gps.txt" in filenames:

            # The folder containing imu_gps.txt is our target processing folder
            imu_folder_path = dirpath

            print(f"\n--- Found file. Processing folder: {imu_folder_path} ---")
            imu_file_path = os.path.join(imu_folder_path, "imu_gps.txt")

            try:
                # The rest of the logic is the same, but it now operates on the
                # deeply nested folder path found by os.walk().

                with open(imu_file_path, 'r', errors='ignore') as f:
                    first_line = f.readline()

                headers = None
                timestamp_column_name = None
                date_format_string = None

                if "Timestamp" in first_line and "Status" in first_line:
                    print("Detected 'Timestamp' (new) header format.")
                    headers = ["Roll", "Pitch", "Yaw", "Lat", "Lon", "Alt", "Timestamp", "Gps_UTC_Date&Time", "Status",
                               "Heading"]
                    timestamp_column_name = "Gps_UTC_Date&Time"
                    date_format_string = "%Y/%m/%d %H:%M:%S"
                elif "Gps_Raw_Date&Time" in first_line:
                    print("Detected 'Gps_Raw_Date&Time' (old) header format.")
                    headers = ["Roll", "Pitch", "Yaw", "Lat", "Lon", "Alt", "GPS_UTC", "Gps_UTC_Date&Time",
                               "Track_Angle", "Geoid_Separation", "SystemTime", "Speed", "Gps_Raw_Date&Time"]
                    timestamp_column_name = "Gps_Raw_Date&Time"
                    date_format_string = "%Y/%b/%d %H:%M:%S"
                else:
                    print(f"Warning: Unknown header format in '{imu_file_path}'. Skipping.")
                    continue

                df = pd.read_csv(
                    imu_file_path, sep='\t', header=None, names=headers,
                    skiprows=1, on_bad_lines='skip', dtype=str
                ).dropna(subset=[timestamp_column_name])

                if df.empty:
                    print(f"Warning: '{imu_file_path}' is empty or has no valid timestamp data.")
                    continue

                non_zero_roll = df[df['Roll'].astype(float) != 0]
                if non_zero_roll.empty:
                    print(f"Warning: No rows with Roll != 0 found in '{imu_file_path}'.")
                    continue

                start_row = non_zero_roll.iloc[0]
                start_time_value = start_row[timestamp_column_name]
                end_time_value = df.iloc[-1][timestamp_column_name]

                start_dt = datetime.strptime(start_time_value.split('.')[0], date_format_string)
                end_dt = datetime.strptime(end_time_value.split('.')[0], date_format_string)

                hour_min_time_start = int(f"{start_dt.hour:02d}{start_dt.minute:02d}")
                hour_min_time_end = int(f"{end_dt.hour:02d}{end_dt.minute:02d}")

                print(f"Time range found (HourMin): {hour_min_time_start:04d} to {hour_min_time_end:04d}")

                start_t04_file, end_t04_file = None, None
                candidate_start_files = [item for item in t04_file_times if item[1] <= hour_min_time_start]
                if candidate_start_files:
                    start_t04_file = max(candidate_start_files, key=lambda item: item[1])[0]

                candidate_end_files = [item for item in t04_file_times if item[1] >= hour_min_time_end]
                if candidate_end_files:
                    end_t04_file = min(candidate_end_files, key=lambda item: item[1])[0]

                if not start_t04_file or not end_t04_file:
                    print("Could not find matching .T04 files for the identified time range.")
                    continue

                if t04_files.index(start_t04_file) > t04_files.index(end_t04_file):
                    print(
                        f"Error: Identified start file '{start_t04_file}' comes after end file '{end_t04_file}'. Skipping copy.")
                    continue

                print(f"Identified start file: {start_t04_file}")
                print(f"Identified end file: {end_t04_file}")

                start_index = t04_files.index(start_t04_file)
                end_index = t04_files.index(end_t04_file)
                files_to_copy = t04_files[start_index: end_index + 1]

                # Create the destination folder inside the folder where the imu_gps.txt was found
                destination_folder = os.path.join(imu_folder_path, "gps_data")
                os.makedirs(destination_folder, exist_ok=True)

                print(f"Copying {len(files_to_copy)} files to '{destination_folder}'...")
                for file_name in files_to_copy:
                    source_file = os.path.join(gps_source_path, file_name)
                    destination_file = os.path.join(destination_folder, file_name)
                    if not os.path.exists(destination_file):
                        shutil.copy2(source_file, destination_file)
                print("Copy complete.")

            except ValueError as ve:
                print(f"A date format error occurred processing the file: {ve}.")
            except Exception as e:
                print(f"An unexpected error occurred while processing {imu_folder_path}: {e}")


if __name__ == "__main__":
    # --- IMPORTANT ---
    # Set the top-level folder you want to start the search from.
    main_folder_path = r"\\RosorFieldNas1\Home\TECK_WHITE_EARTH\TECK_HYPERSPEC\0714"
    # -----------------

    if os.path.isdir(main_folder_path):
        process_flight_data(main_folder_path)
        print("\nScript finished.")
    else:
        print(f"Error: The specified main folder does not exist: '{main_folder_path}'")