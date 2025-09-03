import xarray as xr
import os

def merge_nc_dir_to_file(input_dir, output_file, chunks={'time': 10}):
    """
    Merge all NetCDF files in a directory into one NetCDF file.

    Parameters:
        input_dir (str): Directory containing NetCDF files.
        output_file (str): Path to save the merged NetCDF.
        chunks (dict): Chunking for Dask (optional, improves memory handling).
    """
    files = sorted([os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.nc')])
    if not files:
        print(f"No NetCDF files found in {input_dir}")
        return None

    # Open multiple files as one dataset with lazy loading
    ds = xr.open_mfdataset(files, combine='by_coords', chunks=chunks)

    # Save to a single NetCDF
    ds.to_netcdf(output_file)
    print(f"Merged {len(files)} files from {input_dir} into {output_file}")
    return output_file


if __name__ == "__main__":
    print("="*50)
    print("Script is running...")
    print("="*50)
    
    # Input
    ar_dir = "/cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/detect_blobs/ar_objects/"
    
    # Output
    ar_out = "merged_ar.nc"
    
    # Merge
    merge_nc_dir_to_file(ar_dir, ar_out)
    
    print("="*50)
    print("Script is complete!")
    print("="*50)
