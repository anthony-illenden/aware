import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
from datetime import datetime, timedelta
import os


def generate_file_paths(start_year, start_month, start_day, start_hour,
                        end_year, end_month, end_day, end_hour,
                        base_path_main):
    """
    Generate list of file paths for the specified date range (every 3 hours).
    """
    start_date = datetime(start_year, start_month, start_day, start_hour)
    end_date = datetime(end_year, end_month, end_day, end_hour)

    main_paths = []
    current_date = start_date

    while current_date <= end_date:
        filename = f"sliced_{current_date.strftime('%Y%m%d_%H')}.nc"
        main_paths.append(os.path.join(base_path_main, filename))
        current_date += timedelta(hours=3)

    return main_paths


def load_dataset(main_path, bounds=None):
    """
    Load the dataset file and slice to lat/lon bounds.
    """
    try:
        ds_main = xr.open_dataset(main_path).squeeze()

        if bounds is None:
            bounds = dict(
                latitude=slice(15.0, 60.0),
                longitude=slice(165, 250)
            )

        return ds_main.sel(**bounds)

    except Exception as e:
        print(f"Error loading dataset:\n  File: {main_path}\n  Error: {e}")
        return None


def has_twelve_hour_consecutive_trues(group, window_size):
    mask = group["triple_overlap"]
    # Rolling window for 12 hours, require all True
    return (mask.rolling(window_size).sum() == window_size).any()


def load_cyclone_tracks(cyclone_path):
    df = pd.read_csv(cyclone_path)
    df_track = df[df['triple_overlap'] == True]
    df_track['time'] = pd.to_datetime(df_track['time'])
    df_track["triple_overlap"] = df_track["triple_overlap"].astype(bool)
    time_diffs = df_track.groupby('track_id')['time'].diff().dt.total_seconds() / 3600  # convert to hours
    typical_interval = time_diffs.mode()[0]  # most common interval
    window_size = int(12 / typical_interval)
    storm_ids_to_keep = df_track.groupby("track_id").filter(
        lambda x: has_twelve_hour_consecutive_trues(x, window_size)
    )["track_id"].unique()
    df_track_filtered = df_track[df_track["track_id"].isin(storm_ids_to_keep)]

    return df_track_filtered


