import pandas as pd
import seaborn as sns
from pathlib import Path
import matplotlib.pyplot as plt
import os

# REQUIRED EXPERIMENT SCRIPTS:
# - Above_ExactDP_Exhaustive.sh

ns = [2,3,4,5,6]
ks = [1,2,3]

bdds = pd.DataFrame(index=ks,columns=ns,dtype=int)
inf_times = pd.DataFrame(index=ks,columns=ns,dtype=float)

try:
    for n in ns:
        for k in ks:
            dice_base = Path(f'final_results/stats/dice_flat/inf-exhaustive_comp-exhaustive/above_threshold/list_length-{n}_max_int_value-{k}_threshold-{k-1}_lamb-0.2')
            bdd_stats = pd.read_csv(dice_base / 'bdd_sizes.csv',index_col=0)
            bdds.loc[k,n] = int(bdd_stats['0'].max())
            time_stats = pd.read_csv(dice_base / 'scalability.csv',index_col=0)
            inf_times.loc[k,n] = round(time_stats.loc['total_duration'].iloc[0],4)
except FileNotFoundError:
    pass
except KeyError:
    pass
# except Exception:
#     pass

os.makedirs('plots', exist_ok=True)

print(bdds)
print(inf_times)
sns.set(font_scale=2)
sns.heatmap(bdds,annot=True,cbar=False,cmap="crest")
plt.xlabel('List Length')
plt.ylabel('Max Int Size')
plt.tight_layout()
# plt.title('Maximum BDD Sizes for\nGeometric Above Threshold')
plt.savefig('plots/Fig2.pdf',bbox_inches='tight')