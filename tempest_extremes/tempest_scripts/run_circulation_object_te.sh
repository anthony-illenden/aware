#!/bin/bash
#SBATCH --job-name="circulation_objects"
#SBATCH --output="circulation_objects.%j.%N.out.txt"
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

# Run DetectNodes
csh /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/uncondensed/circulation_object_detect_node.csh
rm -f /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/log*.txt

# Write paths from DetectNodes output
source activate thesis
python /cw3e/mead/projects/csg101/aillenden/tempest_extremes/input_paths/scripts/generate_circulation_objects_paths.py

# Run StitchNodes
csh /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/uncondensed/circulation_object_stitch_nodes.csh
rm -f /cw3e/mead/projects/csg101/aillenden/tempest_extremes/tempest_scripts/log*.txt