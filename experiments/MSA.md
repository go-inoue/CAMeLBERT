# MSA

## Data
- Abu El-Khair Corpus [[paper](https://arxiv.org/pdf/1611.04033.pdf)]
- 

## Pre-training BERT on Google Cloud Platform
### Data Preparation
- 
### Set up VM on Google Cloud Platform
- We use `n1-standard-1`.
    - vCPUs: 1
    - Memory: 3.75 GB
    - Cost: $0.0523/hour at `euroupe-west4`
- We use `v3-8` TPU.

#### 1. Set up a VM.
```bash
gcloud compute instances create camel-bert-msa \
    --zone=europe-west4-a \
    --machine-type=n1-standard-1 \
    --image-project=ml-images \
    --image-family=tf-1-15 \
    --scopes=cloud-platform \
    --no-address
```

#### 2. Set up TPU.
```bash
gcloud compute tpus create camel-bert-msa \
    --zone=europe-west4-a \
    --network=default \
    --version=1.15.3  \
    --accelerator-type=v3-8
```

#### 3. ssh into the VM and download scripts.
```bash
gcloud compute ssh camel-bert-msa --zone=europe-west4-a

git clone https://github.com/go-inoue/CAMeLBERT.git
```

#### 4. Run pre-training with max sequence length of 128 tokens.
```bash
nohup python bert/run_pretraining.py \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-128/MSA* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/model/bert-base-config.json \
    --train_batch_size=1024 \
    --max_seq_length=128 \
    --max_predictions_per_seq=20 \
    --num_train_steps=1000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=1000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-msa \
    --num_tpu_cores=8 \
> output-run_pretraining_bert-base-wp-30k_msl-128-MSA.out \
2> output-run_pretraining_bert-base-wp-30k_msl-128-MSA.err &
```

#### 5. Run pre-training with max sequence length of 512 tokens.
```bash
nohup python bert/run_pretraining.py \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-512/MSA* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-512-MSA \
    --init_checkpoint=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA/model.ckpt-900000 \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/model/bert-base-config.json \
    --train_batch_size=256 \
    --max_seq_length=512 \
    --max_predictions_per_seq=80 \
    --num_train_steps=100000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=1000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-msa \
    --num_tpu_cores=8 \
> output-run_pretraining_bert-base-wp-30k_msl-512-MSA.out \
2> output-run_pretraining_bert-base-wp-30k_msl-512-MSA.err &
```