from pathlib import Path
import pandas as pd

# REQUIRED EXPERIMENT SCRIPTS:
# - RR_DTMC-DP_Exhaustive.sh
# - RR_DTMC-DP_Restricted.sh
# - RR_ExactDP_Exhaustive.sh
# - RR_ExactDP_Restricted.sh

lamb = .2


def generate_storm_rows(ns, lamb, tag, kind):
    rows = ['' for _ in ns]
    for i,n in enumerate(ns):
        try:
            storm_base = Path(f'final_results/stats/storm/{tag}/rr/n-{n}_lamb-{lamb}')
            time_stats = pd.read_csv(storm_base / 'scalability.csv',index_col=0)
            if 'TIMEOUT' not in str(time_stats.loc['total_inference_time'].iloc[0]):
                model_stats = pd.read_csv(storm_base / 'model_stats.csv',index_col=0)
                num_states = model_stats.loc['num_states'].iloc[0]
                num_trans = model_stats.loc['num_trans'].iloc[0]
                num_runs = model_stats.loc['runs'].iloc[0]
                inf_time = round(time_stats.loc['total_inference_time'].iloc[0],4)
                verif_time = round(time_stats.loc['verification_time'].iloc[0],4)
                write_time = round(time_stats.loc['file_write_time'].iloc[0],4)
            else:
                num_states = "TO"
                num_trans = "TO"
                num_runs = "TO"
                inf_time = "TO"
                verif_time = "TO"
                write_time = "TO"
            rows[i] = f"Storm {kind} & {n} & - & {num_states} & {num_trans} & {num_runs} & {inf_time} & {verif_time} & {write_time} \\\\ \hline"
        except FileNotFoundError as err:
            print(f'No Storm {kind} for n={n}, full error: {err}')
            rows[i] = f"Storm {kind} & {n} & - & TODO & TODO & TODO & TODO & TODO & TODO \\\\ \hline"
        except KeyError as err:
            print(f'No Storm {kind} for n={n}, full error: {err}')
            rows[i] = f"Storm {kind} & {n} & - & TODO & TODO & TODO & TODO & TODO & TODO \\\\ \hline"
    return '\n'.join(rows)

def generate_dice_rows(ns, lamb, tag, kind):
    rows = ['' for _ in ns]
    for i,n in enumerate(ns):
        try:
            dice_base = Path(f'final_results/stats/dice_flat/{tag}/rr/n-{n}_lamb-{lamb}')
            time_stats = pd.read_csv(dice_base / 'scalability.csv',index_col=0)
            if 'TIMEOUT' not in str(time_stats.loc['total_inference_time'].iloc[0]):
                bdd_stats = pd.read_csv(dice_base / 'bdd_sizes.csv',index_col=0)
                bdd_size = int(bdd_stats['0'].mean())
                num_runs = int(time_stats.loc['num_inference_calls'].iloc[0])
                inf_time = round(time_stats.loc['total_inference_time'].iloc[0],4)
                verif_time = round(time_stats.loc['verification_time'].iloc[0],4)
                write_time = round(time_stats.loc['file_write_time'].iloc[0],4)
            else:
                bdd_size = "TO"
                num_runs = "TO"
                inf_time = "TO"
                verif_time = "TO"
                write_time = "TO"
            rows[i] = f"Dice {kind} & {n} & {bdd_size} & - & - & {num_runs} & {inf_time} & {verif_time} & {write_time} \\\\ \hline"
        except FileNotFoundError as err:
            print(f'No Dice {kind} for n={n}, full error: {err}')
            rows[i] = f"Dice {kind} & {n} & - & TODO & TODO & TODO & TODO & TODO & TODO \\\\ \hline"
        except KeyError as err:
            print(f'No Dice {kind} for n={n}, full error: {err}')
            rows[i] = f"Dice {kind} & {n} & - & TODO & TODO & TODO & TODO & TODO & TODO \\\\ \hline"
    return '\n'.join(rows)



exhaustive_storm_ns = [2, 4, 6]
exhaustive_dice_ns = [2, 4, 6, 8, 10]
exhaustive_tag = "inf-exhaustive_comp-exhaustive"
restrictive_ns = [5,10,15,20]
restrictive_tag = "inf-min_representative_comp-rr_2n"


storm_exhaustive_all_rows = generate_storm_rows(ns=exhaustive_storm_ns, lamb=lamb, tag=exhaustive_tag, kind='Exhaustive')
storm_restrictive_all_rows = generate_storm_rows(ns=restrictive_ns, lamb=lamb, tag=restrictive_tag, kind='Restricted')
dice_exhaustive_all_rows = generate_dice_rows(ns=exhaustive_dice_ns, lamb=lamb, tag=exhaustive_tag, kind='Exhaustive')
dice_restrictive_all_rows = generate_dice_rows(ns=restrictive_ns, lamb=lamb, tag=restrictive_tag, kind='Restricted')


print(f"""
\\begin{{table*}}[]
\centering
\\resizebox{{\\textwidth}}{{!}}{{%
\\begin{{tabular}}{{|l|l|l|l|l|l|l|l|l|}}
\hline
\\textbf{{Method}}  & \\textbf{{n}} & \\textbf{{BDD Size}} & \\textbf{{\# States}} & \\textbf{{\# Transitions}} & \\textbf{{\# Solver Runs}} & \\textbf{{Inference Time (s)}} & \\textbf{{Verification Time (s)}} & \\textbf{{Model Setup Time (s)}} \\\\ \hline
{storm_exhaustive_all_rows}
{dice_exhaustive_all_rows}
{storm_restrictive_all_rows}
{dice_restrictive_all_rows}
\end{{tabular}}%
}}
\end{{table*}}
""")
