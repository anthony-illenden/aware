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
def parse_detect_nodes_file(filepath):
    data = []
    current_time = None

    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue

            # Date/time line (no leading tab)
            if not line.startswith('\t'):
                # Expect: YYYY MM DD count HH
                if len(parts) != 5:
                    raise ValueError(f"Unexpected datetime line format: {parts}")
                
                year, month, day, count, hour = map(int, parts)

                current_time = {
                    "year": year,
                    "month": month,
                    "day": day,
                    "hour": hour,
                    "count": count
                }

            # Data line (leading tab)
            else:
                i, j = int(parts[0]), int(parts[1])
                lon, lat, pv_val = float(parts[2]), float(parts[3]), float(parts[4])
                entry = {
                    "i": i,
                    "j": j,
                    "lon": lon,
                    "lat": lat,
                    "pv_value": pv_val,
                    "year": current_time["year"],
                    "month": current_time["month"],
                    "day": current_time["day"],
                    "hour": current_time["hour"],
                    "count": current_time["count"]
                }
                data.append(entry)

    return pd.DataFrame(data)

def generate_file_paths(start_dt, end_dt, base_path_main):
    main_paths = []
    current_date = start_dt
    while current_date <= end_dt:
        filename = f"sliced_{current_date.strftime('%Y%m%d_%H')}.nc"
        main_paths.append(os.path.join(base_path_main, filename))
        current_date += timedelta(hours=3)
    return main_paths

def make_plot(ds, directions, output_dir, text_df, event_id):
    lat, lon = ds['latitude'], ds['longitude']
    current_time = pd.to_datetime(ds.pv_925.time.values.item())

    if text_df is not None and not text_df.empty:
        if text_df['lon'].max() > 180:
            text_df['lon'] = text_df['lon'].apply(lambda x: x-360 if x > 180 else x)
        mask = (
            (text_df['year'] == current_time.year) &
            (text_df['month'] == current_time.month) &
            (text_df['day'] == current_time.day) &
            (text_df['hour'] == current_time.hour)
        )
        matched_nodes = text_df[mask]
    else:
        matched_nodes = pd.DataFrame()

    fig, ax = plt.subplots(figsize=(12, 9), subplot_kw={'projection': ccrs.PlateCarree()})
    pv_levels = np.arange(0, 3.26, 0.25)
    pv_colors = ['white', '#d1e9f7', '#a5cdec', '#79a3d5', '#69999b', '#78af58', 
                 '#b0cc58', '#f0d95f', '#de903e', '#cb5428', '#b6282a', '#9b1622', '#7a1419']
    pv_cmap = mcolors.ListedColormap(pv_colors)
    pv_norm = mcolors.BoundaryNorm(pv_levels, pv_cmap.N)

    im3 = ax.contourf(lon, lat, ds.pv_925, levels=pv_levels,
                      cmap=pv_cmap, alpha=0.5, transform=ccrs.PlateCarree(), extend='max')
    ax.contour(lon, lat, ds.pv_925, levels=np.arange(1.5, 1.75, 0.25), 
               colors='k', linewidths=2, transform=ccrs.PlateCarree())

    ax.set_extent([directions['West'], directions['East'], 
                   directions['South'], directions['North']])
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS)
    ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    ax.set_title('925-hPa PV')
    cbar3 = plt.colorbar(im3, ax=ax, pad=0.05, aspect=50, orientation='horizontal')
    cbar3.set_label('2PVU', fontsize=10)

    if not matched_nodes.empty:
        ax.scatter(
            matched_nodes['lon'], matched_nodes['lat'],
            marker='x', color='black', s=50, label='StitchNode'
        )

    pvu_line = plt.Line2D([0], [0], color='black', linewidth=1, label='>=1.5 2PVU')
    ax.legend(handles=[pvu_line], loc='upper right')

    plt.title(current_time.strftime('%Y-%m-%d %H:%M'), fontsize=16)
    plt.tight_layout()

    # Save to output directory
    date_str = current_time.strftime('%Y%m%d_%H%M')
    if event_id == "non_event":
        save_path = os.path.join(output_dir, f"pv_plot_{date_str}.png")
    else:
        save_path = os.path.join(output_dir, f"event_{event_id}", f"pv_plot_{date_str}.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

# =====================================================
if __name__ == "__main__":
    EVENTS_CSV_PATH = "/cw3e/mead/projects/csg101/aillenden/wy2015_dates.csv"
    BASE_PATH_MAIN = "/cw3e/mead/projects/csg101/aillenden/era5_data/wy2015_extra/"
    OUTPUT_DIR = "/cw3e/mead/projects/csg101/aillenden/plots/wy2015/non_events/"
    DETECT_NODES_PATH = "/cw3e/mead/projects/csg101/aillenden/tempest_extremes/python_output/merged_pv_ivt_objects.txt"

    DIRECTIONS = {
        'North': 50,
        'East': 240,
        'South': 30,
        'West': 215
    }

    # Load detect_nodes
    text_df = parse_detect_nodes_file(DETECT_NODES_PATH)
    text_df['timestamp'] = pd.to_datetime(
        text_df[['year', 'month', 'day', 'hour']].assign(minute=0)
    )

    # Load events
    df_events = pd.read_csv(EVENTS_CSV_PATH)
    df_events['Start_Date'] = pd.to_datetime(df_events['Start_Date'])
    df_events['End_Date'] = pd.to_datetime(df_events['End_Date'])

    # =====================================================
    # Plot non-event detect_nodes
    event_intervals = pd.IntervalIndex.from_arrays(df_events['Start_Date'], df_events['End_Date'], closed='both')
    mask_outside = ~text_df['timestamp'].apply(lambda ts: any(ts in interval for interval in event_intervals))
    text_df_outside = text_df[mask_outside]

    print("=" * 50)
    print("Looping over events...")
    print("=" * 50)

    OUTPUT_DIR_NON_EVENTS = os.path.join(OUTPUT_DIR, "non_events")
    os.makedirs(OUTPUT_DIR_NON_EVENTS, exist_ok=True)

    for ts in text_df_outside['timestamp'].unique():
        file_path = os.path.join(
            BASE_PATH_MAIN,
            f"sliced_{ts.strftime('%Y%m%d_%H')}.nc"
        )
        if os.path.exists(file_path):
            ds = xr.open_dataset(file_path).squeeze()
            nodes_at_ts = text_df_outside[text_df_outside['timestamp'] == ts]
            make_plot(ds, DIRECTIONS, OUTPUT_DIR_NON_EVENTS, nodes_at_ts, event_id="non_event")
        else:
            print(f"Missing file: {file_path}")
    print("=" * 50)
    print("All plots processed successfully.")
    print("=" * 50)
