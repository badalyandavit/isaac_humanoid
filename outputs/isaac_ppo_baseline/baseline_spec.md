# Isaac Baseline Spec

| Field | Value |
|---|---|
| `baseline_name` | isaac_v0_official_humanoid_direct |
| `simulator_backend` | Isaac Lab |
| `task` | Isaac-Humanoid-Direct-v0 |
| `reward_version` | isaac_v0_official |
| `loss_version` | isaac_rsl_rl_ppo_default |
| `source` | Isaac Lab official direct humanoid task |
| `reference_url` | https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/modify_direct_rl_env.html |
| `comparison_note` | This is a separate Isaac Lab baseline. Do not compare reward values directly against Gymnasium/MuJoCo Humanoid-v5. |
| `simulator.dt` | 0.008333333333333333 |
| `simulator.decimation` | 2 |
| `simulator.control_dt` | 0.016666666666666666 |
| `simulator.episode_length_s` | 15.0 |
| `simulator.default_num_envs` | 4096 |
| `simulator.terrain` | plane |
| `simulator.static_friction` | 1.0 |
| `simulator.dynamic_friction` | 1.0 |
| `simulator.restitution` | 0.0 |
| `simulator.action_scale` | 1.0 |
| `simulator.action_space` | 21 |
| `simulator.observation_space` | 75 |
| `simulator.termination_height` | 0.8 |
| `reward.design_goal` | Official Isaac Lab direct humanoid reward. |
| `reward.progress_reward` | change in negative distance-to-target potential |
| `reward.alive_reward_scale` | 2.0 |
| `reward.heading_weight` | 0.5 |
| `reward.heading_full_reward_threshold` | 0.8 |
| `reward.up_weight` | 0.1 |
| `reward.up_reward_threshold` | 0.93 |
| `reward.actions_cost_scale` | 0.01 |
| `reward.energy_cost_scale` | 0.05 |
| `reward.dof_vel_scale` | 0.1 |
| `reward.dof_at_limit_cost` | subtract count of joints with scaled position > 0.98 |
| `reward.death_cost` | -1.0 |
| `reward.angular_velocity_scale` | 0.25 |
| `reward.contact_force_scale` | 0.01 |
| `reward.official_v0_parameters.heading_weight` | 0.5 |
| `reward.official_v0_parameters.up_weight` | 0.1 |
| `reward.official_v0_parameters.energy_cost_scale` | 0.05 |
| `reward.official_v0_parameters.actions_cost_scale` | 0.01 |
| `reward.official_v0_parameters.alive_reward_scale` | 2.0 |
| `reward.official_v0_parameters.dof_vel_scale` | 0.1 |
| `reward.official_v0_parameters.death_cost` | -1.0 |
| `reward.official_v0_parameters.termination_height` | 0.8 |
| `reward.official_v0_parameters.angular_velocity_scale` | 0.25 |
| `reward.official_v0_parameters.contact_force_scale` | 0.01 |
| `reward.configured_parameters.heading_weight` | 0.5 |
| `reward.configured_parameters.up_weight` | 0.1 |
| `reward.configured_parameters.energy_cost_scale` | 0.05 |
| `reward.configured_parameters.actions_cost_scale` | 0.01 |
| `reward.configured_parameters.alive_reward_scale` | 2.0 |
| `reward.configured_parameters.dof_vel_scale` | 0.1 |
| `reward.configured_parameters.death_cost` | -1.0 |
| `reward.configured_parameters.termination_height` | 0.8 |
| `reward.configured_parameters.angular_velocity_scale` | 0.25 |
| `reward.configured_parameters.contact_force_scale` | 0.01 |
| `reward.auto_hydra_overrides` | [] |
| `reward.notes` | ['V0 keeps the official Isaac Lab reward coefficients unchanged.'] |
| `training.algorithm` | RSL-RL PPO |
| `training.loss_version` | isaac_rsl_rl_ppo_default |
| `training.loss_note` | V1 changes Isaac reward coefficients only; PPO loss is unchanged. |
| `training.num_envs` | 4096 |
| `training.num_steps_per_env` | 32 |
| `training.max_iterations` | 115 |
| `training.configured_total_timesteps` | 15000000 |
| `training.expected_env_steps` | 15073280 |
| `training.device` | cuda:0 |
