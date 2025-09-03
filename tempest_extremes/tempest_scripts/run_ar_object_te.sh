#!/bin/bash
#SBATCH --job-name="ar_objects"
#SBATCH --output="ar_objects.%j.%N.out.txt"
#SBATCH --partition=shared-192
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --export=ALL
#SBATCH --account=csg101
#SBATCH --time=1:00:00
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=aillenden@ucsd.edu
#######################################################

# Run DetectBlobs
DetectBlobs \
    --in_data_list /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/wy2015_extra_era5_paths.txt \
    --out /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/detect_blobs/ar_objects/possible_objects \
    --thresholdcmd "IVT,>=,500,0" \
    --geofiltercmd "area,>=,5e4km2" \
    --lonname "longitude" \
    --latname "latitude" \
    --maxlat 55.0 \
    --minlat 20.0 \
    --minlon 165 \
    --maxlon 250 \
    --regional \
    --timefilter "3hr"

rm -f /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/log*.txt

# Merge DetectBlobs output into one netCDF 
source activate thesis 
python /cw3e/mead/projects/csg101/aillenden/tempest_extremes/python_scripts/merge_ar_objects.py

# Write paths from DetectBlobs output
python /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/scripts/generate_ar_objects_paths.py

# Run StitchBlobs
#StitchBlobs \
#    --in_list /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/ar_objects_detect_blobs_paths.txt \
#    --out /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_output/stitch_blobs/ar_objects/stitch_ar_objects_wy2015.nc \
#    --var "binary_tag" \
#    --mintime 3h \
#    --lonname "longitude" \
#    --latname "latitude"

#rm -f /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/log*.txt
