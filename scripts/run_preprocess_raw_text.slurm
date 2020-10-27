#!/bin/sh
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=120GB
#SBATCH --time=6:00:00
#SBATCH --job-name=preprocess
#SBATCH --mail-type=ALL
#SBATCH --mail-user=gi372@nyu.edu


module purge
module load all

source activate camelbert

python preprocess_raw_text.py $1 > $2
