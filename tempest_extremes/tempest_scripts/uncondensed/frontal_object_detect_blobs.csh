#!/bin/csh

DetectBlobs \
    --in_data_list /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/wy2015_era5_paths.txt \
    --out /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/detect_blobs/frontal_objects/possible_objects \
    --thresholdcmd "thetae_grad,>=,7.5,0" \
    --geofiltercmd "area,>=,1000km2" \
    --lonname "longitude" \
    --latname "latitude" \
    --maxlat 60.0 \
    --minlat 30.0 \
    --minlon 213 \
    --maxlon 250 \
    --timefilter "3hr"
