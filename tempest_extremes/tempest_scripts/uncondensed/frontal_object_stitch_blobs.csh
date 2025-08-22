#!/bin/csh 

StitchBlobs \
    --in_list /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/frontal_objects_detect_blobs_paths.txt \
    --out /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/stitch_blobs/frontal_objects/stitch_frontal_objects_wy2015.nc \
    --var "binary_tag" \
    --mintime 6h \
    --lonname "longitude" \
    --latname "latitude"