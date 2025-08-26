import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
from datetime import datetime, timedelta
import os


# =====================================================================
# HELPERS
# =====================================================================

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
    Load the main variables dataset file and slice to lat/lon bounds.
    """
    try:
        ds_main = xr.open_dataset(main_path).squeeze()

        if bounds is not None:
            ds_main = ds_main.sel(**bounds)

        return ds_main

    except Exception as e:
        print(f"Error loading dataset:\n  File: {main_path}\n  Error: {e}")
        return None


def load_blob_dataset(blob_path, current_time, bounds=None):
    """
    Load detectblob mask at current_time from a NetCDF file.
    """
    try:
        ds = xr.open_dataset(blob_path)
        if bounds is not None:
            ds = ds.sel(**bounds)
        if "time" in ds.dims:
            ds = ds.sel(time=current_time, method="nearest")
        return ds
    except Exception as e:
        print(f"Error loading blob dataset:\n  File: {blob_path}\n  Error: {e}")
        return None


def parse_nodes_txt(filepath):
    with open(filepath, "r") as f:
        lines = f.readlines()

    data = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 6:
            continue  # skip malformed lines

        try:
            year   = int(parts[0])
            month  = int(parts[1])
            day    = int(parts[2])
            hour   = int(parts[3])
            # Some files might include an ID column before lon/lat
            if len(parts) == 7:
                node_id = int(parts[4])
                lon = float(parts[5])
                lat = float(parts[6])
            else:  # assume lon/lat directly follow time
                lon = float(parts[4])
                lat = float(parts[5])
                node_id = None
        except ValueError:
            continue  # skip bad lines

        current_time = datetime(year, month, day, hour)
        data.append((current_time, lon, lat, node_id))

    import pandas as pd
    return pd.DataFrame(data, columns=["time", "lon", "lat", "node_id"])




# =====================================================================
# PLOTTING
# =====================================================================

def make_plots(ds_sliced, current_time,
               ivt_blob_path, thetae_blob_path,
               vort_nodes_path, slp_nodes_path,
               save_path=None, directions=None):
    """
    Create a 2x4 plot:
      Top row: IVT, theta-e grad, vorticity, MSLP
      Bottom row: IVT blobs, theta-e blobs, vorticity nodes, SLP nodes
    """
    if ds_sliced is None:
        return

    if directions is None:
        directions = {'North': 55, 'East': 250, 'South': 20, 'West': 200}

    # Extract fields
    mslp = ds_sliced.MSLP
    ivt = ds_sliced.IVT
    thetae_grad = ds_sliced.thetae_grad
    vort = ds_sliced['vort_925']
    lat, lon = ds_sliced['latitude'], ds_sliced['longitude']

    # -----------------------------------------------------------------
    # Setup figure
    # -----------------------------------------------------------------
    fig, axes = plt.subplots(2, 4, figsize=(22, 10),
                             subplot_kw={'projection': ccrs.PlateCarree()})
    axes = axes.flatten()

    # Common map formatting
    def format_ax(ax):
        ax.set_extent([directions['West'] - 15, directions['East'],
                       directions['South'], directions['North']])
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS)
        ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

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
    axes[0].set_title('IVT')
    format_ax(axes[0])
    cbar1 = plt.colorbar(im1, ax=axes[0], shrink=0.8, orientation='horizontal')
    cbar1.set_label('kg/m/s')

    # ------------------ Panel 2: Theta-e Gradient ------------------
    im2 = axes[1].contourf(lon, lat, thetae_grad, levels=np.arange(5, 40, 2),
                           cmap='RdYlBu_r', transform=ccrs.PlateCarree(), extend='max')
    slp_contour2 = axes[1].contour(lon, lat, mslp, levels=np.arange(960, 1041, 4),
                                   colors='black', transform=ccrs.PlateCarree(), linewidths=0.5)
    axes[1].clabel(slp_contour2, inline=True, fontsize=8, fmt='%d', colors='black')
    axes[1].set_title(r'925-hPa $\nabla\theta_e$')
    format_ax(axes[1])
    cbar2 = plt.colorbar(im2, ax=axes[1], shrink=0.8, orientation='horizontal')
    cbar2.set_label('K/100km')

    # ------------------ Panel 3: Vorticity ------------------
    im3 = axes[2].contourf(lon, lat, vort, levels=np.arange(1, 51, 5),
                           cmap='YlOrRd', transform=ccrs.PlateCarree(), extend='max')
    slp_contour3 = axes[2].contour(lon, lat, mslp, levels=np.arange(960, 1041, 4),
                                   colors='black', transform=ccrs.PlateCarree(), linewidths=0.5)
    axes[2].clabel(slp_contour3, inline=True, fontsize=8, fmt='%d', colors='black')
    axes[2].set_title(r'925-hPa $\zeta$')
    format_ax(axes[2])
    cbar3 = plt.colorbar(im3, ax=axes[2], shrink=0.8, orientation='horizontal')
    cbar3.set_label('1x10^-5 1/s')

    # ------------------ Panel 4: MSLP ------------------
    im4 = axes[3].contourf(lon, lat, mslp, levels=np.arange(960, 1041, 2),
                           cmap='jet', alpha=0.5, transform=ccrs.PlateCarree(), extend='both')
    slp_contour4 = axes[3].contour(lon, lat, mslp, levels=np.arange(960, 1041, 2),
                                   colors='black', transform=ccrs.PlateCarree(), linewidths=0.5)
    axes[3].clabel(slp_contour4, inline=True, fontsize=8, fmt='%d', colors='black')
    axes[3].set_title('MSLP')
    format_ax(axes[3])
    cbar4 = plt.colorbar(im4, ax=axes[3], shrink=0.8, orientation='horizontal')
    cbar4.set_label('hPa')

    # ------------------ Panel 5: IVT Blobs ------------------
    ds_ivt_blob = load_blob_dataset(ivt_blob_path, current_time, bounds=None)
    if ds_ivt_blob is not None:
        mask = list(ds_ivt_blob.data_vars.values())[0]
        lon_b = ds_ivt_blob["lon"].values if "lon" in ds_ivt_blob else ds_ivt_blob["longitude"].values
        lat_b = ds_ivt_blob["lat"].values if "lat" in ds_ivt_blob else ds_ivt_blob["latitude"].values
        Lon_b, Lat_b = np.meshgrid(lon_b, lat_b)
        axes[4].contourf(Lon_b, Lat_b, mask, levels=[0.5, 1.5],
                         colors=["red"], alpha=0.4, transform=ccrs.PlateCarree())
    axes[4].set_title("IVT Blobs")
    format_ax(axes[4])

    # ------------------ Panel 6: Theta-e Blobs ------------------
    ds_thetae_blob = load_blob_dataset(thetae_blob_path, current_time, bounds=None)
    if ds_thetae_blob is not None:
        mask = list(ds_thetae_blob.data_vars.values())[0]
        lon_b = ds_thetae_blob["lon"].values if "lon" in ds_thetae_blob else ds_thetae_blob["longitude"].values
        lat_b = ds_thetae_blob["lat"].values if "lat" in ds_thetae_blob else ds_thetae_blob["latitude"].values
        Lon_b, Lat_b = np.meshgrid(lon_b, lat_b)
        axes[5].contourf(Lon_b, Lat_b, mask, levels=[0.5, 1.5],
                         colors=["blue"], alpha=0.4, transform=ccrs.PlateCarree())
    axes[5].set_title("Theta-e Blobs")
    format_ax(axes[5])

    # ------------------ Panel 7: Vorticity Nodes ------------------
    df_vort_nodes = parse_nodes_txt(vort_nodes_path)
    nodes_vort = df_vort_nodes[df_vort_nodes["time"] == current_time]
    if not nodes_vort.empty:
        axes[6].scatter(nodes_vort.lon, nodes_vort.lat, c="black", s=40, marker="x",
                        transform=ccrs.PlateCarree())
    axes[6].set_title("Vorticity Nodes")
    format_ax(axes[6])

    # ------------------ Panel 8: SLP Nodes ------------------
    df_slp_nodes = parse_nodes_txt(slp_nodes_path)
    nodes_slp = df_slp_nodes[df_slp_nodes["time"] == current_time]
    if not nodes_slp.empty:
        axes[7].scatter(nodes_slp.lon, nodes_slp.lat, c="black", s=40, marker="o",
                        transform=ccrs.PlateCarree())
    axes[7].set_title("SLP Nodes")
    format_ax(axes[7])

    plt.suptitle(current_time.strftime('%Y-%m-%d %H:%M'), fontsize=16)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.close(fig)


# =====================================================================
# DRIVER
# =====================================================================

def process_time_series(main_files,
                        ivt_blob_path,
                        thetae_blob_path,
                        vort_nodes_path,
                        slp_nodes_path,
                        save_plots=False,
                        output_dir=None,
                        directions=None,
                        bounds=None):
    """
    Loop over time series, generating 2x4 panel plots.
    """
    if save_plots and output_dir:
        os.makedirs(output_dir, exist_ok=True)

    for main_path in main_files:
        print(f"Processing: {os.path.basename(main_path)}")

        ds_sliced = load_dataset(main_path, bounds)

        if ds_sliced is not None:
            current_time = pd.to_datetime(ds_sliced.time.values)

            if save_plots and output_dir:
                timestamp = current_time.strftime('%Y%m%d_%H')
                save_path = os.path.join(output_dir, f"variables_blobs_nodes_{timestamp}.png")
                make_plots(ds_sliced, current_time,
                           ivt_blob_path, thetae_blob_path,
                           vort_nodes_path, slp_nodes_path,
                           save_path=save_path, directions=directions)
            else:
                make_plots(ds_sliced, current_time,
                           ivt_blob_path, thetae_blob_path,
                           vort_nodes_path, slp_nodes_path,
                           directions=directions)


# =====================================================================
# MAIN EXECUTION
# =====================================================================
if __name__ == "__main__":

    # USER CONFIGURATION
    EVENTS_CSV_PATH = "/cw3e/mead/projects/csg101/aillenden/wy2015_dates.csv"
    BASE_PATH_MAIN = "/cw3e/mead/projects/csg101/aillenden/era5_data/wy2015/"
    IVT_BLOB_PATH = "/cw3e/mead/projects/csg101/aillenden/postprocessing/merge_blobs/new/merged_ar.nc"
    THETAE_BLOB_PATH = "/cw3e/mead/projects/csg101/aillenden/postprocessing/merge_blobs/new/merged_frt.nc"
    VORT_NODES_PATH = "/cw3e/mead/projects/csg101/aillenden/postprocessing/merge_nodes/merged_cyclone_objects.txt"
    SLP_NODES_PATH = "/cw3e/mead/projects/csg101/aillenden/postprocessing/merge_nodes/merged_circulation_objects.txt"
    OUTPUT_DIR = "/cw3e/mead/projects/csg101/aillenden/plots/wy2015/variable_objects/"

    DIRECTIONS = {'North': 55, 'East': 250, 'South': 20, 'West': 200}
    DATA_BOUNDS = {'latitude': slice(15.0, 60.0), 'longitude': slice(165, 250)}

    print("=" * 50)
    print("Loading event dates...")
    print("=" * 50)

    df_events = pd.read_csv(EVENTS_CSV_PATH)
    df_events['Start_Date'] = pd.to_datetime(df_events['Start_Date'])
    df_events['End_Date'] = pd.to_datetime(df_events['End_Date'])

    print("Looping over events...")
    for _, row in df_events.iterrows():
        event_id = row.iloc[0]
        start_dt = row['Start_Date']
        end_dt = row['End_Date']

        main_files = generate_file_paths(
            start_dt.year, start_dt.month, start_dt.day, start_dt.hour,
            end_dt.year, end_dt.month, end_dt.day, end_dt.hour,
            base_path_main=BASE_PATH_MAIN
        )

        event_output_dir = os.path.join(OUTPUT_DIR, f"event_{event_id}")
        os.makedirs(event_output_dir, exist_ok=True)

        process_time_series(main_files,
                            ivt_blob_path=IVT_BLOB_PATH,
                            thetae_blob_path=THETAE_BLOB_PATH,
                            vort_nodes_path=VORT_NODES_PATH,
                            slp_nodes_path=SLP_NODES_PATH,
                            save_plots=True,
                            output_dir=event_output_dir,
                            directions=DIRECTIONS,
                            bounds=DATA_BOUNDS)

    print("All events processed.")
