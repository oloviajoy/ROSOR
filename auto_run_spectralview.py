import os
import time
import pyautogui

# ==============================================================================
# --- CONFIGURATION ---
# ==============================================================================
# 1. The single, shared folder where all target files will appear.
#    Example: "C:\\Users\\YourUser\\Desktop\\Processing_Queue"
INPUT_FOLDER_PATH = r"\\RosorFieldNas1\Home\TECK_WHITE_EARTH\TECK_HYPERSPEC\0630\T4_VNIR\TECK_T4_F7_F8_2025_06_30_18_05_30_581\deliverables"

# 2. A list of the base file names to monitor.
#    The order MUST correspond to the order of your Windows virtual desktops.
#    The script will END after finding the .hdr file for the LAST item in this list.
FILE_NAMES_TO_MONITOR = [
    "VNIR_T4_F7_F8_045",
    "VNIR_T4_F7_F8_768",
    "VNIR_T4_F7_F8_012"# <-- The script will stop after processing this file.
    # Add as many base file names as you have virtual desktops
]


# ==============================================================================
# --- SCRIPT START ---
# ==============================================================================

def wait_for_file(base_name, folder_path):
    """
    Waits indefinitely until a file with the given base name (and any extension)
    appears in the specified folder.
    """
    print(f"Waiting for base file '{base_name}.*' to appear in '{folder_path}'...")
    while True:
        try:
            for file in os.listdir(folder_path):
                if os.path.splitext(file)[0] == base_name:
                    found_path = os.path.join(folder_path, file)
                    print(f"  -> Base file found: {found_path}")
                    return found_path
        except FileNotFoundError:
            print(f"  -> Error: The folder '{folder_path}' does not exist. Please check the path. Retrying...")
        except Exception as e:
            print(f"  -> An unexpected error occurred while searching for the base file: {e}. Retrying...")

        time.sleep(10)


def wait_for_hdr_file(base_file_path):
    """
    Given the path to a base file, this function waits indefinitely until a
    corresponding '.hdr' file with the same base name appears.
    """
    base_name = os.path.splitext(os.path.basename(base_file_path))[0]
    folder = os.path.dirname(base_file_path)
    hdr_file_name = f"{base_name}.hdr"
    hdr_file_path = os.path.join(folder, hdr_file_name)

    print(f"Waiting for corresponding HDR file '{hdr_file_name}'...")
    while not os.path.exists(hdr_file_path):
        time.sleep(10)  # Check every 10 seconds

    print(f"  -> HDR file found: {hdr_file_path}")


def switch_to_desktop(desktop_index):
    """
    Switches to the specified virtual desktop (0-indexed).
    It first resets to Desktop 1, then moves right to the target.
    """
    print(f"Switching to Virtual Desktop {desktop_index + 1}...")

    # Reset to the far-left desktop (Desktop 1) to have a known starting point.
    print("  -> Resetting to Desktop 1...")
    for _ in range(len(FILE_NAMES_TO_MONITOR) + 1):
        pyautogui.hotkey('ctrl', 'win', 'left')
        time.sleep(0.1)

    time.sleep(0.5)  # Give the UI a moment to settle

    # Move right to the target desktop.
    if desktop_index > 0:
        print(f"  -> Moving right {desktop_index} time(s)...")
        for _ in range(desktop_index):
            pyautogui.hotkey('ctrl', 'win', 'right')
            time.sleep(0.5)  # Allow time for the desktop switch animation

    print("  -> Switched to the correct desktop.")
    time.sleep(1)  # Final pause to ensure the new desktop is fully active


def start_next_task():
    """
    Performs the keyboard inputs to start the next data processing task.
    """
    print("Automating keyboard input to start the next process...")
    try:
        # Press Tab 4 times
        for i in range(4):
            pyautogui.press('tab')
            print(f"  -> Pressed 'Tab' ({i + 1}/4)")
            time.sleep(0.25)

        # Press Space bar
        pyautogui.press('space')
        print("  -> Pressed 'Space'.")
        print("Process initiated successfully.")
    except Exception as e:
        print(f"An error occurred during keyboard automation: {e}")


def main():
    """
    Main function to run the automation loop.
    """
    if not INPUT_FOLDER_PATH or not FILE_NAMES_TO_MONITOR:
        print("Error: 'INPUT_FOLDER_PATH' or 'FILE_NAMES_TO_MONITOR' is not configured. Please update the script.")
        return

    # --- Startup delay to allow you to switch focus from the IDE/terminal ---
    print("--- Starting Automation in 5 seconds... ---")
    print(">>> Click away from the PyCharm window now! <<<")
    for i in range(5, 0, -1):
        print(f"{i}...", end="", flush=True)
        time.sleep(1)
    print("\nStarting automation process!")

    num_files = len(FILE_NAMES_TO_MONITOR)

    # Loop through the files using an index
    for current_file_index in range(num_files):
        # --- Step 1: Define the current file to monitor ---
        current_base_name = FILE_NAMES_TO_MONITOR[current_file_index]

        print("\n" + "=" * 60)
        print(f"CYCLE START: Monitoring for Desktop {current_file_index + 1} (File: {current_base_name})")
        print("=" * 60)

        # --- Step 2: Wait for the base file, then its .hdr counterpart ---
        found_base_file = wait_for_file(current_base_name, INPUT_FOLDER_PATH)
        wait_for_hdr_file(found_base_file)

        # --- Step 3: Check if this is the last file in the list ---
        # This is the new logic to end the script.
        if current_file_index == num_files - 1:
            print("\n" + "*" * 60)
            print(f"SUCCESS: Final HDR file '{current_base_name}.hdr' found.")
            print("Automation task is complete. Script will now terminate.")
            print("*" * 60)
            break  # Exit the loop
        else:
            # --- If not the last file, proceed to the next desktop ---
            next_desktop_index = current_file_index + 1

            # --- Step 4: Switch to the next virtual desktop ---
            switch_to_desktop(next_desktop_index)

            # --- Step 5: Start the process on the new desktop ---
            start_next_task()

            print(f"--- Cycle complete. Moving to next item in the list. ---")


if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    main()
    print("\nScript finished.")