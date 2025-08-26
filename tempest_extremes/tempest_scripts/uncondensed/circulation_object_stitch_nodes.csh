#!/bin/csh

StitchNodes \
    --in_list /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/circulation_objects_detect_nodes_paths.txt \
    --in_fmt "lon,lat,vort_925" \
    --out /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/stitch_nodes/circulation_objects/circulations_wy2015.txt \
    --mintime 12h