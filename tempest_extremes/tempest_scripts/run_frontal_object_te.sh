#!/bin/bash
#SBATCH --job-name="frontal_objects"
#SBATCH --output="frontal_objects.%j.%N.out.txt"
#SBATCH --partition=shared-128
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
    
rm -f /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/log*.txt

# Write paths from DetectBlobs output
#source activate thesis
#python /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/scripts/generate_frontal_objects_paths.py

# Run StitchBlobs
#csh /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/uncondensed/frontal_object_stitch_blobs.csh
#rm -f /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/log*.txt


