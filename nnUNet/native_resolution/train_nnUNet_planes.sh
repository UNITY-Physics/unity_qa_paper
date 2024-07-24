#!/bin/bash
#SBATCH --time=48:00:00         
#SBATCH --output=log/nnUNet_log_%A_%a.out
#SBATCH --error=log/nnUNet_log_%A_%a.err
#SBATCH --cpus-per-task=16
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=10G
#SBATCH -p gpua100i
#--->SBATCH --array=1-4%1

############################################################
###### Train nnUNet based on native resolution images ######
############################################################

### Setup environment ###
source ~/venv/nnunte/bin/activate
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/home/em2876lj/venv/nnunte/lib/python3.9/site-packages/nvidia/cudnn/lib

### nnUNET variables ###
DATASET_ID=137


# 1. Plan and pre-process
# nnUNetv2_plan_and_preprocess -d $DATASET_ID -pl nnUNetPlannerResEncM

# ---> Outcome here 
# 2 Configurations: 2d and 3d_fullres. 3d_lowres was dropped by nnUNet du to the resolution

# 2. Train 2d
nnUNetv2_train -device cuda -p nnUNetResEncUNetMPlans $DATASET_ID 2d 0 --npz

# Remaining folds
# nnUNetv2_train -device cuda -p nnUNetResEncUNetMPlans $DATASET_ID 3d_fullres $SLURM_ARRAY_TASK_ID --npz 

# nnUNetv2_find_best_configuration $DATASET_ID -p nnUNetResEncUNetMPlans -c 3d_fullres 

####### Run inference like this #######

# nnUNetv2_predict -d $Dataset137_UNITY -i INPUT_FOLDER -o OUTPUT_FOLDER -f  0 1 2 3 4 -tr nnUNetTrainer -c 3d_fullres -p nnUNetResEncUNetMPlans

####### Once inference is completed, run postprocessing like this #######

# nnUNetv2_apply_postprocessing -i OUTPUT_FOLDER -o OUTPUT_FOLDER_PP -pp_pkl_file /home/em2876lj/Projects/nnUNet/nnUNET_results/Dataset137_UNITY/nnUNetTrainer__nnUNetResEncUNetMPlans__3d_fullres/crossval_results_folds_0_1_2_3_4/postprocessing.pkl -np 8 -plans_json /home/em2876lj/Projects/nnUNet/nnUNET_results/Dataset137_UNITY/nnUNetTrainer__nnUNetResEncUNetMPlans__3d_fullres/crossval_results_folds_0_1_2_3_4/plans.json

# nnUNetv2_export_model_to_zip -d $DATASET_ID -f 0 1 2 3 4 -tr nnUNetTrainer -c 3d_fullres -p nnUNetResEncUNetMPlans -o /home/em2876lj/Projects/nnUNet/export137.zip