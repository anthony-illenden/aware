import os

def concatenate_txt_files(dir1):
    # Output file names
    output_file1 = '/cw3e/mead/projects/csg101/aillenden/tempest_extremes/python_output/merged_cyclone_objects.txt'

    # Create or overwrite the output files
    with open(output_file1, 'w') as output1:
        # Concatenate files from dir1 into output_file1 (cyclone objects)
        for file_name in os.listdir(dir1):
            if file_name.endswith('.dat'):
                file_path = os.path.join(dir1, file_name)
                with open(file_path, 'r') as f:
                    output1.write(f.read())  # Directly write contents to output file
    print(f"Concatenated files from {dir1} into {output_file1}")

# Only run the script if this file is being executed directly (not imported)
if __name__ == '__main__':
    dir1 = '/cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/detect_nodes/cyclone_objects/'
    concatenate_txt_files(dir1)
