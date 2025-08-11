

import os
import shutil # For copying files
from qgis.core import (
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QgsApplication,
    QgsUnitTypes # <--- ENSURE THIS IS IMPORTED
)
import processing # QGIS processing framework

# --- USER: SET THESE PATHS ---
input_folder_path = r"D:\the good\fixed-took forever"  # Replace with the actual path to your folder of shapefiles
output_folder_base = r"D:\output\output_2000N_dissolve_simplify50_buffered_MORE_buff_buff_last_one" # Replace with where you want the new folders and files to be created

# --- BUFFER PARAMETERS ---
buffer_distance = 10.0  # Buffer distance (in the units of the shapefile's CRS)
buffer_join_style = 1   # 0 for Round, 1 for Miter, 2 for Bevel
buffer_miter_limit = 2.0 # Default Miter limit

# --- DERIVED PATHS ---
copied_shapefiles_folder = os.path.join(output_folder_base, "copied_shapefiles")
buffered_shapefiles_folder = os.path.join(output_folder_base, "buffered_shapefiles")

# --- SCRIPT START ---
print("Script started...")

# Ensure QGIS processing is initialized (good practice, though usually fine in console)
# QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms()) # May not be needed in console

# 1. Create output directories if they don't exist
try:
    os.makedirs(copied_shapefiles_folder, exist_ok=True)
    os.makedirs(buffered_shapefiles_folder, exist_ok=True)
    print(f"Created/ensured output folder for copies: {copied_shapefiles_folder}")
    print(f"Created/ensured output folder for buffered files: {buffered_shapefiles_folder}")
except OSError as e:
    print(f"Error creating output directories: {e}")
    # Consider exiting or handling

# 2. Find and copy shapefiles and their components
copied_shp_details = [] # Will store tuples of (original_name, copied_path)
if not os.path.isdir(input_folder_path):
    print(f"Error: Input folder '{input_folder_path}' does not exist or is not a directory.")
else:
    print(f"\n--- Copying Shapefiles from '{input_folder_path}' to '{copied_shapefiles_folder}' ---")
    for item_name in os.listdir(input_folder_path):
        if item_name.lower().endswith(".shp"):
            base_name, _ = os.path.splitext(item_name)
            output_shp_path_in_copied_folder = os.path.join(copied_shapefiles_folder, item_name)
            
            print(f"Processing original shapefile: {item_name}")
            
            # Copy all components
            copied_components_ext = []
            has_shp = False
            has_prj = False
            for ext_item_name in os.listdir(input_folder_path):
                current_base_name, current_ext = os.path.splitext(ext_item_name)
                if current_base_name.lower() == base_name.lower(): # Match base name case-insensitively
                    source_file = os.path.join(input_folder_path, ext_item_name)
                    destination_file = os.path.join(copied_shapefiles_folder, ext_item_name)
                    try:
                        shutil.copy2(source_file, destination_file)
                        copied_components_ext.append(current_ext.lower())
                        if current_ext.lower() == ".shp":
                            has_shp = True
                        if current_ext.lower() == ".prj":
                            has_prj = True
                    except Exception as e:
                        print(f"  Error copying component {ext_item_name}: {e}")
            
            if has_shp:
                copied_shp_details.append((item_name, output_shp_path_in_copied_folder))
                print(f"  Successfully copied '{item_name}'. Components copied (extensions): {', '.join(copied_components_ext)}")
                if not has_prj:
                    print(f"  WARNING: No .prj file found or copied for '{item_name}'. CRS issues are likely.")
            else:
                print(f"  Warning: Main .shp file for '{item_name}' was not copied.")

if not copied_shp_details:
    print("\nNo shapefiles were successfully copied. Exiting buffer process.")
