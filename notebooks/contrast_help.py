import pandas as pd
import json
from tqdm import tqdm
import os

projdir = '/home/em2876lj/Projects/QA/QA_paper/project'

def get_contrast_df(subses, layout, recalculate=False):

    df_fname = f'{projdir}/code/unity_qa_paper/results/stats/contrast_df.csv'
    
    if (not os.path.exists(df_fname)) or recalculate:

        all_rows = []
        for i,row in tqdm(subses.iterrows()):
            f = layout.get(scope='raw', subject=row.Subject, 
                                    session=row.Session, extension='.json', 
                                    reconstruction='axi')[0]

            with open(f,'r') as jf:
                sw = json.load(jf)["SoftwareVersions"]

            for run in [1,2]:
                for seg in ['T1', 'T2']:
                    try:
                        f = layout.get(scope='derivatives', subject=row.Subject, 
                                    session=row.Session, extension='.csv', run=run, 
                                    reconstruction='axi', desc=f'seg{seg}mimics')[0]
                        df = pd.read_csv(f).drop(columns=['Unnamed: 0', 'x', 'y', 'z', 'Volume'])
                        df['Mean'] /= df['Mean'].mean()
                        df['Subject'] = row.Subject
                        df['Session'] = row.Session
                        df['Run'] = run
                        df['Seg'] = seg
                        df["SoftwareVersions"] = sw

                        all_rows.append(df)

                    except IndexError:
                        continue
        
        df = pd.concat(all_rows, ignore_index=True)
        df.to_csv(df_fname, index=False)
    
    else:
        df = pd.read_csv(df_fname)

    return df


def calc_contrast(df_master):
    # Relative contrast between WM and GM
    df_master.head()
    df_contrast = pd.DataFrame(columns=['Subject', 'Session', 'Adult WM/GM Contrast', 'Neonatal WM/GM Contrast', 'SoftwareVersions'])
    for sub in df_master.Subject.unique():
        sub_df = df_master[(df_master.Subject == sub) & (df_master.Run == 1)]
        for ses in sub_df.Session.unique():
            ses_df = sub_df[sub_df.Session==ses]
            neo_wm = ses_df[(ses_df.Seg=='T2') & (ses_df.LabelValue == 4.0)].Mean.values[0]
            neo_gm = ses_df[(ses_df.Seg=='T2') & (ses_df.LabelValue == 8.0)].Mean.values[0]

            adult_wm = ses_df[(ses_df.Seg=='T2') & (ses_df.LabelValue == 7.0)].Mean.values[0]
            adult_gm = ses_df[(ses_df.Seg=='T2') & (ses_df.LabelValue == 8.0)].Mean.values[0]
            
            D = {}
            D['Subject'] = [sub]
            D['Session'] = [ses]
            D['Adult WM/GM Contrast'] = [neo_wm/neo_gm]
            D['Neonatal WM/GM Contrast'] = [adult_wm/adult_gm]
            D['SoftwareVersions'] = sub_df.SoftwareVersions.unique()[0]

            df_contrast = pd.concat((df_contrast, pd.DataFrame.from_dict(D)), ignore_index=True)
    
    return df_contrast

def add_temperature_w0(df):
    # Combine with temperature
    df_temp = pd.read_csv('/home/em2876lj/Projects/QA/QA_paper/project/derivatives/fisp_temperature_w0.csv')
    df_temp['Temperature'] = 24-df_temp['n_black']

    df['Temperature'] = None
    df['w0'] = None
    for i,row in df.iterrows():
        df.at[i,'Temperature'] = df_temp[(df_temp['Subject']==row.Subject) & (df_temp['Session']==row.Session)].Temperature.values
        df.at[i,'w0'] = df_temp[(df_temp['Subject']==row.Subject) & (df_temp['Session']==row.Session)].w0.values

    df.Temperature = df.Temperature.astype('float64')
    df.w0 = df.w0.astype('float64')

    return df