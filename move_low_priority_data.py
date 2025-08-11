import os
import shutil

# --- User Inputs ---
input_root_folder = r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC"  # <-- change this
output_folder = r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\move to local drive"   # <-- change this

# --- List of folder names to move ---
target_names = [
    "100165_TECK_T6_F11_F12_2025_06_30_23_19_45",
    "100210_TECK_T6_F13_F14_2025_07_02_23_09_12",
    "100417_TECK_T6_F15_F16_2025_07_11_17_29_10",
    "100212_TECK_T6_F17_2025_07_02_23_32_38",
    "100157_TECK_T6_F4_2025_06_30_20_26_59",
    "100410_TECK_T6_F5_F6_2025_07_11_16_25_55",
    "100316_TECK_T6_F7_F8_2025_07_07_15_20_34",
    "100413_TECK_T6_F9_F10_2025_07_11_16_47_55",
    "100126_TECK_T4_F1_2025_06_29_22_12_07",
    "100472_TECK_T4_F1_2025_07_14_17_23_34",
    "100421_TECK_T4_F13_F14_2025_07_11_21_08_56",
    "100128_TECK_T4_F2_2025_06_29_22_28_53",
    "100130_TECK_T4_F4_F5_2025_06_29_22_45_59",
    "100136_TECK_T4_F6_2025_06_29_23_17_50",
    "100425_TECK_T4_F6_2025_07_11_21_30_27",
    "100147_TECK_T4_F7_F8_2025_06_30_18_05_48",
    "100149_TECK_T4_F9_F10_2025_06_30_18_23_14",
    "100428_TECK_T4_F9_F10_2025_07_11_21_49_52"


]

# --- Script ---
def move_matching_folders(input_root, output_root, folder_names):
    os.makedirs(output_root, exist_ok=True)

    for dirpath, dirnames, _ in os.walk(input_root):
        for dirname in dirnames:
            if dirname in folder_names:
                src_path = os.path.join(dirpath, dirname)
                dest_path = os.path.join(output_root, dirname)

                # Avoid overwriting existing folders
                if not os.path.exists(dest_path):
                    print(f"Moving: {src_path} --> {dest_path}")
                    shutil.move(src_path, dest_path)
                else:
                    print(f"Skipped (already exists): {dest_path}")

move_matching_folders(input_root_folder, output_folder, target_names)
