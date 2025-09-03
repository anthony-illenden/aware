#!/bin/bash
#SBATCH --job-name="pv_nodes"
#SBATCH --output="pv_nodes.%j.%N.out.txt"
#SBATCH --partition=shared-192
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

DetectNodes \
    --in_data_list /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/wy2015_extra_era5_paths.txt \
    --out /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/detect_nodes/pv_objects/possible_pv_objects \
    --mergedist 5.0 \
    --searchbymax "pv_925" \
    --closedcontourcmd "pv_925,1.5,1.0,0" \
    --maxlat 55.0 \
    --minlat 20.0 \
    --minlon 200 \
    --maxlon 250 \
    --regional \
    --timefilter "3hr" \
    --outputcmd "pv_925,max,0"

rm -f /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/log*.txt
