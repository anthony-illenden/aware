#!/bin/bash
#SBATCH --job-name="circ_dn"
#SBATCH --output="circ_dn.%j.%N.out.txt"
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
csh /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/uncondensed/circulation_object_detect_node.csh

rm -f /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/uncondensed/other/log*.txt