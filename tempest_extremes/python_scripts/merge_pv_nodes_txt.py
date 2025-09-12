import os
from collections import defaultdict

def merge_dat_files(input_dir, output_file):
    merged = defaultdict(list)

    # Loop through files in directory
    for file_name in sorted(os.listdir(input_dir)):
        if file_name.endswith('.dat'):
            file_path = os.path.join(input_dir, file_name)
            with open(file_path, 'r') as f:
                lines = f.readlines()

            i = 0
            while i < len(lines):
                parts = lines[i].split()
                if len(parts) == 5:  # header line
                    year, month, day, nobj, hour = map(int, parts)
                    header = (year, month, day, hour)
                    objs = []
                    for _ in range(nobj):
                        i += 1
                        if i < len(lines):
                            objs.append(lines[i].strip())
                    merged[header].extend(objs)
                i += 1

    # Write out merged file
    with open(output_file, 'w') as out:
        for (year, month, day, hour), objs in sorted(merged.items()):
            out.write(f"{year}\t{month}\t{day}\t{len(objs)}\t{hour}\n")
            for obj in objs:
                out.write(f"\t{obj}\n")
            out.write("\n")

    print(f"Merged {len(merged)} time blocks into {output_file}")


if __name__ == '__main__':
    input_dir = '/cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/detect_nodes/pv_ivt_objects/'
    output_file = '/cw3e/mead/projects/csg101/aillenden/tempest_extremes/python_output/merged_pv_ivt_objects.txt'
    merge_dat_files(input_dir, output_file)
