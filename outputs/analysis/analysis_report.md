# Humanoid PPO Analysis

Outputs root: `outputs`

## Generated files

- `run_summary.csv`: final training-log summaries.
- `main_experiment_table.csv`: comparison table, using `eval_summary.csv` when available.
- `eval_summary.csv`: copy of the collected checkpoint evaluation summary.
- `scaling_summary.csv`: copy of the scaling sweep summary.

## Main experiment table

| Method                            | N | Eval episodes | Mean return | Median return | 25% return | Fall rate | Robust score | Checkpoint    |
| --------------------------------- | - | ------------- | ----------- | ------------- | ---------- | --------- | ------------ | ------------- |
| Naive Average PPO                 | 4 | 5             | 6659        | 6649          | 6629       | 0         | 9953         | final_average |
| Baseline PPO                      | 1 | 5             | 353.5       | 357.1         | 342.8      | 1         | 21.34        | final         |
| Robust Heavy-Tail Cooperative PPO | 4 | 8             | 855.4       | 903.2         | 842.3      | 1         | 793.9        | final_best    |

## Source counts

- Training summaries: 9
- Evaluation summaries: 3
- Scaling rows: 4
