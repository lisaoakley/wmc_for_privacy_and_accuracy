import pandas as pd
from pathlib import Path

# REQUIRED EXPERIMENT SCRIPTS:
# - Top_Examples_ExactAcc.sh

N=8
lamb=.2
priv_tag = "acc-min_representative_alpha-3"

dice_base = Path(f'final_results/examples/dice_flat/{priv_tag}/rr_count/n-{N}_lamb-{lamb}')
ex_df = pd.read_csv(dice_base / 'examples.csv')


print(ex_df)