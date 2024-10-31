import pandas as pd
from tqdm import tqdm
import numpy as np
import statsmodels.formula.api as smf
import seaborn as sns

temp_thr = [24.5, 23.5, 22, 21, 20, 19, 18, 16.9, 15.8, 14.8, 0] 
# These are transition temperatures corresponding to how many black vials are visible.
# With 0 visible, the temperature is above 24.5 With 10 visible the temperature is below 14.8 which
# we here write to 0 to indicate it would be anything below 14.8

def add_temperature_w0_sw(df, data_path):
    df_temp = pd.read_csv(f'{data_path}/session_params.csv')
    # df_temp['Temperature'] = 24-df_temp['n_black']
    df_temp['Temperature'] = 0.0
    for i, row in df_temp.iterrows():
        df_temp.loc[i, 'Temperature'] = temp_thr[int(row['n_black'])]

    df['Temperature'] = None
    df['w0'] = None
    df['SoftwareVersions'] = None

    for i,row in tqdm(df.iterrows(), desc="Adding in temperature, w0 and SW", total=len(df)):
        df.at[i,'Temperature'] = df_temp[(df_temp['Subject']==row.Subject) & (df_temp['Session']==row.Session)].Temperature.values
        df.at[i,'w0'] = df_temp[(df_temp['Subject']==row.Subject) & (df_temp['Session']==row.Session)].w0.values
        df.at[i,'SoftwareVersions'] = df_temp[(df_temp['Subject']==row.Subject) & (df_temp['Session']==row.Session)].SW.values[0]

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
            D['Adult WM/GM Contrast'] = [(adult_wm-adult_gm)/ses_df[ses_df.Seg==con_ref['Adult']['WM']['Seg']].Mean.mean()]
            D['Neonatal WM/GM Contrast'] = [(neo_wm-neo_gm)/ses_df[ses_df.Seg==con_ref['Neo']['WM']['Seg']].Mean.mean()]
            D['SoftwareVersions'] = sub_df.SoftwareVersions.unique()[0]

            df_contrast = pd.concat((df_contrast, pd.DataFrame.from_dict(D)), ignore_index=True)
    
    return df_contrast

    
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

def add_subject_lines(ax, df, mixed_lm_res, param):
    slope = mixed_lm_res.params[param]
    intercept = mixed_lm_res.params.Intercept

    for l in ax.get_lines():
        ll = l.get_label()
        if 'P0' in ll:
            c = l.get_color()
            xmin = df[df['Subject']==ll][param].min()
            xmax = df[df['Subject']==ll][param].max()
            
            if xmax==24: # Since we censured data at temperature=24
                xmax = 23
            
            x = np.linspace(xmin, xmax)
            inter = mixed_lm_res.random_effects[ll].Group
            ax.plot(x, x*slope + inter + intercept, color=c)

def remove_seaborn_legends(ax):
    handles, labels = ax.get_legend_handles_labels()
    handles = [handle for handle, label in zip(handles, labels) if 'P0' not in label]
    labels = [label for label in labels if 'P0' not in label]
    ax.legend(handles=handles, labels=labels)

def make_fitline_str_e(res, param, y, x):
    intercept = res['Intercept']
    slope = res[param]
    m_base, m_exp = f"{intercept:.2e}".split('e')
    k_base, k_exp = f"{abs(slope):.2e}".split('e')

    sign = '-' if slope < 0 else '+'

    s = rf'{y}$ = {m_base}\cdot 10^{int(m_exp)} {sign} {x} \cdot {k_base} \cdot 10^{int(k_exp)} $'

    return s

def make_global_group_comparison(df, ax, x_var, y_var, filter_temp=False):
    if filter_temp:
        my_df = df[df.Temperature<24]
    else:
        my_df = df.copy()

    ols_model = smf.ols(f'{y_var} ~ {x_var}', data=my_df)
    ols_res = ols_model.fit()
    slope = ols_res.params[x_var]
    intercept = ols_res.params.Intercept

    sns.scatterplot(data=my_df, x=x_var, y=y_var, hue='Subject', ax=ax)
    x = np.linspace(my_df[x_var].min(),my_df[x_var].max())

    m_base, m_exp = f"{intercept:.2e}".split('e')
    k_base, k_exp = f"{abs(slope):.2e}".split('e')

    if slope < 0:
        sign = '-'
    else:
        sign = '+'

    ax.plot(x, intercept + x*slope, '--k', label=rf'{y_var}$ = {m_base}\cdot 10^{int(m_exp)} {sign} {x_var} \cdot {k_base} \cdot 10^{int(k_exp)} $')

    # Remove seaborn legend entries
    handles, labels = ax.get_legend_handles_labels()
    handles = [handle for handle, label in zip(handles, labels) if 'P0' not in label]
    labels = [label for label in labels if 'P0' not in label]
    ax.legend(handles=handles, labels=labels)

    xlm_model = smf.mixedlm(f"{y_var} ~ {x_var}", my_df, groups=my_df['Subject'])
    xlm_res = xlm_model.fit(method=['lbfgs'])
    slope = xlm_res.params[x_var]
    intercept = xlm_res.params.Intercept

    for l in ax.get_lines():
        ll = l.get_label()
        if 'P0' in ll:
            c = l.get_color()
            xmin = my_df[my_df['Subject']==ll][x_var].min()
            xmax = my_df[my_df['Subject']==ll][x_var].max()
            x = np.linspace(xmin, xmax)
            inter = xlm_res.random_effects[ll].Group
            ax.plot(x, x*slope + inter + intercept, color=c)

    return ax, xlm_res, ols_res