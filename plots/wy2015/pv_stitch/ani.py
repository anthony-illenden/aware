import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.animation import FuncAnimation, PillowWriter
from datetime import datetime, timedelta

def parse_file(filepath):
    data = []
    object_id = 0
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            if parts[0] == "start":
                object_id += 1
                continue
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

def main():
    STITCH_NODES_PATH = "/cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/stitch_nodes/pv_objects/pv_ivt_objects_stitch_paths.txt"
    df_parsed = parse_file(STITCH_NODES_PATH)

    # Create a time string column for unique time steps
    for col in ['year', 'month', 'day', 'hour']:
        df_parsed[col] = df_parsed[col].fillna(0).astype(int)
    df_parsed['time'] = df_parsed.apply(
        lambda row: f"{int(row['year']):04d}-{int(row['month']):02d}-{int(row['day']):02d} {int(row['hour']):02d}:00", axis=1
    )

    # Ensure longitude is in [-180, 180]
    if df_parsed['lon'].max() > 180:
        df_parsed['lon'] = df_parsed['lon'].apply(lambda x: x - 360 if x > 180 else x)

    unique_times = sorted(df_parsed['time'].unique())

    min_lon, max_lon = df_parsed['lon'].min()-2, df_parsed['lon'].max()+2
    min_lat, max_lat = df_parsed['lat'].min()-2, df_parsed['lat'].max()+2

    fig = plt.figure(figsize=(10, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())

    def init():
        ax.set_title("WY2015 StitchNodes Tracks - PV & IVT")
        return []

    def update(frame):
        ax.clear()
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS)
        ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, zorder=0)
        ax.set_extent([min_lon, max_lon, min_lat, max_lat])
        time = unique_times[frame]
        subset = df_parsed[df_parsed['time'] == time]
        for obj_id, group in subset.groupby("object_id"):
            ax.plot(group["lon"], group["lat"], marker='o', linestyle='-', label=f"Object {obj_id}")
        ax.set_title(f"WY2015 StitchNodes Tracks - PV & IVT\nTime: {time}")
        ax.legend()
        return []

    anim = FuncAnimation(fig, update, frames=len(unique_times), init_func=init, blit=False)
    anim.save('wy2015_tracks.gif', writer=PillowWriter(fps=5))
    plt.close(fig)
    print("GIF saved as wy2015_tracks.gif")

if __name__ == "__main__":
    main()