import xarray as xr
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from datetime import datetime
import math


def parse_stitchnodes_txt(filepath):
    tracks = []
    current_track_id = 0
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            if parts[0] == 'start':
                current_track_id += 1
            else:
                i, j, lon, lat, value, y, m, d, h = parts
                time = datetime(int(y), int(m), int(d), int(h))
                tracks.append({
                    'track_id': current_track_id,
                    'time': time,
                    'lon': float(lon),
                    'lat': float(lat),
                    'value': float(value)
                })
    return pd.DataFrame(tracks)


def load_dataset(ds_path):
    try:
        return xr.open_dataset(ds_path)
    except FileNotFoundError:
        print(f"Dataset not found at {ds_path}. Please check the path.")
        return None


def latlon_to_cartesian(lat, lon):
    """Convert lat/lon (deg) to 3D Cartesian coords on unit sphere."""
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    x = np.cos(lat_rad) * np.cos(lon_rad)
    y = np.cos(lat_rad) * np.sin(lon_rad)
    z = np.sin(lat_rad)
    return np.column_stack((x, y, z))


def build_object_tree(ds, time_idx, var_name="binary_tag"):
    """Build KD-tree of frontal objects at a given time in Cartesian coords."""
    mask = ds[var_name].isel(time=time_idx).values > 0
    if not np.any(mask):
        return None

    lats = ds['latitude'].values
    lons = ds['longitude'].values
    points = np.column_stack(np.where(mask))
    coords = np.array([[lats[y], lons[x]] for y, x in points])

    coords_cart = latlon_to_cartesian(coords[:, 0], coords[:, 1])
    return cKDTree(coords_cart)


def check_frontal_proximity(time_val, frt_ds, pv_df, radius_deg=0.5):
    """
    Check if each circulation point is within radius_deg great-circle degrees
    of a frontal object at a given time using KD-tree in Cartesian space.
    """
    try:
        frt_time_idx = np.where(frt_ds.time.values == np.datetime64(time_val))[0][0]
    except IndexError:
        return pd.Series(False, index=pv_df.index)

    frt_tree = build_object_tree(frt_ds, frt_time_idx, var_name="binary_tag")
    if frt_tree is None:
        return pd.Series(False, index=pv_df.index)

    # Convert PV node positions to Cartesian
    pts_cart = latlon_to_cartesian(pv_df['lat'].values, pv_df['lon'].values)

    # Convert angular radius (degrees) ? chord distance on unit sphere
    radius_rad = np.radians(radius_deg)
    chord_dist = 2 * np.sin(radius_rad / 2.0)

    near_front = np.array([len(frt_tree.query_ball_point(pt, chord_dist)) > 0 for pt in pts_cart])
    return pd.Series(near_front, index=pv_df.index)


def main():
    print("="*50)
    print("Checking proximity of stitched nodes to frontal objects (great-circle with KD-tree)...")
    print("="*50)

    # File paths
    FRONTAL_FILE = "/cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/merged_frt.nc"
    PV_FILE = "/cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/stitch_nodes/pv_objects/pv_ivt_objects_stitch_paths.txt"

    frt_ds = load_dataset(FRONTAL_FILE)
    pv_df = parse_stitchnodes_txt(PV_FILE)

    if frt_ds is None or pv_df is None:
        print("Error loading files.")
        return

    frt_times = pd.to_datetime(frt_ds.time.values)
    pv_df = pv_df[pv_df["time"].isin(frt_times)]

    # Initialize output column
    pv_df['near_front'] = False
    for time_val, group in pv_df.groupby('time'):
        results = check_frontal_proximity(time_val, frt_ds, group, radius_deg=0.5)
        pv_df.loc[group.index, "near_front"] = results

    pv_df.to_csv("pv_nodes_fronts.csv", index=False)

    print("="*50)
    print("Script complete! Saved results to pv_nodes_fronts.csv")
    print("="*50)


if __name__ == "__main__":
    main()
