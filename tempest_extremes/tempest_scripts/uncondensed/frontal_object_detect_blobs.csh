#!/bin/csh

DetectBlobs \
    --in_data_list /expanse/nfs/cw3e/csg101/aillenden/python_scripts/wy2015_era5_paths \
    --out /expanse/nfs/cw3e/csg101/aillenden/tempest_extremes/tempest_output/detect_blobs/frontal/ \
    --thresholdcmd "thetae_grad,>=,7.5,0" \
    --geofiltercmd "area,>=,1000km2" \
    --lonname "longitude" \
    --latname "latitude" \
    --maxlat 60.0 \
    --minlat 15.0 \
    --minlon 165 \
    --maxlon 250 \
    --timefilter "3hr"
