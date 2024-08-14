import argparse
import json
import os
import subprocess as sp
import tempfile
import shutil
import ants
from ghost.phantom import Caliber137

def parse_args():
    parser = argparse.ArgumentParser(description="Description of your program")
    
    # Add arguments
    parser.add_argument('-i', '--input', type=str, nargs='+', help='Input file(s)', required=True)
    parser.add_argument('-o', '--output', type=str, nargs='+', help='Output file(s)', required=True)
    parser.add_argument('-c', '--config', type=str, help='Config file', required=True)
    parser.add_argument('--device', type=str, help='Which device to run on', default='cuda')
    parser.add_argument('--keep', action='store_true', help='Keep temporary directory')

    # Parse the arguments
    args = parser.parse_args()

    return args

def main():
    args = parse_args()
    run_prediction(args.input, args.output, args.config, args.device, args.keep)

def run_prediction(input, output, config, device='cuda', keep=False):

    if len(input) != len(output):
        raise ValueError('Input and output must be the same length')
    
    phan = Caliber137()
    # phantom_img = ants.image_read(phan.get_phantom_nii())
    # phantom_resamp = ants.resample_image(phantom_img, resample_params=[1.5, 1.5, 1.5], interp_type=4)

    # 1. Create temporary directories
    print(f"Running inference on {len(input)} images")

    # tmpdir = tempfile.mkdtemp(dir='.', prefix='tempdir_nnUNet_inference_')
    tmpdir = '/home/em2876lj/Projects/QA/QA_paper/project/code/nnUnet_inference/tempdir_nnUNet_inference_fb6i9pqw'
    # os.makedirs(tmpdir+'/input')
    # os.makedirs(tmpdir+'/predicted')
    # os.makedirs(tmpdir+'/final')
    # print(f"Creating temporary directory for processin {tmpdir}")

    channel = '0000'
    data_prefix = 'UNITY'
    data_idx = [f'{int(x):04d}' for x in range(1,len(input)+1)]
    # all_aff = []
    # for idx,f in zip(data_idx, input):
    #     img = ants.image_read(f)
    #     reg = ants.registration(phantom_resamp, img, type_of_transform='Rigid')
    #     all_aff.append(ants.read_transform(reg['fwdtransforms'][0]))
    #     ants.image_write(reg['warpedmovout'], f'{tmpdir}/input/{data_prefix}_{idx}_{channel}.nii.gz')

    # # 2. Get inference parameters
    # with open(config, 'r') as f:
    #     jdata = json.load(f)

    # # 3. Run prediction
    # print("Starting prediction")
    
    # cmd_predict = f"nnUNetv2_predict -device {device} -d {jdata['dataset_id']} -i {tmpdir+'/input'} -o {tmpdir+'/predicted'} -f {jdata['folds']} -tr {jdata['trainer']} -c {jdata['config']} -p {jdata['plan']} --disable_progress_bar"
    
    # sp.call(cmd_predict, shell=True)
    
    # # Run post processing
    # print("Starting post-processing")
    
    # cmd_process = f"nnUNetv2_apply_postprocessing -i {tmpdir+'/predicted'} -o {tmpdir+'/final'} -pp_pkl_file {jdata['pp_pkl_file']} -np 8 -plans_json {jdata['plans_json']}"
    
    # sp.call(cmd_process, shell=True)

    # # Save data
    # print(f'Saving data to {output}')
    for idx,f in zip(data_idx, output):
        try:
            shutil.copy(f'{tmpdir}/final/{data_prefix}_{idx}.nii.gz', f)
            print(f)
        except:
            print(f'Could not copy to dest {f}')

    # for i,f in enumerate(output):
        # reg_fname = f.split('.nii.gz')[0] + '_PreRegFwd.mat'
        # ants.write_transform(all_aff[i], reg_fname)

    if not keep:
        print("Cleaning up temporary directory")
        shutil.rmtree(tmpdir)

if __name__ == '__main__':
    main()
