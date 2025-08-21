#!/bin/csh

DetectBlobs \
    --in_data_list /expanse/nfs/cw3e/csg101/aillenden/wy_era5/paths/wy2015_extra_vars_paths.txt \
    --out /expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/tempest_output/detect_blobs/vort/candiadates \
    --thresholdcmd "vort_925,>=,10,0.5" \
    --geofiltercmd "area,>=,1500km2;area,<=,100000km2" \
    --lonname "longitude" \
    --latname "latitude" \
    --maxlat 60.0 \
    --minlat 15.0 \
    --minlon 165 \
    --maxlon 250 \
    --timefilter "3hr"
