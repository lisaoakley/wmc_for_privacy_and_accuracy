import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import os

# REQUIRED EXPERIMENT SCRIPTS:
# - RR_ExactDP_Restricted.sh
# - RR_ExactAcc_Restricted.sh

N = 6
lambdas = [.05,.1,.15,.2,.25,.3,.35,.4,.45,.5]
priv_bounds = pd.DataFrame(index=lambdas,columns=["Priv. Bound"])
acc_bounds = pd.DataFrame(index=lambdas,columns=["Acc. Bound"])
priv_tag = "inf-min_representative_comp-rr_2n"
acc_tag = "acc-min_representative_alpha-3"

for lamb in lambdas:
    try:
        # Privacy non-exhaustive
        dice_base = Path(f'final_results/stats/dice_flat/{priv_tag}/rr/n-{N}_lamb-{lamb}')
        stats = pd.read_csv(dice_base / 'stats.csv',index_col=0)
        priv_bounds.loc[lamb,"Priv. Bound"] = round(float(stats.loc['worst_ratio'].iloc[0]),4)
    except FileNotFoundError as e:
        print(e)
    except KeyError as e:
        print(e)


    try:
        # Accuracy non-exhaustive
        dice_base = Path(f'final_results/stats/dice_flat/{acc_tag}/rr_count/n-{N}_lamb-{lamb}')
        stats = pd.read_csv(dice_base / 'stats.csv',index_col=0)
        print(stats)
        acc_bounds.loc[lamb,"Acc. Bound"] = 1 - round(float(stats.loc['accuracy_err'].iloc[0]),4)
    except FileNotFoundError as e:
        print(e)
    except KeyError as e:
        print(e)


plt.rc('font', size=22)          # controls default text sizes
plt.rc('axes', titlesize=22)     # fontsize of the axes title
plt.rc('axes', labelsize=22)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=14)    # fontsize of the tick labels
plt.rc('ytick', labelsize=14)    # fontsize of the tick labels
plt.rc('legend', fontsize=16)    # legend fontsize
plt.rc('figure', titlesize=22)  # fontsize of the figure title

os.makedirs('plots', exist_ok=True)

priv_bounds.plot(style=['o:'],color=['purple'],markersize=10,figsize=(4, 5))
plt.xlabel("$\lambda$")
plt.ylabel("$e^\epsilon$")
plt.savefig('plots/Fig4a.pdf',bbox_inches='tight')

print(acc_bounds)
acc_bounds.plot(style=['o:'],color=['purple'],markersize=10,figsize=(4, 5))
plt.xlabel("$\lambda$")
plt.ylabel("$1-\\beta$")
plt.savefig('plots/Fig4b.pdf',bbox_inches='tight')