def make_plots(ds_sliced, cyclone_path, save_path=None, directions=None):
    """
    Create a 2x2 weather plot grid with cyclone track centers overlay.
    """
    if ds_sliced is None:
        return

    if directions is None:
        directions = {'North': 55, 'East': 250, 'South': 20, 'West': 200}

    # Extract variables
    mslp = ds_sliced.MSLP
    ivt = ds_sliced.IVT
    thetae_grad = ds_sliced.thetae_grad
    vort = ds_sliced['vort_925']
    lat, lon = ds_sliced['latitude'], ds_sliced['longitude']

    # Get current time
    current_time = pd.to_datetime(mslp.time.values.item())

    # Load filtered cyclone tracks
    df_track_filtered = load_cyclone_tracks(cyclone_path)

    # Filter tracks for this specific time
    tracks_at_time = pd.DataFrame()
    if df_track_filtered is not None:
        tracks_at_time = df_track_filtered[df_track_filtered['time'] == current_time]

    # Create figure with 2x2 subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10),
                             subplot_kw={'projection': ccrs.PlateCarree()})
    axes = axes.flatten()

    # ------------------ Panel 1: IVT ------------------
    ivt_levels = [250, 300, 400, 500, 600, 700, 800, 1000, 1200, 1400, 1600, 1800]
    ivt_colors = ['#ffff00', '#ffe400', '#ffc800', '#ffad00', '#ff8200', '#ff5000', '#ff1e00',
                  '#eb0010', '#b8003a', '#850063', '#921972', '#570088']
    ivt_cmap = mcolors.ListedColormap(ivt_colors)
    ivt_norm = mcolors.BoundaryNorm(ivt_levels, ivt_cmap.N)

    im1 = axes[0].contourf(lon, lat, ivt, levels=ivt_levels, cmap=ivt_cmap,
                           norm=ivt_norm, transform=ccrs.PlateCarree(), extend='max')
    slp_contour1 = axes[0].contour(lon, lat, mslp, levels=np.arange(960, 1041, 4),
                                   colors='black', transform=ccrs.PlateCarree(), linewidths=0.5)
    axes[0].clabel(slp_contour1, inline=True, fontsize=8, fmt='%d', colors='black')
    axes[0].set_extent([directions['West'] - 15, directions['East'], directions['South'], directions['North']])
    axes[0].coastlines()
    axes[0].add_feature(cfeature.BORDERS)
    axes[0].gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    axes[0].set_title('IVT')
    cbar1 = plt.colorbar(im1, ax=axes[0], shrink=0.8, orientation='horizontal')
    cbar1.set_label('kg/m/s', fontsize=10)

    # ------------------ Panel 2: Theta-e Gradient ------------------
    im2 = axes[1].contourf(lon, lat, thetae_grad, levels=np.arange(5, 40, 2),
                           cmap='RdYlBu_r', transform=ccrs.PlateCarree(), extend='max')
    slp_contour2 = axes[1].contour(lon, lat, mslp, levels=np.arange(960, 1041, 4),
                                   colors='black', transform=ccrs.PlateCarree(), linewidths=0.5)
    axes[1].clabel(slp_contour2, inline=True, fontsize=8, fmt='%d', colors='black')
    axes[1].set_extent([directions['West'] - 15, directions['East'], directions['South'], directions['North']])
    axes[1].coastlines()
    axes[1].add_feature(cfeature.BORDERS)
    axes[1].gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    axes[1].set_title(r'925-hPa $\nabla\theta_e$ Gradient')
    cbar2 = plt.colorbar(im2, ax=axes[1], shrink=0.8, orientation='horizontal')
    cbar2.set_label('K/100km', fontsize=10)

    # ------------------ Panel 3: MSLP ------------------
    slp_contour = axes[2].contour(lon, lat, mslp, levels=np.arange(960, 1041, 2),
                                  colors='black', transform=ccrs.PlateCarree(), linewidths=0.5)
    axes[2].clabel(slp_contour, inline=True, fontsize=8, fmt='%d', colors='black')
    im3 = axes[2].contourf(lon, lat, mslp, levels=np.arange(960, 1041, 2),
                           cmap='jet', alpha=0.5, transform=ccrs.PlateCarree(), extend='both')
    axes[2].set_extent([directions['West'] - 15, directions['East'], directions['South'], directions['North']])
    axes[2].coastlines()
    axes[2].add_feature(cfeature.BORDERS)
    axes[2].gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    axes[2].set_title('MSLP')
    cbar3 = plt.colorbar(im3, ax=axes[2], shrink=0.8, orientation='horizontal')
    cbar3.set_label('hPa', fontsize=10)

    # ------------------ Panel 4: Vorticity ------------------
    im4 = axes[3].contourf(lon, lat, vort, levels=np.arange(1, 51, 5),
                           cmap='YlOrRd', transform=ccrs.PlateCarree(), extend='max')
    slp_contour4 = axes[3].contour(lon, lat, mslp, levels=np.arange(960, 1041, 4),
                                   colors='black', transform=ccrs.PlateCarree(), linewidths=0.5)
    axes[3].clabel(slp_contour4, inline=True, fontsize=8, fmt='%d', colors='black')
    axes[3].set_extent([directions['West'] - 15, directions['East'], directions['South'], directions['North']])
    axes[3].coastlines()
    axes[3].add_feature(cfeature.BORDERS)
    axes[3].gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    axes[3].set_title(r'925-hPa $\zeta$')
    cbar4 = plt.colorbar(im4, ax=axes[3], shrink=0.8, orientation='horizontal')
    cbar4.set_label('1x10^-5 1/s', fontsize=10)

    # ------------------ Overlay Track Centers ------------------
    if not tracks_at_time.empty:
        for ax in axes:
            ax.scatter(tracks_at_time['lon'], tracks_at_time['lat'],
                       c='black', s=50, marker='o', transform=ccrs.PlateCarree(),
                       label='Track Centers', zorder=99)
            ax.legend(loc='upper right', fontsize=8)

    plt.suptitle(current_time.strftime('%Y-%m-%d %H:%M'), fontsize=16)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.close(fig)


