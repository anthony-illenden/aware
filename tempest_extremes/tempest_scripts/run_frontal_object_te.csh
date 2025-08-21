#!/bin/csh

# Detect blobs
/expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/tempest_scripts/frontal_object_detect_blobs.csh

# Generate input file w/ detect blobs output for stitch blobs
python /expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/python_scripts/write_frontal_objects_paths.py

# Stitch blobs
/expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/tempest_scripts/frontal_object_stitch_blobs.csh


