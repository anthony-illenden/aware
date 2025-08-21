#!/bin/csh 

StitchBlobs --in_list /expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/python_scripts/wy2015_tempest_ar_objects_paths.txt  --out /expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/tempest_output/stitch_blobs/updated_wy2015_ar_objects_stitched.nc --var "binary_tag" --mintime 12h --lonname "longitude" --latname "latitude"
