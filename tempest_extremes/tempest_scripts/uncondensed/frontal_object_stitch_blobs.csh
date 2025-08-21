#!/bin/csh

StitchBlobs \
    --in_list /expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/python_scripts/full_wy2015_frontal_objects_paths.txt \
    --out /expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/tempest_output/stitch_blobs/wy2015_frontal_objects.nc \
    --var "binary_tag" \
    --mintime 12h \
    --lonname "longitude" \
    --latname "latitude"
