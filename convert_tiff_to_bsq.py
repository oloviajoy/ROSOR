import os
from qgis.core import QgsApplication
from osgeo import gdal

# Input TIFF file path (update this if needed)
input_tiff = r"D:\question mark\convert\sept_15_aurora_3_new_09_VNIR_1800_SN0933_raw_rad_bsq_float32_atm_polish_geo.tiff"

# Output BSQ path (change as needed)
output_bsq = os.path.splitext(input_tiff)[0] + ".bsq"

# GDAL translation to ENVI format (BSQ interleave by default)
gdal.Translate(
    output_bsq,
    input_tiff,
    format='ENVI'
)

print(f"Conversion complete.\nOutput file: {output_bsq}")