import os
import numpy as np
from osgeo import gdal

def tiff_to_rockveg_grayscale(input_tif,
                              target_wls=(551.413330, 681.534497, 741.319898),
                              vnir_range=(398.42, 1001.57)):
    """
    Loads a VNIR hyperspectral TIFF, extracts three wavelengths (nm) for
    green, red, and red-edge, computes a combined rock-vs-veg index,
    and writes a single-band GeoTIFF next to the input with
    '_rock_bright_veg_dark.tif' appended.
    """
    # Enable GDAL exceptions
    gdal.UseExceptions()

    # Open the TIFF
    ds = gdal.Open(input_tif, gdal.GA_ReadOnly)
    n_bands = ds.RasterCount
    xsize = ds.RasterXSize
    ysize = ds.RasterYSize

    # Compute band spacing (assuming evenly spaced wavelengths)
    first_wl, last_wl = vnir_range
    spacing = (last_wl - first_wl) / (n_bands - 1)

    # Map wavelength (nm) to 1-based GDAL band index
    def wl_to_band(wl):
        idx = int(round((wl - first_wl) / spacing)) + 1
        return max(1, min(n_bands, idx))

    # Read the three bands
    b_g  = ds.GetRasterBand(wl_to_band(target_wls[0])).ReadAsArray().astype(np.float32)
    b_r  = ds.GetRasterBand(wl_to_band(target_wls[1])).ReadAsArray().astype(np.float32)
    b_re = ds.GetRasterBand(wl_to_band(target_wls[2])).ReadAsArray().astype(np.float32)
    ds = None

    # Compute two normalized-difference indices
    eps = 1e-6
    grr  = (b_g  - b_r)  / (b_g  + b_r  + eps)   # green-red ratio
    revi = (b_re - b_r)  / (b_re + b_r  + eps)   # red-edge veg index

    # Combine indices: veg bright → low rock value; invert so rock→bright
    combined = 0.5 * (grr + revi)
    mn, mx = combined.min(), combined.max()
    norm = ((combined - mn) / (mx - mn) * 255).astype(np.uint8)
    rock_bright = 255 - norm

    # Build output path next to input, appending suffix
    base, ext = os.path.splitext(input_tif)
    output_tif = f"{base}_rock_bright_veg_dark.tif"

    # Write out as GeoTIFF
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(output_tif, xsize, ysize, 1, gdal.GDT_Byte)
    out_ds.GetRasterBand(1).WriteArray(rock_bright)
    out_ds.FlushCache()
    out_ds = None

    print(f"Saved rock‐bright grayscale to:\n  {output_tif}")

# Example usage
input_path = r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC\0702\T1_VNIR\TECK_T1_F1_F2_2025_07_02_17_38_03_042\raw_104858.tif"
tiff_to_rockveg_grayscale(input_path)
