#!/bin/sh
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64GB
#SBATCH --time=6:00:00
#SBATCH --job-name=train_wordpiece_tokznier
#SBATCH --mail-type=ALL
#SBATCH --mail-user=gi372@nyu.edu


module purge
module load all

source activate camelbert

python train_bert_wordpiece.py \
--files '../corpora/shards/*.sents' \
--out ../model \
--name bert-wordpiece-30k
