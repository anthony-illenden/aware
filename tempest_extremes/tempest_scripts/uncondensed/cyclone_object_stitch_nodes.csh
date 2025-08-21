#!/bin/csh

StitchNodes \
    --in_list /expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/python_scripts/corrected_wy2015_tempest_stitch_cyclone_paths.txt \
    --in_fmt "lon,lat,MSLP" \
    --out /expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/tempest_output/stitch_nodes/wy2015/corrected_slp.txt \
    --mintime 12h