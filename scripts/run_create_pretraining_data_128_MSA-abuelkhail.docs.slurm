#!/bin/sh
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=20GB
#SBATCH --time=4:00:00
#SBATCH --job-name=prepare_tf_data_128
#SBATCH --mail-type=ALL
#SBATCH --mail-user=gi372@nyu.edu
#SBATCH --output=output-run_create_pretraining_128_MSA-abuelkhail.docs.shard.%a-%A.out
#SBATCH --error=output-run_create_pretraining_128_MSA-abuelkhail.docs.shard.%a-%A.err


module purge
module load all

source activate camelbert

N=${SLURM_ARRAY_TASK_ID}

INPUT=../corpora/shards/MSA-abuelkhail.docs.shard.$(printf "%03d" ${N}).normalized.sents
OUTPUT=../corpora/tfrecord_wp-30k_msl-128/MSA-abuelkhail.docs.shard.$(printf "%03d" ${N}).tf_record

echo $INPUT
echo $OUTPUT

python ../bert/create_pretraining_data.py \
--input_file=$INPUT \
--output_file=$OUTPUT \
--vocab_file=../configs/bert-wordpiece-30k-vocab.txt \
--do_lower_case=False \
--do_whole_word_mask=True \
--max_seq_length=128 \
--max_predictions_per_seq=20 \
--random_seed=12345 \
--dupe_factor=10 \
--masked_lm_prob=0.15 \
--short_seq_prob=0.1

