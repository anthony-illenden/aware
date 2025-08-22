#!/bin/bash
#SBATCH --job-name="tempest_extremes"
#SBATCH --output="tempest_extremes.%j.%N.out.txt"
#SBATCH --partition=compute-192
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --export=ALL
#SBATCH --account=csg101
#SBATCH --time=1:00:00
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=aillenden@ucsd.edu
#######################################################
csh /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/uncondensed/ar_object_detect_blobs.csh

rm -f /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/uncondensed/other/log*.txt