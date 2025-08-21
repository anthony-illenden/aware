#!/bin/bash
#SBATCH --job-name="make_plots"
#SBATCH --output="make_plots.%j.%N.out.txt"
#SBATCH --partition=cw3e-compute
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
srun python plot_era5_variables.py

