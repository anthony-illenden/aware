#!/bin/bash
#SBATCH --job-name="merge_pv"
#SBATCH --output="merge_pv.%j.%N.out.txt"
#SBATCH --partition=shared-192
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --export=ALL
#SBATCH --account=csg101
#SBATCH --time=0:30:00
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=aillenden@ucsd.edu
#######################################################
source activate thesis
srun python merge_pv_nodes_txt.py

