import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import os

# REQUIRED EXPERIMENT SCRIPTS:
# - RR_ExactDP_Restricted.sh
# - RR_ExactDP_Exhaustive.sh
# - RR_ExactAcc_Restricted.sh
# - RR_ExactAcc_Exhaustive.sh

ns = list(range(2,9))
lamb = .2
bdds = pd.DataFrame(index=ns,columns=['Priv.','Acc.'])
times = pd.DataFrame(index=ns,columns=['Priv.','Acc.','Priv. (Exh.)', 'Acc. (Exh.)'])
restrictive_tag = "inf-min_representative_comp-rr_2n"
exhaustive_tag = "inf-exhaustive_comp-exhaustive"
acc_restrictive_tag = "acc-min_representative_alpha-3"
acc_exhaustive_tag = "acc-exhaustive_alpha-3"

for n in ns:

    try:
        # Privacy Exhaustive
        dice_base = Path(f'final_results/stats/dice_flat/{exhaustive_tag}/rr/n-{n}_lamb-{lamb}')
        time_stats = pd.read_csv(dice_base / 'scalability.csv',index_col=0)
        times.loc[n,'Priv. (Exh.)'] = round(time_stats.loc['total_duration'].iloc[0],4)
        print(round(time_stats.loc['total_duration'].iloc[0],4))
    except FileNotFoundError as e:
        print(e)
    except KeyError as e:
        print(e)

    try:
        # Privacy non-exhaustive ()
        dice_base = Path(f'final_results/stats/dice_flat/{restrictive_tag}/rr/n-{n}_lamb-{lamb}')
        time_stats = pd.read_csv(dice_base / 'scalability.csv',index_col=0)
        times.loc[n,'Priv.'] = round(time_stats.loc['total_duration'].iloc[0],4)
        # BDDs
        bdd_stats = pd.read_csv(dice_base / 'bdd_sizes.csv',index_col=0)
        bdds.loc[n,'Priv.'] = int(bdd_stats['0'].max())
    except FileNotFoundError as e:
        print(e)
    except KeyError as e:
        print(e)

    try:
        # Accuracy Exhaustive
        dice_base = Path(f'final_results/stats/dice_flat/{acc_exhaustive_tag}/rr_count/n-{n}_lamb-{lamb}')
        time_stats = pd.read_csv(dice_base / 'scalability.csv',index_col=0)
        times.loc[n,'Acc. (Exh.)'] = round(time_stats.loc['total_duration'].iloc[0],4)
    except FileNotFoundError as e:
        print(e)
    except KeyError as e:
        # times.loc[n,'Acc. (Exh.)'] = times.loc[n-1,'Acc. (Exh.)']
        times.loc[n,'Acc. (Exh.) TO'] = times.loc[n-1,'Acc. (Exh.)']
        print(e)

    try:
        # Accuracy non-exhaustive
        dice_base = Path(f'final_results/stats/dice_flat/{acc_restrictive_tag}/rr_count/n-{n}_lamb-{lamb}')
        time_stats = pd.read_csv(dice_base / 'scalability.csv',index_col=0)
        times.loc[n,'Acc.'] = round(time_stats.loc['total_duration'].iloc[0],4)
        # BDD
        bdd_stats = pd.read_csv(dice_base / 'bdd_sizes.csv',index_col=0)
        bdds.loc[n,'Acc.'] = int(bdd_stats['0'].max())    
    except FileNotFoundError as e:
        print(e)
    except KeyError as e:
        # times.loc[n,'Acc.'] = bdds.loc[n-1,'Acc.']
        print(e)


plt.rc('font', size=22)          # controls default text sizes
plt.rc('axes', titlesize=18)     # fontsize of the axes title
plt.rc('axes', labelsize=18)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=15)    # fontsize of the tick labels
plt.rc('ytick', labelsize=15)    # fontsize of the tick labels
plt.rc('legend', fontsize=16)    # legend fontsize
plt.rc('figure', titlesize=22)  # fontsize of the figure title

os.makedirs('plots', exist_ok=True)

# print(bdds)
bdds.plot(style=['D:','s:'],color=['orange','green'],markersize=10,figsize=(3.4, 5))
# plt.title('BDD Sizes for\nPriv. and Accuracy',size=16)
plt.xlabel("n")
plt.ylabel("Max BDD Size")
plt.savefig('plots/Fig3a.pdf',bbox_inches='tight')

# # print(times)
times.plot(style=['D:','s:','o:','P:','x'],color=['orange','green','blue','red','red'],markersize=10,figsize=(4.4, 5),logy=True)
# plt.title('Experiment Duration for\nPriv. and Accuracy',size=16)
plt.xlabel("n")
plt.ylabel("Experiment Duration (s)")
plt.savefig('plots/Fig3b.pdf',bbox_inches='tight')