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


def make_plots(ds_sliced, save_path=None, directions=None):
    """
    Create a 2x2 plot grid.
    """
    if ds_sliced is None:
        return

    if directions is None:
        directions = {'North': 55, 'East': 240, 'South': 20, 'West': 200}

    # Extract variables
    mslp = ds_sliced['MSLP'] # units: hPa
    ivt = ds_sliced['IVT'] # units: kg/m/s
    thetae_grad = ds_sliced['thetae_grad'] # units: K / 100 km
    pv_925 = ds_sliced['pv_925'] # units: 2PVU
    tadv_925 = ds_sliced['tadv_925'] # units: K/hr
    z_500 = ds_sliced['z_500'] # units: dam
    lat, lon = ds_sliced['latitude'], ds_sliced['longitude']

    # Get current time
    current_time = pd.to_datetime(mslp.time.values.item())

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
    z_contour = axes[0].contour(lon, lat, z_500, levels=np.arange(500, 620, 6),
                                   colors='black', transform=ccrs.PlateCarree(), linewidths=0.5)
    axes[0].clabel(z_contour, inline=True, fontsize=8, fmt='%d', colors='black')
    axes[0].set_extent([directions['West'], directions['East'], directions['South'], directions['North']])
    axes[0].coastlines()
    axes[0].add_feature(cfeature.BORDERS)
    axes[0].gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    axes[0].set_title('IVT')
    cbar1 = plt.colorbar(im1, ax=axes[0], shrink=0.8, orientation='horizontal')
    cbar1.set_label('kg/m/s', fontsize=10)

    # ------------------ Panel 2: Theta-e Gradient ------------------
    im2 = axes[1].contourf(lon, lat, thetae_grad, levels=np.arange(5, 40, 2),
                           cmap='RdYlBu_r', transform=ccrs.PlateCarree(), extend='max')
    slp_contour2 = axes[1].contour(lon, lat, mslp, levels=np.arange(960, 1041, 2),
                                   colors='black', transform=ccrs.PlateCarree(), linewidths=0.5)
    axes[1].clabel(slp_contour2, inline=True, fontsize=8, fmt='%d', colors='black')
    axes[1].set_extent([directions['West'], directions['East'], directions['South'], directions['North']])
    axes[1].coastlines()
    axes[1].add_feature(cfeature.BORDERS)
    axes[1].gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    axes[1].set_title(r'925-hPa $\nabla\theta_e$ Gradient')
    cbar2 = plt.colorbar(im2, ax=axes[1], shrink=0.8, orientation='horizontal')
    cbar2.set_label('K/100km', fontsize=10)

    # ------------------ Panel 3: PV ------------------
    pv_levels = np.arange(0, 3.26, 0.25)
    pv_colors = ['white', '#d1e9f7', '#a5cdec', '#79a3d5', '#69999b', '#78af58', '#b0cc58', '#f0d95f', '#de903e', '#cb5428', '#b6282a', '#9b1622', '#7a1419']
    pv_cmap = mcolors.ListedColormap(pv_colors)
    pv_norm = mcolors.BoundaryNorm(pv_levels, pv_cmap.N)
    im3 = axes[2].contourf(lon, lat, pv_925, levels=pv_levels,
                           cmap=pv_cmap, alpha=0.5, transform=ccrs.PlateCarree(), extend='max')
    slp_contour3 = axes[2].contour(lon, lat, mslp, levels=np.arange(960, 1041, 4),
                                   colors='black', transform=ccrs.PlateCarree(), linewidths=0.5)
    axes[2].clabel(slp_contour3, inline=True, fontsize=8, fmt='%d', colors='black')
    axes[2].set_extent([directions['West'], directions['East'], directions['South'], directions['North']])
    axes[2].coastlines()
    axes[2].add_feature(cfeature.BORDERS)
    axes[2].gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    axes[2].set_title('925-hPa PV')
    cbar3 = plt.colorbar(im3, ax=axes[2], shrink=0.8, orientation='horizontal')
    cbar3.set_label('2PVU', fontsize=10)

    # ------------------ Panel 4: TADV ------------------
    im4 = axes[3].contourf(lon, lat, tadv_925, levels=np.arange(-3, 4, 0.25),
                           cmap='bwr', transform=ccrs.PlateCarree(), extend='both')
    slp_contour4 = axes[3].contour(lon, lat, mslp, levels=np.arange(960, 1041, 4),
                                   colors='black', transform=ccrs.PlateCarree(), linewidths=0.5)
    axes[3].clabel(slp_contour4, inline=True, fontsize=8, fmt='%d', colors='black')
    axes[3].set_extent([directions['West'], directions['East'], directions['South'], directions['North']])
    axes[3].coastlines()
    axes[3].add_feature(cfeature.BORDERS)
    axes[3].gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    axes[3].set_title('925-hPa tadv')
    cbar4 = plt.colorbar(im4, ax=axes[3], shrink=0.8, orientation='horizontal')
    cbar4.set_label('K/hr', fontsize=10)

    plt.suptitle(current_time.strftime('%Y-%m-%d %H:%M'), fontsize=16)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.close(fig)


def process_time_series(main_files,
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
                make_plots(ds_sliced, save_path=save_path, directions=directions)
            else:
                make_plots(ds_sliced, directions=directions)

    return datasets


if __name__ == "__main__":
    # =============================================================================
    # USER CONFIGURATION
    # =============================================================================

    EVENTS_CSV_PATH = "/cw3e/mead/projects/csg101/aillenden/plots/extra_variable_field/ar_subjective_ds_mfw_wy2017.csv"
    BASE_PATH_MAIN = "/cw3e/mead/projects/csg101/aillenden/era5_data/wy2017/"
    OUTPUT_DIR = "/cw3e/mead/projects/csg101/aillenden/plots/extra_variable_field/"

    DIRECTIONS = {
        'North': 55,
        'East': 240,
        'South': 25,
        'West': 210
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
    df_events['start_date'] = pd.to_datetime(df_events['start_date'])
    df_events['end_date'] = pd.to_datetime(df_events['end_date'])

    print("=" * 50)
    print("Looping over events")
    print("=" * 50)

    for _, row in df_events.iterrows():
        event_id = row.iloc[0]
        start_dt = row['start_date']
        end_dt = row['end_date']

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
            save_plots=True,
            output_dir=event_output_dir,
            directions=DIRECTIONS,
            bounds=DATA_BOUNDS
        )

    print("=" * 50)
    print("Script completed successfully.")
    print("=" * 50)
