

import os
import time
import pyautogui
# ==============================================================================
# --- CONFIGURATION ---
# ==============================================================================
PROCESSING_STAGES = [
    {
        "folder_path": r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\0702\T6_VNIR\TECK_T6_F13_F14_2025_07_02_23_08_55_592\deliverables",
        "file_names": [
            "VNIR_T6_F13_F14_956",
            "VNIR_T6_F13_F14_317",
        ],
    },
    {
        "folder_path": r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\0630\T6_VNIR\TECK_T6_F11_F12_2025_06_30_23_19_28_380\deliverables",
        "file_names": [
            "VNIR_T6_F11_F12_255",
            "VNIR_T6_F11_F12_568",
            "VNIR_T6_F11_F12_700",
        ],
    },
    {
        "folder_path": r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\0629\T4_VNIR\TECK_T4_F6_2025_06_29_23_17_33_824\deliverables",
        "file_names": [
            "VNIR_T4_F6_622",
            "VNIR_T4_F6_036",
        ],
    },
]



# ==============================================================================
# --- SCRIPT START ---
# ==============================================================================

def wait_for_file(base_name, folder_path):
    """Waits for a file with the given base name to appear."""
    print(f"Waiting for base file '{base_name}.*' in '{folder_path}'...")
    while True:
        try:
            for file in os.listdir(folder_path):
                if os.path.splitext(file)[0] == base_name:
                    found_path = os.path.join(folder_path, file)
                    print(f"  -> Base file found: {found_path}")
                    return found_path
        except FileNotFoundError:
            print(f"  -> Error: Folder '{folder_path}' not found. Retrying...")
        except Exception as e:
            print(f"  -> An error occurred while searching for the base file: {e}. Retrying...")
        time.sleep(10)


def wait_for_hdr_file(base_file_path):
    """Waits for a corresponding '.hdr' file to appear."""
    base_name = os.path.splitext(os.path.basename(base_file_path))[0]
    folder = os.path.dirname(base_file_path)
    hdr_file_name = f"{base_name}.hdr"
    hdr_file_path = os.path.join(folder, hdr_file_name)

    print(f"Waiting for corresponding HDR file '{hdr_file_name}'...")
    while not os.path.exists(hdr_file_path):
        time.sleep(10)

    print(f"  -> HDR file found: {hdr_file_path}")


def switch_to_desktop(desktop_index, total_desktops):
    """Switches to the specified virtual desktop, resetting first."""
    print(f"Switching to Virtual Desktop {desktop_index + 1}...")

    print("  -> Resetting to Desktop 1...")
    # Press left enough times to guarantee reaching the first desktop
    for _ in range(total_desktops + 2):
        pyautogui.hotkey('ctrl', 'win', 'left')
        time.sleep(0.1)

    time.sleep(0.5)

    if desktop_index > 0:
        print(f"  -> Moving right {desktop_index} time(s)...")
        for _ in range(desktop_index):
            pyautogui.hotkey('ctrl', 'win', 'right')
            time.sleep(0.5)

    print("  -> Switched to the correct desktop.")
    time.sleep(1)


def start_next_task():
    """Simulates keyboard input to start the next process."""
    print("Automating keyboard input...")
    try:
        for i in range(4):
            pyautogui.press('tab')
            print(f"  -> Pressed 'Tab' ({i + 1}/4)")
            time.sleep(0.25)

        pyautogui.press('space')
        print("  -> Pressed 'Space'.")
        print("Process initiated successfully.")
    except Exception as e:
        print(f"An error occurred during keyboard automation: {e}")


def main():
    """Main function to run the multi-stage automation loop."""
    if not PROCESSING_STAGES:
        print("Error: 'PROCESSING_STAGES' is empty. Please configure at least one stage.")
        return

    # Calculate the total number of desktop slots needed for the entire run
    total_desktop_slots = sum(len(stage["file_names"]) for stage in PROCESSING_STAGES)

    print("--- Starting Automation in 5 seconds... ---")
    print(">>> Click away from the PyCharm window now! <<<")
    for i in range(5, 0, -1):
        print(f"{i}...", end="", flush=True)
        time.sleep(1)
    print("\nStarting automation process!")

    # A single counter for all desktops across all stages
    global_desktop_index = 0

    for stage_index, stage in enumerate(PROCESSING_STAGES):
        stage_number = stage_index + 1
        folder_path = stage["folder_path"]
        file_names_in_stage = stage["file_names"]

        print("\n" + "#" * 60)
        print(f"# STAGE {stage_number} of {len(PROCESSING_STAGES)} STARTED")
        print(f"# Monitoring Folder: {folder_path}")
        print("#" * 60)

        for file_index, base_name in enumerate(file_names_in_stage):

            print("\n" + "=" * 60)
            print(f"STAGE {stage_number} - FILE {file_index + 1}/{len(file_names_in_stage)}")
            print(f"Monitoring for: '{base_name}' on Desktop {global_desktop_index + 1}")
            print("=" * 60)

            found_base_file = wait_for_file(base_name, folder_path)
            wait_for_hdr_file(found_base_file)
            print(f"--- Task for '{base_name}' complete. ---")

            # Check for absolute termination condition
            is_last_task_overall = (global_desktop_index == total_desktop_slots - 1)
            if is_last_task_overall:
                print("\n" + "*" * 60)
                print(f"SUCCESS: Final HDR file for the final stage found.")
                print("Entire automation task is complete. Script will now terminate.")
                print("*" * 60)
                return  # Exit the main function and end the script

            # --- CORRECTED LOGIC ---
            # If it's not the absolute end, we MUST start the next task.
            # We simply increment our global desktop counter to move to the next slot.
            global_desktop_index += 1

            # Switch to the next desktop in the sequence and start the process
            # that will generate the next file we need to wait for.
            switch_to_desktop(global_desktop_index, total_desktop_slots)
            start_next_task()


if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    main()
    print("\nScript finished.")