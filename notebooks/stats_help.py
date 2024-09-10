import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import shapiro
import seaborn as sns
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
import statsmodels.formula.api as smf
import pandas as pd

def show_bootstrap(model, coefs, nrows, ncols, figsize, ymax=250):
    fig, axes = plt.subplots(4,6, figsize=figsize)
    for i in range(coefs.shape[1]):
        ax = axes[np.unravel_index(i, axes.shape)]
        ax.hist(coefs[:,i])
        ax.set_title(model.params.index[i], size=8)
        ax.plot([model.params.iloc[i]]*2,[0,ymax], '--r', linewidth=2)
        shapiro_test = shapiro(coefs[:,i])
        print(f"{model.params.index[i]} Fit: {model.params.iloc[i]:.1f} Boostrap: {np.mean(coefs[:,i]):.1f} ({2*np.std(coefs[:,i]):.1f}) (Normality pvalue={shapiro_test.pvalue:.1e})")

    plt.tight_layout()
    plt.show()

def check_model(model):
    dw_test = sm.stats.stattools.durbin_watson(model.resid)
    print("---- Auto correlation ----")
    print(f'Durbin-Watson Test: {dw_test:.3f} (Close to 2 is good)')

    fig, axes = plt.subplots(1,3,figsize=(12,4))
    ##############
    ax = axes[0]
    ax.scatter(model.fittedvalues, model.resid)
    ax.axhline(0, color='red', linestyle='--')
    ax.set_xlabel('Fitted Values')
    ax.set_ylabel('Residuals')
    ax.set_title('Residuals vs Fitted Values')
    
    ############## 
    bp_test = het_breuschpagan(model.resid, model.model.exog)
    labels = ['Lagrange multiplier statistic', 'p-value', 'f-value', 'f p-value']
    print("\n---- Check if variance depends on parameter value ----")
    print(f"Lagrange multiplier statistic: {bp_test[0]:.4f} (p-value: {bp_test[1]:.4f})")
    print(f"f-statistic of the hypothesis that the error variance does not depend on x: {bp_test[2]:.4f} (p-value: {bp_test[3]:.4f})")

    sns.histplot(model.resid, kde=True, ax=axes[1])
    axes[1].set_title('Histogram of Residuals')
    
    ##############
    sm.qqplot(model.resid, line='s', ax=axes[2])
    axes[2].set_title('Q-Q Plot of Residuals')
    
    shapiro_test = shapiro(model.resid)
    
    print(f'\n----Shapiro-Wilk Test for normality ----')
    print(f"Stat: {shapiro_test.statistic:.3f} pvalue: {shapiro_test.pvalue}")

    plt.tight_layout()
    plt.show()

def bootstrap_formula(df, formula, num_bootstrap=100, num_coeff=23):
    coefs = np.zeros((num_bootstrap, num_coeff))

    for i in range(num_bootstrap):
        
        bootstrap_sample = pd.DataFrame()

        # Stratify sampling within each group
        for group in df['Subject'].unique():
            group_data = df[df['Subject'] == group]
            
            for sw in group_data['SoftwareVersions'].unique():
                group_sw_data = group_data[group_data['SoftwareVersions']==sw]

                # Sample with replacement from each group
                group_bootstrap_sample = group_sw_data.sample(n=len(group_sw_data), replace=True)
                
                # Append to the bootstrap sample
                bootstrap_sample = pd.concat([bootstrap_sample, group_bootstrap_sample])
        
        # Fit the OLS model on the resampled data
        model = smf.ols(formula, data=bootstrap_sample).fit()
        coefs[i, :] = model.params

    # Calculate the mean and standard error of the coefficients

    return coefs