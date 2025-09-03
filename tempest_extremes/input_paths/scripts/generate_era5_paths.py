import os

def list_files(input_dir, output_dir, output_filename):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Combine output directory and filename
    output_path = os.path.join(output_dir, output_filename)
    
    with open(output_path, 'w') as f:
        for root, _, files in os.walk(input_dir):
            files.sort()
            for file in files:
                f.write(os.path.join(root, file) + '\n')

if __name__ == "__main__":
    print("="*50)
    print("Script is running...")
    print("="*50)

    wy = "2015"  # Water year 
    input_dir = f"/cw3e/mead/projects/csg101/aillenden/era5_data/wy{wy}_extra/"
    output_dir = "/cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/"
    output_filename = f"wy{wy}_extra_era5_paths.txt"
    list_files(input_dir, output_dir, output_filename)

    print("="*50)
    print("Script is complete!")
    print("="*50)