def process_time_series(main_files,
                        cyclone_path,
                        save_plots=False,
                        output_dir=None,
                        directions=None,
                        bounds=None):
    """
    Process multiple files for a time series.
    """
    if save_plots and output_dir:
        os.makedirs(output_dir, exist_ok=True)

    datasets = []

    for main_path in main_files:
        print(f"Processing: {os.path.basename(main_path)}")

        ds_sliced = load_dataset(main_path, bounds)

        if ds_sliced is not None:
            datasets.append(ds_sliced)

            if save_plots and output_dir:
                timestamp = pd.to_datetime(ds_sliced.time.values).strftime('%Y%m%d_%H')
                save_path = os.path.join(output_dir, f"base_variables_{timestamp}.png")
                make_plots(ds_sliced, cyclone_path, save_path=save_path, directions=directions)
            else:
                make_plots(ds_sliced, cyclone_path, directions=directions)

    return datasets


if __name__ == "__main__":
    # =============================================================================
    # USER CONFIGURATION
    # =============================================================================

    EVENTS_CSV_PATH = "/cw3e/mead/projects/csg101/aillenden/wy2015_dates.csv"
    BASE_PATH_MAIN = "/cw3e/mead/projects/csg101/aillenden/era5_data/wy2015/"
    CYCLONE_PATH = "/cw3e/mead/projects/csg101/aillenden/postprocessing/merge_blobs/wy2015_overlap_raw.csv"
    OUTPUT_DIR = "/cw3e/mead/projects/csg101/aillenden/plots/wy2015/variable_field/"

    DIRECTIONS = {
        'North': 55,
        'East': 250,
        'South': 20,
        'West': 200
    }

    DATA_BOUNDS = {
        'latitude': slice(15.0, 60.0),
        'longitude': slice(165, 250)
    }

    # =============================================================================
    # MAIN EXECUTION
    # =============================================================================

    print("=" * 50)
    print("Script is running...")
    print("=" * 50)
    print("Loading event dates...")
    print("=" * 50)

    df_events = pd.read_csv(EVENTS_CSV_PATH)
    df_events['Start_Date'] = pd.to_datetime(df_events['Start_Date'])
    df_events['End_Date'] = pd.to_datetime(df_events['End_Date'])

    print("=" * 50)
    print("Looping over events")
    print("=" * 50)

    for _, row in df_events.iterrows():
        event_id = row.iloc[0]
        start_dt = row['Start_Date']
        end_dt = row['End_Date']

        print(f"Processing Event {event_id} from {start_dt} to {end_dt}")

        main_files = generate_file_paths(
            start_dt.year, start_dt.month, start_dt.day, start_dt.hour,
            end_dt.year, end_dt.month, end_dt.day, end_dt.hour,
            base_path_main=BASE_PATH_MAIN
        )

        event_output_dir = os.path.join(OUTPUT_DIR, f"event_{event_id}")
        os.makedirs(event_output_dir, exist_ok=True)

        process_time_series(
            main_files=main_files,
            cyclone_path=CYCLONE_PATH,
            save_plots=True,
            output_dir=event_output_dir,
            directions=DIRECTIONS,
            bounds=DATA_BOUNDS
        )

    print("=" * 50)
    print("Script completed successfully.")
    print("=" * 50)
