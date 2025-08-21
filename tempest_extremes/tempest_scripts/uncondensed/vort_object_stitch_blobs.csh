#!/bin/csh

StitchBlobs \
    --in_list /expanse/nfs/cw3e/csg101/aillenden/vort_candiates_paths.txt \
    --out /expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/tempest_output/stitch_blobs/vort_candidates_stitched.nc \
    --var "binary_tag" \
    --mintime 12h \
    --lonname "longitude" \
    --latname "latitude"

