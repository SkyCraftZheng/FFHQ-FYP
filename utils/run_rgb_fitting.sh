# This code was taken directly from the original github implementation of FFHQ-UV (Bai et al. (2023)), which can be found here: https://github.com/csbhr/FFHQ-UV


#!/bin/bash
#PBS -l select=1:ncpus=1:mem=6gb:ngpus=1:filesystem_type=gpfs
#PBS -l walltime=2:00:00
#PBS -N FFHQ

cd ~/FFHQ-UV-RGB

# Load modules
# module load git
module load tools/prod
module load miniforge/3
module load cuda/10.1
module load cudnn/7.0
eval "$(~/miniforge3/bin/conda shell.bash hook)"
conda activate FFHQ2

set -e

/usr/bin/nvidia-smi
uptime

######################### Configuration #########################
# input_dir: the directory of the input images
# output_dir: the directory of the output results
# checkpoints_dir: the directory of the used checkpoints
# topo_assets_dir: the directory of the topo assets, e.g., 3DMM, masks, etc.
#################################################################
input_dir=../data/inputs
output_dir=../data/outputs
checkpoints_dir=../checkpoints
topo_assets_dir=../topo_assets


#################### Step 1. Preprocess Data ####################
# Read the input images in ${input_dir}
# Save the processed data in ${input_dir}/processed_data and ${input_dir}/processed_data_vis
#################################################################
cd ./RGB_Fitting
python step1_process_data.py \
    --input_dir ${input_dir} \
    --output_dir ${input_dir}/processed_data \
    --checkpoints_dir ${checkpoints_dir} \
    --topo_dir ${topo_assets_dir}


###################### Step 2. RGB Fitting ######################
# Read the processed data in ${input_dir}/processed_data
# Save the output results in ${output_dir}
#################################################################
python step2_fit_processed_data.py \
    --input_dir ${input_dir}/processed_data \
    --output_dir ${output_dir} \
    --checkpoints_dir ${checkpoints_dir} \
    --topo_dir ${topo_assets_dir} \
    --texgan_model_name texgan_ffhq_uv.pth


###################### Step 3. Add Eyeballs #####################
# Obtain necessary files from output for eyeballs
# Save the output results in directory 'render_files'
#################################################################
cd ../Mesh_Add_EyeBall

for mesh_dir in $(find ${output_dir} -mindepth 1 -maxdepth 1 -type d); do
    python run_mesh_add_eyeball.py \
        --mesh_path ${mesh_dir}/stage3_mesh_id.obj
done


# ###################### Step 3. Obtain blend file ################
# # Blend the outputs
# #################################################################
# cd ..
# export PATH=$PATH:/Applications/Blender.app/Contents/MacOS
# export FILE_DIR="/Users/raymondguo/Desktop/meshesFFHQ/outputs/015309"
# blender --background --python blend_copy.py




