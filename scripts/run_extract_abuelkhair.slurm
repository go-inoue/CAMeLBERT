#!/bin/sh
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=64GB
#SBATCH --time=3:00:00
#SBATCH --job-name=preprocess
#SBATCH --mail-type=ALL
#SBATCH --mail-user=gi372@nyu.edu


module purge
module load all

source activate camelbert

for f in ../downloads/abuelkahir/*.xml; do
    python extract_xml.py $f Text > $f.docs
done

