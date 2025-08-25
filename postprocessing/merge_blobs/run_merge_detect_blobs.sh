#!/bin/bash
#SBATCH --job-name="merge_blobs"
#SBATCH --output="merge_blobs.%j.%N.out.txt"
#SBATCH --partition=compute-192
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --export=ALL
#SBATCH --account=csg101
#SBATCH --time=04:00:00
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=aillenden@ucsd.edu
#######################################################
source activate thesis
srun python merge_detect_blobs_export_csv.py

