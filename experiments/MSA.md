# MSA

## Data
- Abu El-Khair Corpus [[paper](https://arxiv.org/pdf/1611.04033.pdf)]
- Wikipedia (2019-0201)
- Arabic Gigaword Fifth Edition
- OSCAR (unshuffled)
- OSIAN
- MSA labeled samples in data collected by Nurpeiis Baimukan for dialectal identification task

### Preprocessing
- Remove non-printing characters.
- Remove lines without any Arabic characters.
- Remove diacritics and kashida.
- Heuristic sentence split.

## Pre-training BERT on Google Cloud Platform
### Notes and tips on Google Cloud Platform
- You have $300 free credit for 12 months upon registration.
- You may be eligible for TensorFlow Research Cloud (TFRC) Program, which allows free access to five on-demand v3-8 TPUs, five on-demand v2-8 TPUs, and 100 preemptible Cloud TPU v2-8 for one month.
- You may get extended access to TPUs once your trial period has ended, if you have a compelling reason to do so.
- You will not be charged as long as you are using a normal account, however, to use TPUs, you need to make your account billable. This means that you will be charged for the usage that exceeds $300 credit.
- Google Cloud Console has a usage limit of 50 hours per week.
- Make sure to set up your TPU instance, VM instance, and Cloud Storage bucket in the same region.
- Make sure to set up Cloud NAT, otherwise, your VM instance will not have access to Internet.
- To move files from Google Cloud Storage to Google Drive, the cheapest way is to set up a small VM instance, and download files from Google Cloud Storage to the instance, and then upload the files from the instance to Google Drive. There will be no charge.
- The most expensive component in pre-training a BERT model is data storage in Google Cloud Storage.

### Data Preparation

### Upload files to Google Cloud Storage
- `camelbert/data/tfrecord_wp-30k_msl-128`
   - First file: `MSA-abuelkhail.docs.shard.000.tf_record`
     - Created time: `Oct 27, 2020, 4:34:37 AM`
   - Last file: `MSA-osian.lines.shard.023.tf_record`
     - Created time: `Oct 27, 2020, 8:44:54 AM`
- `camelbert/data/tfrecord_wp-30k_msl-512`
   - First file: `MSA-abuelkhail.docs.shard.000.tf_record`
     - Created time: `Nov 1, 2020, 11:00:19 PM`
   - Last file: `MSA-osian.lines.shard.023.tf_record`
     - Created time: `Nov 2, 2020, 7:01:05 AM`

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
- MSA-eighth, from 290000
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
- MSA-sixteenth, from 321000
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

- MSA-quarter, from 416000
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

- MSA-sixteenth, from 417000
```bash
# Resume pre-training from a specific checkpoint
# The following script starts from 417000
# Make sure to update the file named `checkpoint` accordingly.
# Specifically, you need to update the number specified in the first line.
nohup python bert/run_pretraining.py \
    --init_checkpoint=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-sixteenth/model.ckpt-417000 \
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
> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-sixteenth-from-417000.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-sixteenth-from-417000.err &
```

- MSA-quarter, from 427000
```bash
# Resume pre-training from a specific checkpoint
# The following script starts from 427000
# Make sure to update the file named `checkpoint` accordingly.
# Specifically, you need to update the number specified in the first line.
nohup python bert/run_pretraining.py \
    --init_checkpoint=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-quarter/model.ckpt-427000 \
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
> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-quarter-from-427000.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-quarter-from-427000.err &
```

- MSA-eighth, from 952000
```bash
# Resume pre-training from a specific checkpoint
# The following script starts from 952000, not 291000 to make sure that the ckeckpoint does not have any issue.
# Make sure to update the file named `checkpoint` accordingly.
# Specifically, you need to update the number specified in the first line.
nohup python bert/run_pretraining.py \
    --init_checkpoint=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-eighth/model.ckpt-952000 \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-128/MSA*eighth* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-eighth \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/configs/bert-base-config.json \
    --train_batch_size=1024 \
    --max_seq_length=128 \
    --max_predictions_per_seq=20 \
    --num_train_steps=1000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=5000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-4 \
    --num_tpu_cores=8 \
> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-eighth-from-952000.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-128-MSA-eighth-from-952000.err &
```

#### 5. Run pre-training with max sequence length of 512 tokens.
- Copy starting model checkpoints and update chekcpoint file

```bash
gsutil cp gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-full/model.ckpt-900000.* \
gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-full/

gsutil cp gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-half/model.ckpt-900000.* \
gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-half/

gsutil cp gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-quarter/model.ckpt-900000.* \
gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-quarter/

gsutil cp gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-eighth/model.ckpt-900000.* \
gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-eighth/

gsutil cp gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-sixteenth/model.ckpt-900000.* \
gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-sixteenth/

echo model_checkpoint_path: "model.ckpt-900000" > ./checkpoint
echo all_model_checkpoint_paths: "model.ckpt-900000" >> ./checkpoint

gsutil cp ./checkpoint gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-full/
gsutil cp ./checkpoint gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-half/
gsutil cp ./checkpoint gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-quarter/
gsutil cp ./checkpoint gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-eighth/
gsutil cp ./checkpoint gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-sixteenth/
```

- MSA-full
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
    --init_checkpoint=gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-full/model.ckpt-900000 \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/configs/bert-base-config.json \
    --train_batch_size=256 \
    --max_seq_length=512 \
    --max_predictions_per_seq=80 \
    --num_train_steps=1000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=1000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-1 \
    --num_tpu_cores=8 \
> experiments/output-run_pretraining_bert-base-wp-30k_msl-512-MSA-full-from-900000.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-512-MSA-full-from-900000.err &
```

- MSA-half
```bash
# Run pre-training on background
nohup python bert/run_pretraining.py \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-512/MSA*half* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-half \
    --init_checkpoint=gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-half/model.ckpt-900000 \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/configs/bert-base-config.json \
    --train_batch_size=256 \
    --max_seq_length=512 \
    --max_predictions_per_seq=80 \
    --num_train_steps=1000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=1000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-2 \
    --num_tpu_cores=8 \
> experiments/output-run_pretraining_bert-base-wp-30k_msl-512-MSA-half-from-900000.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-512-MSA-half-from-900000.err &
```

- MSA-quarter
```bash
# Run pre-training on background
nohup python bert/run_pretraining.py \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-512/MSA*quarter* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-quarter \
    --init_checkpoint=gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-quarter/model.ckpt-900000 \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/configs/bert-base-config.json \
    --train_batch_size=256 \
    --max_seq_length=512 \
    --max_predictions_per_seq=80 \
    --num_train_steps=1000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=1000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-3 \
    --num_tpu_cores=8 \
> experiments/output-run_pretraining_bert-base-wp-30k_msl-512-MSA-quarter-from-900000.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-512-MSA-quarter-from-900000.err &
```

- MSA-eighth
```bash
# Run pre-training on background
nohup python bert/run_pretraining.py \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-512/MSA*eighth* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-eighth \
    --init_checkpoint=gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-eighth/model.ckpt-900000 \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/configs/bert-base-config.json \
    --train_batch_size=256 \
    --max_seq_length=512 \
    --max_predictions_per_seq=80 \
    --num_train_steps=1000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=1000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-4 \
    --num_tpu_cores=8 \
> experiments/output-run_pretraining_bert-base-wp-30k_msl-512-MSA-eighth-from-900000.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-512-MSA-eighth-from-900000.err &
```

- MSA-sixteenth
```bash
# Run pre-training on background
nohup python bert/run_pretraining.py \
    --input_file=gs://camelbert/data/tfrecord_wp-30k_msl-512/MSA*sixteenth* \
    --output_dir=gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-sixteenth \
    --init_checkpoint=gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-sixteenth/model.ckpt-900000 \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$HOME/CAMeLBERT/configs/bert-base-config.json \
    --train_batch_size=256 \
    --max_seq_length=512 \
    --max_predictions_per_seq=80 \
    --num_train_steps=1000000 \
    --num_warmup_steps=10000 \
    --save_checkpoints_steps=1000 \
    --keep_checkpoint_max=1000 \
    --learning_rate=1e-4 \
    --use_tpu \
    --tpu_name=camel-bert-5 \
    --num_tpu_cores=8 \
> experiments/output-run_pretraining_bert-base-wp-30k_msl-512-MSA-sixteenth-from-900000.out \
2> experiments/output-run_pretraining_bert-base-wp-30k_msl-512-MSA-sixteenth-from-900000.err &
```


```bash
# Create a VM instance
gcloud compute instances create gcs-vm-gdrive-2 \
    --zone=europe-west4-a \
    --machine-type=f1-micro \
    --scopes=cloud-platform \
    --no-address

# ssh into the VM instnace
gcloud compute ssh gcs-vm-gdrive-2 --zone=europe-west4-a

# Install unzip for rclone installation
sudo apt install unzip htop

# Install rclone for uploading files to Google Drive
curl https://rclone.org/install.sh | sudo bash

# Configure rclone
rclone config

# Make temporary directories for moving files
mkdir full half quarter eighth sixteenth


for i in {401000..500000..1000}; do
  for s in full half quarter eighth sixteenth; do
  gsutil -o "GSUtil:parallel_thread_count=1" \
  -o "GSUtil:sliced_object_download_max_components=8" \
  mv gs://camelbert/model/bert-base-wp-30k_msl-128-MSA-$s/model.ckpt-$i.* $s/
  #sleep 1
  rclone move $s/model.ckpt-$i.index gdrive:CAMeLBERT/model/bert-base-wp-30k_msl-128-MSA-$s/ --verbose
  #sleep 1
  rclone move $s/model.ckpt-$i.meta gdrive:CAMeLBERT/model/bert-base-wp-30k_msl-128-MSA-$s/ --verbose
  #sleep 1
  rclone move $s/model.ckpt-$i.data-00000-of-00001 gdrive:CAMeLBERT/model/bert-base-wp-30k_msl-128-MSA-$s/ --drive-chunk-size 128M --verbose
  for f in `ls $s`; do
    sleep 1
    rclone move $s/$f gdrive:CAMeLBERT/model/bert-base-wp-30k_msl-128-MSA-$s/ --verbose
  done
  done
done
```

```bash
for s in full half quarter eighth sixteenth; do
  gsutil -o "GSUtil:parallel_thread_count=1" \
  -o "GSUtil:sliced_object_download_max_components=8" \
  mv gs://camelbert/model/bert-base-wp-30k_msl-512-MSA-$s/model.ckpt-1000000.* $s/
  #sleep 1
  rclone move $s/model.ckpt-1000000.index gdrive:CAMeLBERT/model/bert-base-wp-30k_msl-512-MSA-$s/ --verbose
  #sleep 1
  rclone move $s/model.ckpt-1000000.meta gdrive:CAMeLBERT/model/bert-base-wp-30k_msl-512-MSA-$s/ --verbose
  #sleep 1
  rclone move $s/model.ckpt-1000000.data-00000-of-00001 gdrive:CAMeLBERT/model/bert-base-wp-30k_msl-512-MSA-$s/ --drive-chunk-size 256M --verbose
done
```


## Converting tf checkpoint to torch chekcpoint
### Set up environment
```bash
# version 1.5.1
module purge
module load all
module load cuda/9.2

conda create -n torch_1.5.1-transformers_3.1.0 python=3.6
conda activate torch_1.5.1-transformers_3.1.0
conda install pytorch==1.5.1 cudatoolkit=9.2 -c pytorch
pip install tensorflow==1.15 transformers==3.1.0 camel_tools seqeval==0.0.12 scikit-learn==0.21.3
```

### Download tf checkpoint
```bash
for split in full half quarter eighth sixteenth; do
    # Create a directory
    mkdir -p bert-base-wp-30k_msl-512-MSA-$split-1000000-step

    # Download checkpoint files from Google Drive
    rclone copy google:CAMeLBERT/model/bert-base-wp-30k_msl-512-MSA-$split/model.ckpt-1000000.index bert-base-wp-30k_msl-512-MSA-$split-1000000-step/
    rclone copy google:CAMeLBERT/model/bert-base-wp-30k_msl-512-MSA-$split/model.ckpt-1000000.meta bert-base-wp-30k_msl-512-MSA-$split-1000000-step/
    rclone copy google:CAMeLBERT/model/bert-base-wp-30k_msl-512-MSA-$split/model.ckpt-1000000.data-00000-of-00001 bert-base-wp-30k_msl-512-MSA-$split-1000000-step/

    # Copy config files
    cp ../../configs/bert-base-config.json bert-base-wp-30k_msl-512-MSA-$split-1000000-step/config.json
    cp ../../configs/bert-wordpiece-30k-vocab.txt bert-base-wp-30k_msl-512-MSA-$split-1000000-step/vocab.txt
done
```

### Convert tf checkpoint to pytorch checkpoint 
```bash
for split in full half quarter eighth sixteenth; do
transformers-cli convert --model_type bert \
  --tf_checkpoint bert-base-wp-30k_msl-512-MSA-$split-1000000-step/model.ckpt-1000000 \
  --config ../../configs/bert-base-config.json \
  --pytorch_dump_output bert-base-wp-30k_msl-512-MSA-$split-1000000-step/pytorch_model.bin
done
```
