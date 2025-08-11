import matplotlib.pyplot as plt

# Absorption wavelengths (µm) for each mineral
minerals = {
    "Biotite": [1.4, 2.2, 2.35],
    "Calcite": [2.34, 2.54],
    "Dolomite": [2.33, 2.52],
    "Magnesite": [2.3, 2.5],
    "Smithsonite": [2.34, 2.57],
    "Monazite": [0.59, 0.745, 0.8, 0.86],
    "Magnetite": [1.0],
    "Hematite": [0.535, 0.65, 0.86],
    "Ancylite": [0.745, 0.8, 0.86, 2.33],
    "Apatite": [0.9, 2.2],
    "Laterite": [0.92, 2.2],
    "Ankerite": [1.36, 2.34],
    "Siderite": [1.0, 2.35],
    "Carbonatite (rock)": [0.8, 2.33, 2.5],
}

# Flatten and convert to nanometers
wavelengths_nm = [wl * 1000 for wls in minerals.values() for wl in wls]

# Define VNIR and SWIR ranges (nm)
vnir_range = (398.42, 1001.57)
swir_range = (891.28, 2505.39)

# Plot histogram
fig, ax = plt.subplots()
counts, bins, patches = ax.hist(wavelengths_nm, bins=150)

# Draw vertical lines for VNIR and SWIR extents
ax.axvline(vnir_range[0], linestyle='--')
ax.axvline(vnir_range[1], linestyle='--')
ax.axvline(swir_range[0], linestyle='--')
ax.axvline(swir_range[1], linestyle='--')

# Annotate regions
ymax = max(counts) * 1.05
ax.set_ylim(0, ymax)
ax.text((vnir_range[0] + vnir_range[1]) / 2, ymax * 0.9, "VNIR", ha='center', va='center')
ax.text((swir_range[0] + swir_range[1]) / 2, ymax * 0.9, "SWIR", ha='center', va='center')

# Labels
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Count (# wavelengths per bin)")
ax.set_title("Histogram of Mineral Absorption Wavelengths")

plt.show()

