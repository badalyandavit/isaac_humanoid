# Fair PPO/SAC Evaluation

| method | num_trained_agents_used | aggregation_method | total_env_steps | mean_return | median_return | q25_return | fall_rate | action_l2_norm | action_smoothness |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single PPO | 1 | mean | 14999552 | 5992 | 6594 | 6561 | 0.2 | 1.54 | 0.1398 |
| PPO Action Average K=2 | 2 | mean | 9994240 | 755.8 | 766.9 | 703.2 | 1 | 1.007 | 0.04027 |
| PPO Action Average K=3 | 3 | mean | 14991360 | 624.9 | 607.6 | 545.7 | 1 | 0.8327 | 0.02667 |
