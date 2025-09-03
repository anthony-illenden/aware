#!/bin/bash
#SBATCH --job-name="download_era5"
#SBATCH --output="download_era5.%j.%N.out.txt"
#SBATCH --partition=shared-128
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --export=ALL
#SBATCH --account=csg101
#SBATCH --time=8:00:00
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=aillenden@ucsd.edu
#######################################################
source activate thesis
srun python download_era5_thredds.py

