# MSA

## Data
- Abu El-Khair Corpus [[paper](https://arxiv.org/pdf/1611.04033.pdf)]
- 

## Pre-training BERT on Google Cloud Platform
### Data Preparation
- 
### Set up VMs on Google Cloud Platform
- We use `n1-standard-2` for running the pre-training script.
    - vCPUs: 4
    - Memory: 7.5 GB
    - Cost: $0.1046/hour at `euroupe-west4`
    - Note: If you're training only one model, you can use a lower spec model such as `n1-standard-1`.
    In our case, we run five concurrent pre-training scripts, which requires more memory.
- We use `f1-micro` for downloading model files from GCS to VM, then VM to Google Drive.
    - vCPUs: 1
    - Memory: 0.6 GB
    - Cost: $0.0084/hour at `euroupe-west4`
    - Note: You won't get charged for data transfer between GCS and VM in the same region, and between VM and Google Drive. Note that you will get charged if you directly move files from GCS to Google Drive with `gsuil` command. You can move files from GCS to Google Drive for free if you first move files from GCS to VM, then move files from VM to Google Drive. We create a new VM instance for transfer purpose only, so that the process won't interupt the main pre-training script.
- We use `v3-8` TPU.
    - The location of TPU should be the same as the region of VM so that you can transfer data for no charge.

#### 1. Set up a VM.
```bash
# Set project name
gcloud config set project camelbert

# Create a VM instance for pre-training
gcloud compute instances create camel-bert \
    --zone=europe-west4-a \
    --machine-type=n1-standard-2 \
    --image-project=ml-images \
    --image-family=tf-1-15 \
    --scopes=cloud-platform \
    --no-address
```

#### 2. Set up TPU nodes.
```bash
# Create a TPU instance
gcloud compute tpus create camel-bert-1 \
    --zone=europe-west4-a \
    --network=default \
    --version=1.15.3 \
    --accelerator-type=v3-8
    
gcloud compute tpus create camel-bert-2 \
    --zone=europe-west4-a \
    --network=default \
    --version=1.15.3 \
    --accelerator-type=v3-8

gcloud compute tpus create camel-bert-3 \
    --zone=europe-west4-a \
    --network=default \
    --version=1.15.3 \
    --accelerator-type=v3-8

gcloud compute tpus create camel-bert-4 \
    --zone=europe-west4-a \
    --network=default \
    --version=1.15.3 \
    --accelerator-type=v3-8

gcloud compute tpus create camel-bert-5 \
    --zone=europe-west4-a \
    --network=default \
    --version=1.15.3 \
    --accelerator-type=v3-8
```

#### 3. ssh into the VM and download scripts.
```bash
gcloud compute ssh camel-bert --zone=europe-west4-a

# Install htop for monitoring purpose
sudo apt install htop

# Download pre-training script
git clone https://github.com/go-inoue/CAMeLBERT.git
cd CAMeLBERT
```

#### 4. Run pre-training with max sequence length of 128 tokens.
- MSA-full
```bash
# Make sure that the following hyperparameters are the same as the original paper
# The number of tokens in a batch is 131,072. This number stays the same across different max length.
# -> train_batch_size=1024, max_seq_length=128
# Make num_train_steps a large number. This is a global step, meaning you can re-start pre-training from an arbitrary checkpoint up untill this number of steps.
# -> num_train_steps=5000000

# Run pre-training on background
nohup python bert/run_pretraining.py \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-128/MSA* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-full \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/configs/bert-base-config.json \
    --train_batch_size=1024 \
    --max_seq_length=128 \
    --max_predictions_per_seq=20 \
    --num_train_steps=5000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=5000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-1 \
    --num_tpu_cores=8 \
> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-full.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-full.err &
```
- MSA-half
```bash
# Run pre-training on background
nohup python bert/run_pretraining.py \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-128/MSA*half* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-half \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/configs/bert-base-config.json \
    --train_batch_size=1024 \
    --max_seq_length=128 \
    --max_predictions_per_seq=20 \
    --num_train_steps=5000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=5000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-2 \
    --num_tpu_cores=8 \
> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-half.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-half.err &
```
- MSA-quarter
```bash
# Run pre-training on background
nohup python bert/run_pretraining.py \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-128/MSA*quarter* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-quarter \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/configs/bert-base-config.json \
    --train_batch_size=1024 \
    --max_seq_length=128 \
    --max_predictions_per_seq=20 \
    --num_train_steps=5000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=5000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-3 \
    --num_tpu_cores=8 \
> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-quarter.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-quarter.err &
```
- MSA-eighth
```bash
# Run pre-training on background
nohup python bert/run_pretraining.py \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-128/MSA*eighth* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-eighth \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/configs/bert-base-config.json \
    --train_batch_size=1024 \
    --max_seq_length=128 \
    --max_predictions_per_seq=20 \
    --num_train_steps=5000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=5000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-4 \
    --num_tpu_cores=8 \
> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-eighth.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-eighth.err &
```
- MSA-sixteenth
```bash
# Run pre-training on background
nohup python bert/run_pretraining.py \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-128/MSA*sixteenth* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-sixteenth \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/configs/bert-base-config.json \
    --train_batch_size=1024 \
    --max_seq_length=128 \
    --max_predictions_per_seq=20 \
    --num_train_steps=5000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=5000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-5 \
    --num_tpu_cores=8 \
> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-sixteenth.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-sixteenth.err &
```

- Download model files from GCS to a VM and upload them to Google Drive.

```bash
# Create a VM instance
gcloud compute instances create gcs-vm-gdrive \
    --zone=europe-west4-a \
    --machine-type=f1-micro \
    --scopes=cloud-platform \
    --no-address

# ssh into the VM instnace
gcloud compute ssh gcs-vm-gdrive --zone=europe-west4-a

# Install unzip for rclone installation
sudo apt install unzip htop

# Install rclone for uploading files to Google Drive
curl https://rclone.org/install.sh | sudo bash

# Configure rclone
rclone config

# Make temporary directories for moving files
mkdir full half quarter eighth sixteenth

for i in {0..1000000..100000}; do
  for s in full half quarter eighth sixteenth; do
  # Download files from GCS
  gsutil mv gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-$s/model.ckpt-$i.* $s/

  # Upload files to Google Drive (750GB per day is the limit) 
  rclone move $s/model.ckpt-$i.index gdrive:CAMeLBERT/model/bert-base-wp-30k_msl-128-MSA-$s/ --verbose
  rclone move $s/model.ckpt-$i.meta gdrive:CAMeLBERT/model/bert-base-wp-30k_msl-128-MSA-$s/ --verbose
  rclone move $s/model.ckpt-$i.data-00000-of-00001 gdrive:CAMeLBERT/model/bert-base-wp-30k_msl-128-MSA-$s/ --drive-chunk-size 128M --verbose
  done
done
```

#### Resume pre-training from a certain checkpoint due to the error occurred at 291000 for MSA-eighth, 322000 for MSA-sixteenth, 417000 for MSA-quarter
- MSA-eighth
```bash
# Resume pre-training from a specific checkpoint
# The following script starts from 290000, not 291000 to make sure that the ckeckpoint does not have any issue.
# Make sure to update the file named `checkpoint` accordingly.
# Specifically, you need to update the number specified in the first line.
nohup python bert/run_pretraining.py \
    --init_checkpoint=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-eighth/model.ckpt-290000 \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-128/MSA*eighth* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-eighth \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/configs/bert-base-config.json \
    --train_batch_size=1024 \
    --max_seq_length=128 \
    --max_predictions_per_seq=20 \
    --num_train_steps=5000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=5000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-4 \
    --num_tpu_cores=8 \
> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-eighth-from-290000.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-eighth-from-290000.err &
```
- MSA-sixteenth
```bash
# Resume pre-training from a specific checkpoint
# The following script starts from 321000, not 322000 to make sure that the ckeckpoint does not have any issue.
# Make sure to update the file named `checkpoint` accordingly.
# Specifically, you need to update the number specified in the first line.
nohup python bert/run_pretraining.py \
    --init_checkpoint=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-sixteenth/model.ckpt-321000 \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-128/MSA*sixteenth* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-sixteenth \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/configs/bert-base-config.json \
    --train_batch_size=1024 \
    --max_seq_length=128 \
    --max_predictions_per_seq=20 \
    --num_train_steps=5000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=5000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-5 \
    --num_tpu_cores=8 \
> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-sixteenth-from-321000.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-sixteenth-from-321000.err &

- MSA-quarter
```bash
# Resume pre-training from a specific checkpoint
# The following script starts from 416000, not 417000 to make sure that the ckeckpoint does not have any issue.
# Make sure to update the file named `checkpoint` accordingly.
# Specifically, you need to update the number specified in the first line.
nohup python bert/run_pretraining.py \
    --init_checkpoint=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-quarter/model.ckpt-416000 \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-128/MSA*quarter* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-quarter \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/configs/bert-base-config.json \
    --train_batch_size=1024 \
    --max_seq_length=128 \
    --max_predictions_per_seq=20 \
    --num_train_steps=5000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=5000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-3 \
    --num_tpu_cores=8 \
> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-quarter-from-416000.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-quarter-from-416000.err &
```

#### 5. Run pre-training with max sequence length of 512 tokens.
```bash
# Make sure that the following hyperparameters are the same as the original paper.
# The number of tokens in a batch is 131,072. This number stays the same across different max length.
# -> train_batch_size=256, max_seq_length=512
# Do not forget to set max_predictions_per_seq 15% of max_seq_length, which is approximately 80.
# -> max_predictions_per_seq=80
# 
# Run pre-training on background
nohup python bert/run_pretraining.py \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-512/MSA* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-full \
    --init_checkpoint=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-full/model.ckpt-900000 \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/configs/bert-base-config.json \
    --train_batch_size=256 \
    --max_seq_length=512 \
    --max_predictions_per_seq=80 \
    --num_train_steps=5000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=1000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-1 \
    --num_tpu_cores=8 \
> experiments/output-run_pretraining_bert-base-wp-30k_msl-512-MSA-full.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-512-MSA-full.err &
```
