import os, uuid, time
from qgis.core import QgsProcessingFeedback, QgsVectorLayer, QgsProject
import processing

inputroot = r"E:\hyspex_shp_files\sept_15_flt_2_new"
output_root = r"E:\hyspex_shp_files\output_3"

os.makedirs(output_root, exist_ok=True)
fb = QgsProcessingFeedback()

def safe_name(path):
    return os.path.splitext(os.path.basename(path))[0].replace(" ", "_")

def clean_temp_files(base_path, max_retries=3):
    """Safely remove temporary shapefile components with retries"""
    extensions = ['.shp', '.shx', '.dbf', '.prj', '.cpg']
    for ext in extensions:
        temp_file = base_path.replace('.shp', ext)
        if os.path.exists(temp_file):
            for attempt in range(max_retries):
                try:
                    os.remove(temp_file)
                    break
                except PermissionError:
                    if attempt == max_retries - 1:
                        print(f"⚠ Could not delete temporary file {temp_file}")
                    else:
                        time.sleep(0.1)

for dirpath, dirnames, files in os.walk(inputroot):
    for fname in files:
        if not fname.lower().endswith(".bsq"):
            continue

        raster_path = os.path.join(dirpath, fname)
        out_path = os.path.join(output_root, safe_name(fname) + ".shp")
        
        if os.path.exists(out_path):
            out_path = os.path.join(
                output_root,
                f"{safe_name(fname)}_{uuid.uuid4().hex[:6]}.shp"
            )

        print(f"▶ Processing {raster_path}")

        # Step 1: Polygonize to temporary file
        temp_poly_path = os.path.join(output_root, f"temp_poly_{uuid.uuid4().hex[:8]}.shp")
        processing.run(
            "gdal:polygonize",
            {
                "INPUT": raster_path,
                "BAND": 1,
                "FIELD": "DN",
                "EIGHT_CONNECTEDNESS": False,
                "EXTRA": "",
                "OUTPUT": temp_poly_path
            },
            feedback=fb
        )

        # Step 2: Load and validate
        poly_layer = QgsVectorLayer(temp_poly_path, "temp_poly", "ogr")
        if not poly_layer.isValid():
            print(f"⚠ Failed to load polygonized layer for {fname}")
            clean_temp_files(temp_poly_path)
            continue

        if poly_layer.featureCount() == 0:
            print(f"⚠ No features created from {fname}, skipping")
            clean_temp_files(temp_poly_path)
            continue

        # Step 3: Filter by area (<= 4 m²)
        temp_filtered_path = os.path.join(output_root, f"temp_filtered_{uuid.uuid4().hex[:8]}.shp")
        processing.run(
            "native:extractbyexpression",
            {
                "INPUT": temp_poly_path,
                "EXPRESSION": "$area <= 4",
                "OUTPUT": temp_filtered_path
            },
            feedback=fb
        )

        # Clean up polygonized temp file immediately
        clean_temp_files(temp_poly_path)

        # Step 4: Dissolve remaining features
        processing.run(
            "native:dissolve",
            {
                "INPUT": temp_filtered_path,
                "FIELD": [],  # Dissolve all features together
                "OUTPUT": out_path
            },
            feedback=fb
        )

        # Clean up filtered temp file
        clean_temp_files(temp_filtered_path)

        # Verify final output
        if os.path.exists(out_path):
            final_layer = QgsVectorLayer(out_path, "result", "ogr")
            if final_layer.isValid():
                print(f"✓ Saved output with {final_layer.featureCount()} features ➜ {out_path}")
            else:
                print(f"⚠ Final output is invalid for {fname}")
            del final_layer
        else:
            print(f"⚠ Failed to create output for {fname}")

print("Processing complete.")