else:
    print(f"\n--- Buffering {len(copied_shp_details)} Copied Shapefiles ---")
    # 3. Batch process: Buffer the copied shapefiles
    for original_name, copied_shp_path in copied_shp_details:
        shp_filename = os.path.basename(copied_shp_path) # This is same as original_name here
        base_name, _ = os.path.splitext(shp_filename)
        
        print(f"\n--- Preparing to buffer: {shp_filename} ---")
        print(f"  Path to copied .shp: {copied_shp_path}")

        # --- VALIDATION STEP for the copied layer ---
        layer_to_buffer = QgsVectorLayer(copied_shp_path, base_name + "_temp_check", "ogr")

        if not layer_to_buffer.isValid():
            print(f"  ERROR: Copied layer '{shp_filename}' from path '{copied_shp_path}' is NOT VALID. Skipping buffer.")
            continue 

        feature_count = layer_to_buffer.featureCount()
        print(f"  Layer loaded. Feature count: {feature_count}")
        if feature_count == 0:
            print(f"  WARNING: Copied layer '{shp_filename}' has 0 features. Buffering will likely result in an empty layer.")

        crs = layer_to_buffer.crs()
        if crs.isValid():
            print(f"  Layer CRS: {crs.authid()} - {crs.description()}")
            if crs.isGeographic():
                print(f"  CRITICAL WARNING: Layer '{shp_filename}' has a GEOGRAPHIC CRS ({crs.authid()}).")
                print(f"                   Buffer distance of {buffer_distance} will be in DEGREES.")
                print(f"                   This is usually NOT what you want and can lead to very large or invalid buffers.")
                print(f"                   Please ensure your data is in a PROJECTED CRS for meaningful distance buffering.")
                # print("                   Skipping buffer for this geographic layer.")
                # continue
            else: # Projected CRS
                # Get map units as string
                map_units_enum = crs.mapUnits()
                map_units_str = "Unknown"
                if map_units_enum == QgsUnitTypes.DistanceUnit.Meters:
                    map_units_str = "Meters"
                elif map_units_enum == QgsUnitTypes.DistanceUnit.Feet:
                    map_units_str = "Feet"
                elif map_units_enum == QgsUnitTypes.DistanceUnit.NauticalMiles:
                    map_units_str = "Nautical Miles"
                elif map_units_enum == QgsUnitTypes.DistanceUnit.Kilometers:
                    map_units_str = "Kilometers"
                elif map_units_enum == QgsUnitTypes.DistanceUnit.Yards:
                    map_units_str = "Yards"
                elif map_units_enum == QgsUnitTypes.DistanceUnit.Miles:
                    map_units_str = "Miles"
                elif map_units_enum == QgsUnitTypes.DistanceUnit.Degrees: 
                    map_units_str = "Degrees (from mapUnits, unusual for projected)"
                else:
                    map_units_str = f"Unit enum value: {map_units_enum} (Refer to QgsUnitTypes.DistanceUnit)"
                
                print(f"  Layer has a Projected CRS. Buffer units: {map_units_str}")
        else:
            print(f"  CRITICAL WARNING: Layer '{shp_filename}' has an INVALID OR UNKNOWN CRS. Buffering is highly likely to fail or produce incorrect results. Skipping.")
            continue
        
        extent = layer_to_buffer.extent()
        print(f"  Layer extent: {extent.toString()}")
        if extent.width() == 0 and extent.height() == 0 and feature_count > 0 :
             print(f"  WARNING: Layer '{shp_filename}' has 0 width and 0 height extent, but {feature_count} features. This is unusual and might indicate issues.")
        
        # --- End of VALIDATION STEP ---

        output_buffered_shp_name = f"{base_name}.shp"
        output_buffered_shp_path = os.path.join(buffered_shapefiles_folder, output_buffered_shp_name)
        
        print(f"  Proceeding with buffer for: {shp_filename}")
        print(f"  Buffer output will be: {output_buffered_shp_path}")
        
        buffer_params = {
            'INPUT': copied_shp_path,
            'DISTANCE': buffer_distance,
            'SEGMENTS': 8,
            'END_CAP_STYLE': 0, 
            'JOIN_STYLE': buffer_join_style,
            'MITER_LIMIT': buffer_miter_limit,
            'DISSOLVE': False,
            'OUTPUT': output_buffered_shp_path
        }
        
        try:
            result = processing.run("native:buffer", buffer_params)
            if result and result.get('OUTPUT'):
                print(f"  Successfully buffered. Output saved to: {result['OUTPUT']}")
            else:
                print(f"  Buffer process for '{shp_filename}' ran, but no output path in result or result is None. Check logs and parameters.")
        except Exception as e:
            print(f"  ERROR during buffering of {shp_filename}: {e}")
            import traceback
            print("Traceback:")
            traceback.print_exc()


print("\nScript finished.")