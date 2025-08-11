from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsLayerTreeGroup
)
from qgis.PyQt.QtCore import QUrl, QUrlQuery
import os

def load_csvs_preserve_structure(
    base_folder: str,
    delimiter: str = ',',
    x_field: str = 'lon',
    y_field: str = 'lat',
    crs: str = 'EPSG:4326',
    collapse_lowest: bool = False
):
    """
    Loads all CSVs under base_folder into QGIS, mirroring the folder tree
    as nested legend groups.

    :param base_folder: root directory to scan for .csv files
    :param delimiter:   CSV delimiter (default ',')
    :param x_field:     name of the longitude column (default 'lon')
    :param y_field:     name of the latitude column (default 'lat')
    :param crs:         layer CRS (default 'EPSG:4326')
    :param collapse_lowest: if True, each leaf group is collapsed in the legend
    """
    # 1) find all CSV files named "cube_coords.csv"
    csv_paths = []
    for root, dirs, files in os.walk(base_folder):
        for fname in files:
            # only load files named exactly "cube_coords.csv" (case‑insensitive)
            if fname.lower() == 'cube_coords.csv':
                csv_paths.append(os.path.join(root, fname))
    if not csv_paths:
        print("No cube_coords.csv found under", base_folder)
        return

    # 2) set up top‐level group
    root_grp = QgsProject.instance().layerTreeRoot()
    top_name = os.path.basename(os.path.normpath(base_folder))
    top_group = QgsLayerTreeGroup(top_name)
    root_grp.insertChildNode(0, top_group)

    def get_or_create_group(parent: QgsLayerTreeGroup, name: str) -> QgsLayerTreeGroup:
        for child in parent.children():
            if isinstance(child, QgsLayerTreeGroup) and child.name() == name:
                return child
        grp = QgsLayerTreeGroup(name)
        parent.insertChildNode(-1, grp)
        return grp

    # 3) load each CSV into the appropriate subgroup
    for path in csv_paths:
        rel = os.path.relpath(path, base_folder)
        parts = rel.split(os.sep)
        *subdirs, fname = parts

        parent = top_group
        for sub in subdirs:
            parent = get_or_create_group(parent, sub)

        layer_name = os.path.splitext(fname)[0]

        # build the delimited‐text URI
        url = QUrl.fromLocalFile(path)
        query = QUrlQuery()
        query.addQueryItem('delimiter', delimiter)
        query.addQueryItem('xField', x_field)
        query.addQueryItem('yField', y_field)
        query.addQueryItem('crs', crs)
        url.setQuery(query)
        uri = url.toString(QUrl.FullyEncoded)

        layer = QgsVectorLayer(uri, layer_name, 'delimitedtext')
        if not layer.isValid():
            print("⚠️ Failed to load CSV:", path)
            continue

        QgsProject.instance().addMapLayer(layer, False)
        parent.addLayer(layer)
        if collapse_lowest:
            parent.setExpanded(False)

    print("✅ Done loading CSVs into QGIS under group:", top_name)

# Example usage:
load_csvs_preserve_structure(
    r"Y:\TECK_WHITE_EARTH\TECK_HYPERSPEC",
    collapse_lowest=True
)
