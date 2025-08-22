#!/bin/csh

DetectNodes \
    --in_data_list /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/wy2015_era5_paths.txt \
    --out /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/detect_nodes/circulation_objects/wy2015_possible_objects.txt \
    --mergedist 0.5 \
    --searchbymax "vort_925" \
    --thresholdcmd "vort_925,>=,15,0.5" \
    --lonname "longitude" \
    --latname "latitude" \
    --maxlat 60.0 \
    --minlat 15.0 \
    --minlon 165 \
    --maxlon 250 \
    --timefilter "3hr" \
    --outputcmd "vort_925,max,0"
