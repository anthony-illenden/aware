import xarray as xr
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from datetime import datetime


def load_dataset(ds_path):
    try:
        return xr.open_dataset(ds_path)
    except FileNotFoundError:
        print(f"Dataset not found at {ds_path}. Please check the path.")
        return None

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

def load_df(df_path):
    try:
        return parse_stitchnodes_txt(df_path)
    except FileNotFoundError:
        print(f"Track data file not found at {df_path}. Please check the path.")
        return None

def merge_detect_blobs(ar_file_path, frontal_file_path, vort_file_path,
                       output_file="triple_overlap.nc", radius_deg=0.50):
    """
    Detect points where AR, frontal, and vortex objects all exist
    within radius_deg degrees of each other.
    """
    ar_ds = load_dataset(ar_file_path)
    frt_ds = load_dataset(frontal_file_path)
    vort_ds = load_dataset(vort_file_path)

    ar_ds, frt_ds, vort_ds = xr.align(ar_ds, frt_ds, vort_ds, join='inner')

    lats = frt_ds['latitude'].values
    lons = frt_ds['longitude'].values
    overlap_points = []

    for i in range(len(frt_ds.time)):
        time_val = frt_ds.time.values[i]

        ar_mask = ar_ds['object_id'].isel(time=i).values > 0
        frt_mask = frt_ds['object_id'].isel(time=i).values > 0
        vort_mask = vort_ds['object_id'].isel(time=i).values > 0

        if not (np.any(ar_mask) and np.any(frt_mask) and np.any(vort_mask)):
            continue

        # 2D indices of True values
        ar_points = np.column_stack(np.where(ar_mask))
        frt_points = np.column_stack(np.where(frt_mask))
        vort_points = np.column_stack(np.where(vort_mask))

        # Convert to lat/lon coordinates
        ar_coords = np.array([[lats[y], lons[x]] for y, x in ar_points])
        frt_coords = np.array([[lats[y], lons[x]] for y, x in frt_points])
        vort_coords = np.array([[lats[y], lons[x]] for y, x in vort_points])

        # Build spatial trees
        ar_tree = cKDTree(ar_coords)
        vort_tree = cKDTree(vort_coords)

        matched_lats = []
        matched_lons = []

        # Check that for each frontal point there is at least one AR and one vortex point within radius_deg
        for lat, lon in frt_coords:
            nearby_ar_idx = ar_tree.query_ball_point([lat, lon], radius_deg)
            nearby_vort_idx = vort_tree.query_ball_point([lat, lon], radius_deg)
            found = False
            for ar_idx in nearby_ar_idx:
                for vort_idx in nearby_vort_idx:
                    ar_lat, ar_lon = ar_coords[ar_idx]
                    vort_lat, vort_lon = vort_coords[vort_idx]
                    dist = np.sqrt((ar_lat - vort_lat)**2 + (ar_lon - vort_lon)**2)
                    if dist <= radius_deg:
                        matched_lats.append(lat)
                        matched_lons.append(lon)
                        found = True
                        break
                if found:
                    break

        if matched_lats:
            df = pd.DataFrame({
                'time': np.repeat(time_val, len(matched_lats)),
                'lat': matched_lats,
                'lon': matched_lons,
                'overlap': np.ones(len(matched_lats), dtype=int)
            })
            overlap_points.append(df)

    if overlap_points:
        overlap_df = pd.concat(overlap_points, ignore_index=True)
        overlap_ds = overlap_df.set_index(['time', 'lat', 'lon']).to_xarray()
        overlap_ds.to_netcdf(output_file)
        return overlap_ds
    else:
        print("No triple-overlap points found.")
        return None

def check_spatial_overlap(track_lat, track_lon, track_time, ds, radius_deg=0.50):
    """
    Returns True if any overlap=1 point is within radius_deg of track point at track_time.
    """
    try:
        overlap_time_slice = ds.sel(time=track_time, method='nearest')
        overlap_mask = overlap_time_slice == 1

        if not np.any(overlap_mask):
            return False

        overlap_indices = np.column_stack(np.where(overlap_mask.values))
        lats = overlap_time_slice.lat.values
        lons = overlap_time_slice.lon.values

        overlap_coords = np.array([[lats[idx[0]], lons[idx[1]]] for idx in overlap_indices])
        overlap_tree = cKDTree(overlap_coords)

        nearby_points = overlap_tree.query_ball_point([track_lat, track_lon], radius_deg)
        return len(nearby_points) > 0
    except Exception:
        return False

def compute_overlap_column(ds, df_tracks, radius_deg=0.50):
    """
    Adds a column 'overlap_qtr_deg' to track DataFrame indicating overlap presence.
    """
    try:
        return df_tracks.assign(
            overlap_qtr_deg=df_tracks.apply(
                lambda row: check_spatial_overlap(row.lat, row.lon, row.time, ds['overlap'], radius_deg),
                axis=1
            )
        )
    except KeyError:
        print("Dataset does not contain 'overlap'.")
        return None

def save_csv(df, filepath='overlap_results.csv'):
    if df is not None:
        df.to_csv(filepath, index=False)


if __name__ == "__main__":
    # Expanse paths
    ar_file = "/expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/tempest_output/stitch_blobs/new_wy2015_ar_objects_stitched.nc"
    frontal_file = "/expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/tempest_output/stitch_blobs/wy2015_frontal_objects.nc"
    vort_file = "/expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/tempest_output/stitch_blobs/vort_candidates_stitched.nc"
    df_file = "/expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/tempest_output/stitch_nodes/wy2015/corrected_slp.txt"

    overlap_ds = merge_detect_blobs(ar_file, frontal_file, vort_file)
    if overlap_ds is None:
        exit(1)

    df_tracks = load_df(df_file)
    if df_tracks is None:
        exit(1)

    df_tracks_overlap = compute_overlap_column(overlap_ds, df_tracks)
    if df_tracks_overlap is None:
        exit(1)

    save_csv(df_tracks_overlap, 'slp_triple_overlap.csv')
    print("Script complete!")
