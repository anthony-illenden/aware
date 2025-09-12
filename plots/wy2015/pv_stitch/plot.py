import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
from datetime import datetime, timedelta
import os

# =====================================================
def parse_stitch_nodes_file(filepath):
    data = []
    object_id = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            
            if not parts:
                continue
            
            # Start of a new object block
            if parts[0] == "start":
                object_id += 1
                nsteps = int(parts[1])
                start_time = {
                    "year": int(parts[2]),
                    "month": int(parts[3]),
                    "day": int(parts[4]),
                    "hour": int(parts[5])
                }
                continue
            
            # Regular data line
            i, j = int(parts[0]), int(parts[1])
            lon, lat, pv_val = float(parts[2]), float(parts[3]), float(parts[4])
            year, month, day, hour = map(int, parts[5:])
            
            data.append({
                "object_id": object_id,
                "i": i,
                "j": j,
                "lon": lon,
                "lat": lat,
                "pv_value": pv_val,
                "year": year,
                "month": month,
                "day": day,
                "hour": hour
            })
    
    return pd.DataFrame(data)

def generate_file_paths(start_dt, end_dt, base_path_main):
    """
    Generate list of file paths for the specified date range (every 3 hours).
    """
    main_paths = []
    current_date = start_dt

    while current_date <= end_dt:
        filename = f"sliced_{current_date.strftime('%Y%m%d_%H')}.nc"
        main_paths.append(os.path.join(base_path_main, filename))
        current_date += timedelta(hours=3)

    return main_paths
    
def make_plot(ds, directions, output_dir, df_path, event_id):
    lat, lon = ds['latitude'], ds['longitude']
    current_time = pd.to_datetime(ds.pv_925.time.values.item())

    df = parse_stitch_nodes_file(df_path)

    if df['lon'].max() > 180:
        df['lon'] = df['lon'].apply(lambda x: x-360 if x > 180 else x)
    min_lon, max_lon = df['lon'].min()-2, df['lon'].max()+2
    min_lat, max_lat = df['lat'].min()-2, df['lat'].max()+2

    matched_nodes = pd.DataFrame()
    if df is not None:
        mask = (
            (df['year'] == current_time.year) &
            (df['month'] == current_time.month) &
            (df['day'] == current_time.day) &
            (df['hour'] == current_time.hour)
        )
        matched_nodes = df[mask]

    fig, ax = plt.subplots(figsize=(12, 9), subplot_kw={'projection': ccrs.PlateCarree()})
    pv_levels = np.arange(0, 3.26, 0.25)
    pv_colors = ['white', '#d1e9f7', '#a5cdec', '#79a3d5', '#69999b', '#78af58', '#b0cc58', '#f0d95f', '#de903e', '#cb5428', '#b6282a', '#9b1622', '#7a1419']
    pv_cmap = mcolors.ListedColormap(pv_colors)
    pv_norm = mcolors.BoundaryNorm(pv_levels, pv_cmap.N)
    im3 = ax.contourf(lon, lat, ds.pv_925, levels=pv_levels,
                      cmap=pv_cmap, alpha=0.5, transform=ccrs.PlateCarree(), extend='max')
    ax.contour(lon, lat, ds.pv_925, levels=np.arange(1.5, 1.75, 0.25), colors='k', linewidths=2, transform=ccrs.PlateCarree())

    ax.set_extent([directions['West'], directions['East'], directions['South'], directions['North']])
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS)
    ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    ax.set_title('925-hPa PV')
    cbar3 = plt.colorbar(im3, ax=ax, pad=0.05, aspect=50, orientation='horizontal')
    cbar3.set_label('2PVU', fontsize=10)


    # Plot stitchnodes if provided
    if matched_nodes is not None and not matched_nodes.empty:
        ax.scatter(
            matched_nodes['lon'], matched_nodes['lat'],
            marker='o', color='red', s=50, edgecolors='black',
            label='StitchNode'
        )

    # Custom legend to include both node types and PVU line
    handles = []
    pvu_line = plt.Line2D([0], [0], color='black', linewidth=1, label='>=1.5 2PVU')
    handles.append(pvu_line)
    if matched_nodes is not None and not matched_nodes.empty:
        stitch_handle = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markeredgecolor='red', markersize=8, linestyle='None', label='StitchNode')
        handles.append(stitch_handle)
    ax.legend(handles=handles, loc='upper right')

    plt.title(current_time.strftime('%Y-%m-%d %H:%M'), fontsize=16)
    plt.tight_layout()

    # Save inside event-specific directory
    date_str = current_time.strftime('%Y%m%d_%H%M')
    save_path = os.path.join(output_dir, f"event_{event_id}", f"pv_plot_{date_str}.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

# =====================================================
if __name__ == "__main__":
    EVENTS_CSV_PATH = "/cw3e/mead/projects/csg101/aillenden/wy2015_dates.csv"
    BASE_PATH_MAIN = "/cw3e/mead/projects/csg101/aillenden/era5_data/wy2015_extra/"
    OUTPUT_DIR = "/cw3e/mead/projects/csg101/aillenden/plots/wy2015/pv_stitch/"
    STITCH_NODES_PATH = "/cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/stitch_nodes/pv_objects/pv_ivt_objects_stitch_paths.txt"

    DIRECTIONS = {
        'North': 50,
        'East': 240,
        'South': 30,
        'West': 215
    }

    # Load event dates
    df_events = pd.read_csv(EVENTS_CSV_PATH)
    df_events['Start_Date'] = pd.to_datetime(df_events['Start_Date'])
    df_events['End_Date'] = pd.to_datetime(df_events['End_Date'])

    print("=" * 50)
    print("Looping over events...")
    print("=" * 50)

    for _, row in df_events.iterrows():
        event_id = row.iloc[0]   # first column = event_id
        start_dt = row['Start_Date']
        end_dt = row['End_Date']

        print(f"Processing Event {event_id} from {start_dt} to {end_dt}")

        main_files = generate_file_paths(start_dt, end_dt, base_path_main=BASE_PATH_MAIN)

        for file_path in main_files:
            if os.path.exists(file_path):
                ds = xr.open_dataset(file_path).squeeze()
                make_plot(ds, DIRECTIONS, OUTPUT_DIR, STITCH_NODES_PATH, event_id)
            else:
                print(f"Missing file: {file_path}")

    print("=" * 50)
    print("All events processed successfully.")
    print("=" * 50)
