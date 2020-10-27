#!/bin/sh
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8GB
#SBATCH --time=00:30:00
#SBATCH --job-name=normalize_document_level_corpus
#SBATCH --mail-type=ALL
#SBATCH --mail-user=gi372@nyu.edu
#SBATCH --output=slurm-log_normalize_document_level_corpus_%A_%a.out
#SBATCH --error=slurm-log_normalize_document_level_corpus_%A_%a.err

module purge
module load all

source activate camelbert

N=${SLURM_ARRAY_TASK_ID}

INPUT=$1.shard.$(printf "%03d" ${N})

echo $INPUT

python preprocess_raw_text.py $INPUT > $INPUT.normalized

#rm $INPUT
