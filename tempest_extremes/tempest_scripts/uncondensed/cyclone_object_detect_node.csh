#!/bin/csh

DetectNodes \
    --in_data_list /expanse/nfs/cw3e/csg101/aillenden/python_scripts/wy2015_era5_paths \
    --out /expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/tempest_output/detect_nodes/wy2015/cyclone/wy2015_cyclone_candidates.txt \
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
