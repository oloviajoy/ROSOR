import os
import time
from qgis.core import QgsVectorLayer, QgsProject, QgsFeature
import processing
from datetime import datetime

# Set your paths here
input_folder = r"D:\re-process_test"  # Update as needed
output_folder = r"D:\re-process_test_ouput_50"  # Update as needed

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Get all .shp files in the input folder
shp_files = [f for f in os.listdir(input_folder) if f.endswith('.shp')]

# Function to format time
def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{seconds:.2f}"

# Main processing loop
total_start_time = time.time()
total_files = len(shp_files)
processed_files = 0

for i, shp_file in enumerate(shp_files, 1):
    file_start_time = time.time()
    print(f"\nProcessing file {i}/{total_files}: {shp_file}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Load the original file
    input_path = os.path.join(input_folder, shp_file)
    load_start = time.time()
    original_layer = QgsVectorLayer(input_path, "original", "ogr")
    load_time = time.time() - load_start
    
    if not original_layer.isValid():
        print(f"× Failed to load layer: {shp_file} (took {format_time(load_time)})")
        continue
    
    print(f"✓ Layer loaded. Feature count: {original_layer.featureCount()} (took {format_time(load_time)})")
    
    try:
        # 2. Delete holes
        print("Step 1/5: Deleting holes...")
        step_start = time.time()
        layer_a = processing.run("native:deleteholes", {
            'INPUT': original_layer,
            'MIN_AREA': 0.0,
            'OUTPUT': 'memory:'
        })['OUTPUT']
        step_time = time.time() - step_start
        print(f"✓ Result feature count: {layer_a.featureCount()} (took {format_time(step_time)})")
        
                # 3. Keep largest N parts
        print("Step 2/5: Keeping top 10 largest parts...")
        step_start = time.time()
        N = 50  # Number of parts to keep

        # First convert to singlepart
        singlepart = processing.run("native:multiparttosingleparts", {
            'INPUT': layer_a,
            'OUTPUT': 'memory:'
        })['OUTPUT']

        # Get all features with their areas
        features_with_areas = []
        for feature in singlepart.getFeatures():
            geom = feature.geometry()
            features_with_areas.append((feature, geom.area()))

        if not features_with_areas:
            print("! Warning: No features found after singlepart conversion")
            layer_b = singlepart  # fallback to original
        else:
            # Sort features by area descending and keep top N
            features_with_areas.sort(key=lambda x: x[1], reverse=True)
            top_features = [fa[0] for fa in features_with_areas[:N]]

            # Create new memory layer with top N features
            layer_b = QgsVectorLayer("Polygon?crs=" + singlepart.crs().authid(), "top_parts", "memory")
            layer_b_data = layer_b.dataProvider()
            layer_b_data.addAttributes(singlepart.fields())
            layer_b.updateFields()
            layer_b_data.addFeatures(top_features)
            layer_b.updateExtents()

            print(f"✓ Kept {len(top_features)} largest parts.")
            if len(features_with_areas) > N:
                print(f"Discarded {len(features_with_areas)-N} smaller parts")
                print(f"Smallest kept area: {features_with_areas[N-1][1]:.2f} sq units")

        step_time = time.time() - step_start
        print(f"✓ Result feature count: {layer_b.featureCount()} (took {format_time(step_time)})")

        
        # 4. Simplify with tolerance = 10
        print("Step 3/5: Simplifying...")
        step_start = time.time()
        layer_c = processing.run("native:simplifygeometries", {
            'INPUT': layer_b,
            'METHOD': 0,
            'TOLERANCE': 10,
            'OUTPUT': 'memory:'
        })['OUTPUT']
        step_time = time.time() - step_start
        print(f"✓ Result feature count: {layer_c.featureCount()} (took {format_time(step_time)})")
        
        # 5. Buffer with distance = 25m, miter join
        print("Step 4/5: Buffering...")
        step_start = time.time()
        layer_d = processing.run("native:buffer", {
            'INPUT': layer_c,
            'DISTANCE': 25,
            'SEGMENTS': 5,
            'END_CAP_STYLE': 0,
            'JOIN_STYLE': 2,
            'MITER_LIMIT': 2,
            'DISSOLVE': False,
            'OUTPUT': 'memory:'
        })['OUTPUT']
        step_time = time.time() - step_start
        print(f"✓ Result feature count: {layer_d.featureCount()} (took {format_time(step_time)})")
        
        # 6. Save final output
        print("Step 5/5: Saving result...")
        step_start = time.time()
        output_path = os.path.join(output_folder, shp_file)
        
        # Brief pause to release any file handles
        time.sleep(1)  
        
        # Remove existing files if they exist
        for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg']:
            file_to_remove = output_path.replace('.shp', ext)
            if os.path.exists(file_to_remove):
                try:
                    os.remove(file_to_remove)
                except PermissionError:
                    print(f"! Could not remove {file_to_remove} - skipping overwrite")
                    continue
        
        processing.run("native:savefeatures", {
            'INPUT': layer_d,
            'OUTPUT': output_path,
            'FILE_ENCODING': 'UTF-8'
        })
        step_time = time.time() - step_start
        print(f"✓ Successfully saved: {shp_file} (took {format_time(step_time)})")
        
        processed_files += 1
        file_time = time.time() - file_start_time
        print(f"✔ Completed processing {shp_file} in {format_time(file_time)}")
        
    except Exception as e:
        file_time = time.time() - file_start_time
        print(f"! Processing failed after {format_time(file_time)}: {str(e)}")
        continue

total_time = time.time() - total_start_time
print(f"\nProcessing summary:")
print(f"Successfully processed {processed_files} of {total_files} files")
print(f"Total processing time: {format_time(total_time)}")
print(f"Average time per file: {format_time(total_time/max(1, processed_files))}")