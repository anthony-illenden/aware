#!/bin/csh 

StitchBlobs \
    --in_list /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/ar_objects_detect_blobs_paths.txt \
    --out /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/stitch_blobs/ar_objects/stitch_ar_objects_wy2015.nc \
    --var "binary_tag" \
    --mintime 3h \
    --lonname "longitude" \
    --latname "latitude"