import ants
import os
import json
import pandas as pd

nnUNet_raw = "/home/em2876lj/Projects/nnUNet/nnUNet_raw"
projdir = "/home/em2876lj/Projects/QA/QA_paper/project"
DATASET = "Dataset137_UNITY"

def get_data(sub, ses, rec):

    # Get data from reference folder
    if rec == 'axi':
        runstr = f'_run-01'
    else:
        runstr = ''

    raw = f'{projdir}/reference_segmentations/original/sub-{sub}_ses-{ses}_rec-{rec}{runstr}_T2w.nii.gz'
    seg = f'{projdir}/reference_segmentations/final/sub-{sub}_ses-{ses}_rec-{rec}{runstr}_desc-segRegFidLabels_T2w.nii.gz'.replace('-', '')

    return ants.image_read(raw), ants.image_read(seg)

def save_data(idx, raw, seg):
    raw_name = f'{nnUNet_raw}/Dataset137_UNITY/imagesTr/UNITY_{idx:03d}_0000.nii.gz'
    seg_name = f'{nnUNet_raw}/Dataset137_UNITY/labelsTr/UNITY_{idx:03d}.nii.gz'

    ants.image_write(raw, raw_name)
    ants.image_write(seg, seg_name)

    idx +=1 
    return idx


def main():

    # Make folders
    nnUNet_path = f"{nnUNet_raw}/{DATASET}"

    for fol in ['imagesTr', 'labelsTr']:
        fol_name = os.path.join(nnUNet_path, fol)
        
        if not os.path.exists(fol_name):
            os.makedirs(fol_name)

    ref_subses = pd.read_csv(f'{projdir}/code/ref_sessions.txt', 
                            names=['Subject', 'Session'], delimiter=' ')
    
    df_data = pd.DataFrame(columns=['Subject', 'Session', 'Rec'])

    # Get reference image and segmentation
    fname = "/home/em2876lj/Code/GHOST/data/Caliber137/phantom_T1w.nii.gz"
    ref_img = ants.image_read(fname)
    ref_fid = ants.image_read("/home/em2876lj/Code/GHOST/data/Caliber137/seg_fiducials.nii.gz")
    IDX = save_data(1, ref_img, ref_fid)

    df_data.loc[IDX-1] = ['Caliber137', '01', 'Iso']

    for i,row in ref_subses.iterrows():
        sub = row.Subject
        ses = row.Session

        for rec in ['axi','cor','sag']:
            print(sub, ses, rec)
            raw, seg = get_data(sub, ses, rec)
            IDX = save_data(IDX, raw, seg)
            df_data.loc[IDX-1] = [sub, ses, rec]

    df_data.to_csv(f'{nnUNet_raw}/{DATASET}/files.csv')

    # Make json
    labels = {f"fid{x}":x for x in range(1,16)}
    labels['background'] = 0
    D = {
        "channel_names": {"0": "T2"}, 
        "labels": labels, 
        "numTraining": IDX-1, 
        "file_ending": ".nii.gz",
        "overwrite_image_reader_writer": "SimpleITKIO"
        }
    
    with open(f"{nnUNet_raw}/{DATASET}/dataset.json", 'w') as f:
        json.dump(D,f)

if __name__ == '__main__':
    main()