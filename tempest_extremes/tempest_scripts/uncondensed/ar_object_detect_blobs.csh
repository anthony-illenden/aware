#!/bin/csh

DetectBlobs \
    --in_data_list /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/wy2015_era5_paths.txt \
    --out /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/detect_blobs/ar_objects/possible_objects \
    --thresholdcmd "IVT,>=,250,0" \
    --geofiltercmd "area,>=,1e5km2" \
    --lonname "longitude" \
    --latname "latitude" \
    --maxlat 55.0 \
    --minlat 20.0 \
    --minlon 165 \
    --maxlon 250 \
    --timefilter "3hr"