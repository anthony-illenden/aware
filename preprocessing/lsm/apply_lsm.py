import os
import xarray as xr

ds_lsm = xr.open_dataset("/cw3e/mead/projects/csg101/aillenden/preprocessing/lsm/era5_landmask.nc")

# Input and output directories
data_dir = "/cw3e/mead/projects/csg101/aillenden/era5_data/wy2015_extra/"

for filename in os.listdir(data_dir):
    if filename.endswith(".nc"):
        file_path = os.path.join(data_dir, filename)
        ds = xr.open_dataset(file_path)
        # Apply the LSM filter using ds_lsm
        ds_filtered = ds.where(ds_lsm['LSM'] <= 0)
        # Overwrite the original file with the filtered data
        ds_filtered.to_netcdf(file_path)
        ds.close()
        ds_filtered.close()