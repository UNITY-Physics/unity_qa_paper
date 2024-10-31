import pandas as pd
import numpy as np
import statsmodels.api as sm

encoding_dir = {'axi':{'phase':'y', 'frequency':'x', 'slice':'z'},
                    'sag':{'phase':'z', 'frequency':'y', 'slice':'x'},
                    'cor':{'phase':'x', 'frequency':'z', 'slice':'y'}}

def my_polyfit(x,y, degree=2):
    X = np.column_stack([x**i for i in range(degree+1)])
    X = sm.add_constant(X)
    model = sm.OLS(y,X)
    results = model.fit()

    return results.params, results. pvalues

def load_distortions_df():
    bw = {'axi':571.429,'cor':516.129,'sag':470.588}

    df = pd.read_csv('../data/distortions_df.csv', low_memory=False)
    df = df.loc[(df['Method']=='UNetAxisRigid') & (df['Run']==1)]
    
    df['Date'] = pd.to_datetime(df['Session'].str[:8], format='%Y%m%d')

    df['LabelValue'] = df['LabelValue'].astype(int)

    df.loc[:,'BW'] = 0.0

    for ax in bw.keys():
        df.loc[df['Axis']==ax,'BW'] = 1/bw[ax]

    df['r_ref'] = 0.0
    df['3D_diff'] = 0.0
    df['2D_diff'] = 0.0

    df.loc[:,'r_ref'] = np.sqrt(df.loc[:, 'x_ref']**2 + df.loc[:, 'y_ref']**2 + df.loc[:, 'z_ref']**2)
    df.loc[:,'3D_diff'] = np.sqrt(df.loc[:, 'x_diff']**2 + df.loc[:, 'y_diff']**2 + df.loc[:, 'z_diff']**2)

    for ax in ['axi', 'sag', 'cor']:
        rf = (df.Axis==ax)
        x = f'{encoding_dir[ax]["phase"]}'
        y = f'{encoding_dir[ax]["frequency"]}'
        df.loc[rf,'2D_diff'] = np.sqrt( df.loc[rf, f'{x}_diff']**2 + df.loc[rf, f'{y}_diff']**2)

    df['r_ref_level'] = df['r_ref'].round(1).astype(str)

    all_sub = df['Subject'].unique()
    all_ses = {}
    for sub in all_sub:
        all_ses[sub] = list(df[df['Subject']==sub].Session.unique())

    df.reset_index(inplace=True, drop=True)

    nremove = 0
    for sub in df.Subject.unique():
        for ses in df.loc[df.Subject==sub, 'Session'].unique():
            for ax in ['axi', 'sag', 'cor']:
                # Check session
                failed_session = len(df.loc[(df.Subject==sub) & (df.Session==ses) & (df.Axis==ax) & ((df.x_diff.abs()>20) | (df.y_diff.abs()>20) | (df.z_diff.abs()>20))])>0
                if failed_session:
                    df.drop(df.loc[(df.Subject==sub) & (df.Session==ses) & (df.Axis==ax)].index, inplace=True)
                    nremove+=1

    print(f"Removed {nremove} sessions")

    return df

def make_distortions_corr_df(df):
    to_concat = []

    
    encoding_dir_inv = {}
    for ax in encoding_dir.keys():
        encoding_dir_inv[ax] = {}
        for k in ['phase', 'frequency', 'slice']:
            encoding_dir_inv[ax][encoding_dir[ax][k]] = k

    for sub in df.Subject.unique():
        for ses in df.loc[df.Subject==sub].Session.unique():
            for ax in ['axi', 'sag', 'cor']:
                
                # Axial
                my_df = df.loc[(df.Axis==ax) & (df.Subject==sub) & (df.Session==ses)]
                
                if len(my_df)>0:
                    my_out = {'Subject':sub, 'Session':ses, 'Axis':ax}

                    for enc in ['phase', 'frequency']:
                        x = my_df[f"{encoding_dir[ax][enc]}_ref"]
                        y = my_df[f"{encoding_dir[ax][enc]}_diff"]

                        cc = np.corrcoef(x,y)
                        par, pval = my_polyfit(x, y)

                        my_out[f'par1_{enc}'] = par.x1
                        my_out[f'par2_{enc}'] = par.x2
                        
                        my_out[f'pval1_{enc}'] = pval.x1
                        my_out[f'pval2_{enc}'] = pval.x2

                        my_out[f'cc_{enc}'] = cc[0,1]

                    to_concat.append(pd.DataFrame(my_out, index=[0]))

    df_poly = pd.concat(to_concat, ignore_index=True)

    return df_poly

def calc_mean_2D_dist_radius(df):
    to_concat = []

    for sub in df.Subject.unique():
        for ses in df.loc[df.Subject==sub].Session.unique():
            for ax in ['axi', 'sag', 'cor']:
                for r in ['70.7', '50.0', '0.0']:
                    try:
                        rf = ((df.Subject==sub) & (df.Session==ses) & (df.r_ref_level==r) & (df.Axis==ax))
                        D = {'Subject':sub, 
                            'Session':ses, 
                            'SoftwareVersions':df.loc[rf,'SoftwareVersions'].unique()[0],
                            'Temperature':df.loc[rf,'Temperature'].unique()[0],
                            'Mean_2D':df.loc[rf,'2D_diff'].mean(),
                            'Axis':ax, 
                            'r_ref_level':r,
                            'radius':float(r)}
                        
                        to_concat.append(pd.DataFrame(D, index=[0]))
                    except:
                        continue

    mean_rad_df = pd.concat(to_concat, ignore_index=True)
    mean_rad_df.dropna(inplace=True)
    
    return mean_rad_df