#!/bin/sh
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=120GB
#SBATCH --time=6:00:00
#SBATCH --job-name=sentence_split
#SBATCH --mail-type=ALL
#SBATCH --mail-user=gi372@nyu.edu


module purge
module load all

source activate camelbert

python sentence_split.py $1 > $2
