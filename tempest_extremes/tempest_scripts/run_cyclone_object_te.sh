#!/bin/bash
#SBATCH --job-name="cyclone_objects"
#SBATCH --output="cyclone_objects.%j.%N.out.txt"
#SBATCH --partition=compute-192
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --export=ALL
#SBATCH --account=csg101
#SBATCH --time=1:00:00
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=aillenden@ucsd.edu
#######################################################

# Run DetectNodes
DetectNodes \
    --in_data_list /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/wy2015_era5_paths.txt \
    --out /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/detect_nodes/cyclone_objects/possible_objects \
    --mergedist 0.5 \
    --searchbymin "MSLP" \
    --lonname "longitude" \
    --latname "latitude" \
    --maxlat 60.0 \
    --minlat 15.0 \
    --minlon 165 \
    --maxlon 250 \
    --timefilter "3hr" \
    --outputcmd "MSLP,min,0"

rm -f /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/log*.txt

# Merge DetectNodes output into one txt file
source activate thesis
python /cw3e/mead/projects/csg101/aillenden/tempest_extremes/python_scripts/merge_cyclone_txt.py

# Write paths from DetectNodes output
python /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/scripts/generate_cyclone_objects_paths.py

# Run StitchNodes
csh /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/uncondensed/cyclone_object_stitch_nodes.csh
rm -f /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/log*.txt