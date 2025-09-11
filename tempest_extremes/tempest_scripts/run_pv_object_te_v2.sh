#!/bin/bash
#SBATCH --job-name="pv_objects"
#SBATCH --output="pv_objects.%j.%N.out.txt"
#SBATCH --partition=shared-128
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --export=ALL
#SBATCH --account=csg101
#SBATCH --time=1:00:00
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=aillenden@ucsd.edu
#######################################################

# Run DetectNodes
DetectNodes \
    --in_data_list /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/wy2015_extra_era5_paths.txt \
    --out /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/detect_nodes/pv_objects/possible_pv_objects \
    --mergedist 5 \
    --searchbymax "pv_925" \
    --closedcontourcmd "pv_925,-0.5,2,0" \
    --lonname "longitude" \
    --latname "latitude" \
    --maxlat 60.0 \
    --minlat 30.0 \
    --minlon 200 \
    --maxlon 250 \
    --regional \
    --timefilter "3hr" \
    --outputcmd "pv_925,max,0"

rm -f /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/log*.txt

# Write paths from DetectNodes output
python /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/scripts/generate_pv_detect_nodes_paths.py

# Run StitchNodes
StitchNodes \
    --in_list /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/pv_objects_detect_nodes_paths.txt \
    --in_fmt "lon,lat,pv_925" \
    --out /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/stitch_nodes/pv_objects/pv_objects_stitch_paths.txt \
    --mintime 6h \
    --maxgap 1 \
    --min_endpoint_dist 5

# Activate thesis Python environment for PV plots
source activate thesis

# Run Python script that plots PV and DetectNodes
python /cw3e/mead/projects/csg101/aillenden/plots/wy2015/pv_field/plot_detect_nodes.py


