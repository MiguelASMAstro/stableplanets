#!/bin/bash
#SBATCH --account=b1094 ## Required: your allocation/account name, i.e. eXXXX, pXXXX or bXXXX
#SBATCH --partition=ciera-std ## Required: (buyin, short, normal, long, gengpu, genhimem, etc)
#SBATCH --time=03:00:00 ## Required: How long will the job need to run (remember different partitions have restrictions on this parameter)
#SBATCH --nodes=1 ## how many computers/nodes do you need (no default)
#SBATCH --ntasks-per-node=1 ## how many cpus or processors do you need on per computer/node (default value 1)
#SBATCH --array=0-19
#SBATCH --mem=300M ## how much RAM do you need per computer/node (this affects your FairShare score so be careful to not ask for more than you need))
#SBATCH --job-name=solarsystem ## When you run squeue -u  this is how you can identify the job

module load python/anaconda3.6
source activate venv

python integratortest_heartbeat.py &> results/testout_hb_${SLURM_ARRAY_TASK_ID}.txt

head -n 1 results/testout_hb_${SLURM_ARRAY_TASK_ID}.txt > results/temp_${SLURM_ARRAY_TASK_ID}.txt | mv results/temp_${SLURM_ARRAY_TASK_ID}.txt results/testout_hb_${SLURM_ARRAY_TASK_ID}.txt
rm results/temp_${SLURM_ARRAY_TASK_ID}.txt