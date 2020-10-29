
cd ../log/output-run_create_pretraining_128_MSA.slurm
grep -nr 'tensorflow:Wrote' . | \
sed 's/\.\/output-run_create_pretraining_128_//' | \
sed 's/\.err:396:INFO:tensorflow:Wrote//' | \
sed 's/-217\([0-9]\)\{4\}/.normalized.sents/' | \
sed 's/ total instances//' | \
sed 's/shards/shard/' | \
tr ' ' \\t | sort > ../../experiments/tmp.tsv
cd ../../scripts

join -t $'\t' -j 1 ../experiments/tmp.tsv ../experiments/split/MSA.tsv \
> ../experiments/MSA-number_of_tf_instances.tsv

rm ../experiments/tmp.tsv