This repo contains the tools `ExactAcc` and `ExactDP` for running tight privacy and accuracy bound synthesis as described in the paper:


>[Oakley, Lisa, Steven Holtzen, and Alina Oprea. "Synthesizing Tight Privacy and Accuracy Bounds via Weighted Model Counting," 2024 IEEE 37th Computer Security Foundations Symposium (CSF), 2024.](https://arxiv.org/abs/2402.16982)

This repo also contains all the experiment and plotting scripts to reproduce the results from the paper. To cite, please use:
```
@article{oakley2024synthesizing,
  title={Synthesizing Tight Privacy and Accuracy Bounds via Weighted Model Counting},
  author={Oakley, Lisa and Holtzen, Steven and Oprea, Alina},
  booktitle={2024 IEEE 37th Computer Security Foundations Symposium (CSF)}, 
  year={2024}
  }
```

## Reproducing Paper Results
`./plotting_scripts` contains scripts for plotting figures in the paper. In the `README.md`, and at the top of each script, there is a comment which tells you which experiment scripts need to be run before the plot can be made. The plotting scripts must be run from the project home directory (e.g. `python plotting_scripts/Fig2.py`).

## Running Experiments
`./experiment_scripts` contains all the scripts for running the experiments whose data appears in the paper. The experiment scripts must be run from the project home directory (e.g. `./experiment_scripts/RR_ExactDP_Restricted.sh`).

## Using ExactDP and ExactAcc directly
`ExactDP` and `ExactAcc` can be run directly with different parameters specified in the command line. Run with `-h` to see which options are available.

## Dependencies
To run the Weighted Model Counting (WMC) solution, we use the [Dice probabilistic programming language](https://github.com/SHoltzen/dice).

To run the DTMC model checker experiments, we use the [Stormpy python package](https://moves-rwth.github.io/stormpy/) for the [Storm model checker](https://www.stormchecker.org/).

