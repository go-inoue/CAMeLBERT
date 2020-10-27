#!/bin/sh
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4GB
#SBATCH --time=2:00:00
#SBATCH --job-name=array_transliterate
#SBATCH --mail-type=ALL
#SBATCH --mail-user=gi372@nyu.edu


module purge
module load all

source activate camelbert

N=${SLURM_ARRAY_TASK_ID}

INPUT=$1.$(printf "%03d" ${N})
OUTPUT=$1.ar.$(printf "%03d" ${N})

echo $INPUT
echo $OUTPUT

camel_transliterate -s bw2ar -o $OUTPUT $INPUT
