import os

def concatenate_txt_files(dir1, dir2):
    # Output file names
    output_file1 = 'merged_cyclone_objects.txt'
    output_file2 = 'merged_circulation_objects.txt'

    # Create or overwrite the output files
    with open(output_file1, 'w') as output1, open(output_file2, 'w') as output2:
        # Concatenate files from dir1 into output_file1 (cyclone objects)
        for file_name in os.listdir(dir1):
            if file_name.endswith('.dat'):
                file_path = os.path.join(dir1, file_name)
                with open(file_path, 'r') as f:
                    output1.write(f.read())  # Directly write contents to output file

        # Concatenate files from dir2 into output_file2 (circulation objects)
        for file_name in os.listdir(dir2):
            if file_name.endswith('.dat'):
                file_path = os.path.join(dir2, file_name)
                with open(file_path, 'r') as f:
                    output2.write(f.read())  # Directly write contents to output file

    print(f"Concatenated files from {dir1} into {output_file1}")
    print(f"Concatenated files from {dir2} into {output_file2}")


# Only run the script if this file is being executed directly (not imported)
if __name__ == '__main__':
    dir1 = '/cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/detect_nodes/cyclone_objects/'
    dir2 = '/cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/detect_nodes/circulation_objects/'

    concatenate_txt_files(dir1, dir2)
