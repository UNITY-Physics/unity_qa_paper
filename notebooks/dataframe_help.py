import pandas as pd
from tqdm import tqdm

def add_temperature_w0(df, data_path):
    print()
    df_temp = pd.read_csv(f'{data_path}/fisp_temperature_w0.csv')
    df_temp['Temperature'] = 24-df_temp['n_black']

    df['Temperature'] = None
    df['w0'] = None
    for i,row in tqdm(df.iterrows(), desc="Adding in temperature and w0", total=len(df)):
        df.at[i,'Temperature'] = df_temp[(df_temp['Subject']==row.Subject) & (df_temp['Session']==row.Session)].Temperature.values
        df.at[i,'w0'] = df_temp[(df_temp['Subject']==row.Subject) & (df_temp['Session']==row.Session)].w0.values

    df.Temperature = df.Temperature.astype('float64')
    df.w0 = df.w0.astype('float64')

    return df


def calc_contrast(df_master, con_ref):
    # Relative contrast between WM and GM
    df_master.head()
    df_contrast = pd.DataFrame(columns=['Subject', 'Session', 'Adult WM/GM Contrast', 'Neonatal WM/GM Contrast', 'SoftwareVersions'])

    for sub in df_master.Subject.unique():
        sub_df = df_master[(df_master.Subject == sub) & (df_master.Run == 1)]
    
        for ses in sub_df.Session.unique():
            ses_df = sub_df[sub_df.Session==ses]

            neo_wm = ses_df[(ses_df.Seg==con_ref['Neo']['WM']['Seg']) & 
                            (ses_df.LabelValue==con_ref['Neo']['WM']['LabelValue'])].Mean.values[0]
            
            neo_gm = ses_df[(ses_df.Seg==con_ref['Neo']['GM']['Seg']) & 
                            (ses_df.LabelValue==con_ref['Neo']['GM']['LabelValue'])].Mean.values[0]

            adult_wm = ses_df[(ses_df.Seg==con_ref['Adult']['WM']['Seg']) & 
                              (ses_df.LabelValue==con_ref['Adult']['WM']['LabelValue'])].Mean.values[0]
            adult_gm = ses_df[(ses_df.Seg==con_ref['Adult']['GM']['Seg']) & 
                              (ses_df.LabelValue==con_ref['Adult']['GM']['LabelValue'])].Mean.values[0]
            
            D = {}
            D['Subject'] = [sub]
            D['Session'] = [ses]
            D['Adult WM/GM Contrast'] = [adult_wm/adult_gm]
            D['Neonatal WM/GM Contrast'] = [neo_wm/neo_gm]
            D['SoftwareVersions'] = sub_df.SoftwareVersions.unique()[0]

            df_contrast = pd.concat((df_contrast, pd.DataFrame.from_dict(D)), ignore_index=True)
    
    return df_contrast


# def get_relax_df(mimics):
    
#     if mimics not in valid_sheets:
#         raise ValueError(f'Mimics must be one of: {valid_sheets}')

#     return pd.read_excel(fname, sheet_name=mimics)
    

def add_relaxometry(df, results_path):
    print()
    df_T1 = pd.read_csv(f'{results_path}/relaxometry_NiCl_mimics.csv')
    df_T2 = pd.read_csv(f'{results_path}/relaxometry_MnCl_mimics.csv')

    # Add in T1 and T2 in the dataframe
    df['T1'] = None
    df['T2'] = None
    df['Conc'] = None
    df['Content'] = None

    for i,row in tqdm(df.iterrows(), desc="Adding in relaxometry results", total=len(df)):
        mimic = int(row.LabelValue)

        if row.Seg == 'T1':
            relax_df = df_T1
            content = 'NiCl2'

        elif row.Seg == 'T2':
            relax_df = df_T2
            content = 'MnCl2'

        df.at[i,'T1'] = relax_df[relax_df['Mimic'] == f'{row.Seg} {mimic}']['T1 [s]'].values
        df.at[i,'T2'] = relax_df[relax_df['Mimic'] == f'{row.Seg} {mimic}']['T2 [s]'].values
        df.at[i,'Conc'] = relax_df[relax_df['Mimic'] == f'{row.Seg} {mimic}']['Conc. [mM]'].values
        df.at[i,'Content'] = content
    
    df.T1 = df.T1.astype('float64')
    df.T2 = df.T2.astype('float64')
    df.Conc = df.Conc.astype('float64')

    return df