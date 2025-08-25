import xarray as xr 
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from datetime import datetime


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


def build_object_tree(ds, time_idx, var_name="binary_tag"):
    """
    Build KD-tree of object locations at a given time.
    Uses `binary_tag > 0` as valid objects.
    """
    mask = ds[var_name].isel(time=time_idx).values > 0
    if not np.any(mask):
        return None

    lats = ds['latitude'].values
    lons = ds['longitude'].values
    points = np.column_stack(np.where(mask))
    coords = np.array([[lats[y], lons[x]] for y, x in points])
    return cKDTree(coords)


def build_txt_tree(df, time_val):
    df_time = df[df['time'] == time_val]
    if df_time.empty:
        return None
    coords = df_time[['lat', 'lon']].values
    return cKDTree(coords)


def check_overlap_for_time(time_val, ar_ds, frt_ds, slp_df, circ_df, radius_deg=0.25):
    """Check triple overlap and record nearest SLP value for all circulation points at one time."""
    try:
        ar_time_idx = np.where(ar_ds.time.values == np.datetime64(time_val))[0][0]
        frt_time_idx = np.where(frt_ds.time.values == np.datetime64(time_val))[0][0]
    except IndexError:
        return pd.DataFrame({
            "triple_overlap": False,
            "slp_value": np.nan
        }, index=circ_df.index)

    ar_tree = build_object_tree(ar_ds, ar_time_idx, var_name="binary_tag")
    frt_tree = build_object_tree(frt_ds, frt_time_idx, var_name="binary_tag")
    slp_time = slp_df[slp_df["time"] == time_val]

    if ar_tree is None or frt_tree is None or slp_time.empty:
        return pd.DataFrame({
            "triple_overlap": False,
            "slp_value": np.nan
        }, index=circ_df.index)

    pts = circ_df[['lat', 'lon']].values

    # Build trees
    frt_near = np.array([bool(x) for x in frt_tree.query_ball_point(pts, radius_deg)])
    ar_near  = np.array([bool(x) for x in ar_tree.query_ball_point(pts, radius_deg)])

    slp_coords = slp_time[['lat', 'lon']].values
    slp_tree   = cKDTree(slp_coords)
    slp_near   = slp_tree.query_ball_point(pts, radius_deg)

    # Default: no overlap, NaN SLP
    overlap = np.zeros(len(circ_df), dtype=bool)
    slp_vals = np.full(len(circ_df), np.nan)

    # Loop over circulation points
    for i, neighbors in enumerate(slp_near):
        if neighbors:  # if at least one SLP within radius
            overlap[i] = ar_near[i] and frt_near[i]
            # assign value of closest SLP
            _, idx = slp_tree.query(pts[i], k=1)
            slp_vals[i] = slp_time.iloc[idx]["value"]

    return pd.DataFrame({
        "triple_overlap": overlap,
        "slp_value": slp_vals
    }, index=circ_df.index)


def main():
    print("="*50)
    print("Script is running...")
    print("="*50)

    # File paths (updated merged NetCDFs)
    ar_file = "/cw3e/mead/projects/csg101/aillenden/postprocessing/merge_blobs/new/merged_ar.nc"
    frontal_file = "/cw3e/mead/projects/csg101/aillenden/postprocessing/merge_blobs/new/merged_frt.nc"
    circulation_file = "/cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/stitch_nodes/circulation_objects/circulations_wy2015.txt"
    slp_file = "/cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/stitch_nodes/cyclone_objects/slp_mins_wy2015.txt"

    ar_ds = load_dataset(ar_file)
    frt_ds = load_dataset(frontal_file)
    circ_df = parse_stitchnodes_txt(circulation_file)
    slp_df = parse_stitchnodes_txt(slp_file)

    if ar_ds is None or frt_ds is None or circ_df is None or slp_df is None:
        print("Error loading files.")
        return

    # Align AR and frontal datasets on time
    ar_ds, frt_ds = xr.align(ar_ds, frt_ds, join='inner')

    # Initialize output column
    circ_df['triple_overlap'] = False

    # Process circulations grouped by time
    for time_val, group in circ_df.groupby('time'):
        results = check_overlap_for_time(time_val, ar_ds, frt_ds, slp_df, group, radius_deg=0.25)
        circ_df.loc[group.index, ["triple_overlap", "slp_value"]] = results

    circ_df.to_csv("wy2015_overlap.csv", index=False)
    print("="*50)
    print("Script is complete!")
    print("="*50)


if __name__ == "__main__":
    main()
