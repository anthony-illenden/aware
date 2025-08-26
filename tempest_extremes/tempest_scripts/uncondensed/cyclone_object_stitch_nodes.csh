#!/bin/csh

StitchNodes \
    --in_list /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/cyclone_objects_detect_nodes_paths.txt \
    --in_fmt "lon,lat,MSLP" \
    --out /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/stitch_nodes/cyclone_objects/slp_mins_wy2015.txt \
    --mintime 3h