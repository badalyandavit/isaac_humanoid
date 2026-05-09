# Isaac Baseline Spec

| Field | Value |
|---|---|
| `baseline_name` | isaac_v10_balanced_gait_reward_humanoid_direct |
| `simulator_backend` | Isaac Lab |
| `task` | Isaac-Humanoid-V10-Direct-v0 |
| `reward_version` | isaac_v10_balanced_gait_reward |
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
| `simulator.termination_height` | 0.95 |
| `reward.design_goal` | Build on V9's stable upright locomotion by reducing lateral drift and one-sided foot-contact dominance. |
| `reward.custom_isaac_task` | True |
| `reward.progress_reward` | change in negative distance-to-target potential |
| `reward.alive_reward_scale` | 0.95 |
| `reward.heading_weight` | 1.0 |
| `reward.heading_full_reward_threshold` | 0.8 |
| `reward.up_weight` | 0.9 |
| `reward.up_reward_threshold` | 0.93 |
| `reward.actions_cost_scale` | 0.03 |
| `reward.energy_cost_scale` | 0.09 |
| `reward.dof_vel_scale` | 0.1 |
| `reward.dof_at_limit_cost` | subtract count of joints with scaled position > 0.98 |
| `reward.death_cost` | -4.0 |
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
| `reward.configured_parameters.heading_weight` | 1.0 |
| `reward.configured_parameters.up_weight` | 0.9 |
| `reward.configured_parameters.energy_cost_scale` | 0.09 |
| `reward.configured_parameters.actions_cost_scale` | 0.03 |
| `reward.configured_parameters.alive_reward_scale` | 0.95 |
| `reward.configured_parameters.dof_vel_scale` | 0.1 |
| `reward.configured_parameters.death_cost` | -4.0 |
| `reward.configured_parameters.termination_height` | 0.95 |
| `reward.configured_parameters.angular_velocity_scale` | 0.25 |
| `reward.configured_parameters.contact_force_scale` | 0.01 |
| `reward.custom_v4_parameters.height_target` | 1.28 |
| `reward.custom_v4_parameters.height_bonus_scale` | 0.0 |
| `reward.custom_v4_parameters.height_tracking_penalty_scale` | 2.0 |
| `reward.custom_v4_parameters.low_height_threshold` | 1.1 |
| `reward.custom_v4_parameters.low_height_penalty_scale` | 3.2 |
| `reward.custom_v4_parameters.high_height_threshold` | 1.46 |
| `reward.custom_v4_parameters.high_height_penalty_scale` | 5.0 |
| `reward.custom_v4_parameters.torso_low_height` | 1.04 |
| `reward.custom_v4_parameters.torso_low_penalty_scale` | 2.5 |
| `reward.custom_v4_parameters.arm_low_height` | 0.7 |
| `reward.custom_v4_parameters.arm_low_penalty_scale` | 4.0 |
| `reward.custom_v4_parameters.leg_pose_penalty_scale` | 0.3 |
| `reward.custom_v4_parameters.arm_pose_penalty_scale` | 1.7 |
| `reward.custom_v4_parameters.action_rate_penalty_scale` | 0.075 |
| `reward.custom_v4_parameters.vertical_velocity_penalty_scale` | 2.2 |
| `reward.custom_v4_parameters.arm_action_penalty_scale` | 0.75 |
| `reward.custom_v4_parameters.arm_velocity_penalty_scale` | 0.03 |
| `reward.custom_v4_parameters.leg_action_symmetry_penalty_scale` | 0.12 |
| `reward.custom_v4_parameters.leg_pose_symmetry_penalty_scale` | 0.06 |
| `reward.custom_v4_parameters.non_foot_low_height` | 0.65 |
| `reward.custom_v4_parameters.non_foot_low_penalty_scale` | 4.0 |
| `reward.custom_v4_parameters.foot_air_height` | 0.22 |
| `reward.custom_v4_parameters.foot_air_penalty_scale` | 0.35 |
| `reward.custom_v4_parameters.foot_slip_height` | 0.18 |
| `reward.custom_v4_parameters.foot_slip_penalty_scale` | 0.28 |
| `reward.custom_v4_parameters.target_forward_velocity` | 1.0 |
| `reward.custom_v4_parameters.forward_velocity_reward_scale` | 1.25 |
| `reward.custom_v4_parameters.forward_velocity_sigma` | 0.55 |
| `reward.custom_v4_parameters.forward_velocity_tracking_penalty_scale` | 0.2 |
| `reward.custom_v4_parameters.max_forward_velocity` | 1.35 |
| `reward.custom_v4_parameters.high_forward_velocity_penalty_scale` | 1.2 |
| `reward.custom_v4_parameters.lateral_velocity_penalty_scale` | 1.1 |
| `reward.custom_v4_parameters.low_speed_threshold` | 0.5 |
| `reward.custom_v4_parameters.low_speed_vertical_penalty_scale` | 3.0 |
| `reward.custom_v4_parameters.arm_high_height` | 1.44 |
| `reward.custom_v4_parameters.arm_high_penalty_scale` | 5.0 |
| `reward.custom_v4_parameters.foot_contact_height` | 0.17 |
| `reward.custom_v4_parameters.foot_contact_force_threshold` | 1.0 |
| `reward.custom_v4_parameters.single_foot_contact_reward_scale` | 0.16 |
| `reward.custom_v4_parameters.foot_contact_switch_reward_scale` | 0.08 |
| `reward.custom_v4_parameters.no_foot_contact_penalty_scale` | 0.95 |
| `reward.custom_v4_parameters.double_foot_contact_penalty_scale` | 0.12 |
| `reward.custom_v4_parameters.foot_contact_balance_penalty_scale` | 1.85 |
| `reward.custom_v4_parameters.foot_contact_ema_decay` | 0.97 |
| `reward.custom_v4_parameters.foot_contact_transition_reward_scale` | 0.17 |
| `reward.custom_v4_parameters.foot_contact_transition_target` | 0.3 |
| `reward.custom_v4_parameters.soft_single_foot_contact_reward_scale` | 0.3 |
| `reward.custom_v4_parameters.swing_foot_clearance_height` | 0.25 |
| `reward.custom_v4_parameters.swing_foot_clearance_reward_scale` | 0.12 |
| `reward.custom_v4_parameters.foot_height_difference_target` | 0.1 |
| `reward.custom_v4_parameters.foot_height_difference_reward_scale` | 0.12 |
| `reward.custom_v4_parameters.step_length_target` | 0.26 |
| `reward.custom_v4_parameters.step_length_reward_scale` | 0.08 |
| `reward.custom_v4_parameters.max_foot_lateral_distance` | 0.4 |
| `reward.custom_v4_parameters.foot_lateral_distance_penalty_scale` | 0.25 |
| `reward.custom_v4_parameters.gait_curriculum_steps` | 24000.0 |
| `reward.custom_v4_parameters.gait_curriculum_start` | 0.2 |
| `reward.parameter_changes_from_v0.heading_weight.official_v0` | 0.5 |
| `reward.parameter_changes_from_v0.heading_weight.configured` | 1.0 |
| `reward.parameter_changes_from_v0.up_weight.official_v0` | 0.1 |
| `reward.parameter_changes_from_v0.up_weight.configured` | 0.9 |
| `reward.parameter_changes_from_v0.energy_cost_scale.official_v0` | 0.05 |
| `reward.parameter_changes_from_v0.energy_cost_scale.configured` | 0.09 |
| `reward.parameter_changes_from_v0.actions_cost_scale.official_v0` | 0.01 |
| `reward.parameter_changes_from_v0.actions_cost_scale.configured` | 0.03 |
| `reward.parameter_changes_from_v0.alive_reward_scale.official_v0` | 2.0 |
| `reward.parameter_changes_from_v0.alive_reward_scale.configured` | 0.95 |
| `reward.parameter_changes_from_v0.death_cost.official_v0` | -1.0 |
| `reward.parameter_changes_from_v0.death_cost.configured` | -4.0 |
| `reward.parameter_changes_from_v0.termination_height.official_v0` | 0.8 |
| `reward.parameter_changes_from_v0.termination_height.configured` | 0.95 |
| `reward.auto_hydra_overrides` | ['env.heading_weight=1.0', 'env.up_weight=0.9', 'env.energy_cost_scale=0.09', 'env.actions_cost_scale=0.03', 'env.alive_reward_scale=0.95', 'env.death_cost=-4.0', 'env.termination_height=0.95', 'env.height_target=1.28', 'env.height_bonus_scale=0.0', 'env.height_tracking_penalty_scale=2.0', 'env.low_height_threshold=1.1', 'env.low_height_penalty_scale=3.2', 'env.high_height_threshold=1.46', 'env.high_height_penalty_scale=5.0', 'env.torso_low_height=1.04', 'env.torso_low_penalty_scale=2.5', 'env.arm_low_height=0.7', 'env.arm_low_penalty_scale=4.0', 'env.leg_pose_penalty_scale=0.3', 'env.arm_pose_penalty_scale=1.7', 'env.action_rate_penalty_scale=0.075', 'env.vertical_velocity_penalty_scale=2.2', 'env.arm_action_penalty_scale=0.75', 'env.arm_velocity_penalty_scale=0.03', 'env.leg_action_symmetry_penalty_scale=0.12', 'env.leg_pose_symmetry_penalty_scale=0.06', 'env.non_foot_low_height=0.65', 'env.non_foot_low_penalty_scale=4.0', 'env.foot_air_height=0.22', 'env.foot_air_penalty_scale=0.35', 'env.foot_slip_height=0.18', 'env.foot_slip_penalty_scale=0.28', 'env.target_forward_velocity=1.0', 'env.forward_velocity_reward_scale=1.25', 'env.forward_velocity_sigma=0.55', 'env.forward_velocity_tracking_penalty_scale=0.2', 'env.max_forward_velocity=1.35', 'env.high_forward_velocity_penalty_scale=1.2', 'env.lateral_velocity_penalty_scale=1.1', 'env.low_speed_threshold=0.5', 'env.low_speed_vertical_penalty_scale=3.0', 'env.arm_high_height=1.44', 'env.arm_high_penalty_scale=5.0', 'env.foot_contact_height=0.17', 'env.foot_contact_force_threshold=1.0', 'env.single_foot_contact_reward_scale=0.16', 'env.foot_contact_switch_reward_scale=0.08', 'env.no_foot_contact_penalty_scale=0.95', 'env.double_foot_contact_penalty_scale=0.12', 'env.foot_contact_balance_penalty_scale=1.85', 'env.foot_contact_ema_decay=0.97', 'env.foot_contact_transition_reward_scale=0.17', 'env.foot_contact_transition_target=0.3', 'env.soft_single_foot_contact_reward_scale=0.3', 'env.swing_foot_clearance_height=0.25', 'env.swing_foot_clearance_reward_scale=0.12', 'env.foot_height_difference_target=0.1', 'env.foot_height_difference_reward_scale=0.12', 'env.step_length_target=0.26', 'env.step_length_reward_scale=0.08', 'env.max_foot_lateral_distance=0.4', 'env.foot_lateral_distance_penalty_scale=0.25', 'env.gait_curriculum_steps=24000.0', 'env.gait_curriculum_start=0.2'] |
| `reward.custom_v4_reward_terms` | ['height bonus for maintaining torso/root height near target', 'height tracking penalty to avoid jumping above the target posture', 'low torso/root height penalty', 'high torso/root height penalty to discourage hopping', 'low torso/pelvis/head body penalty', 'low arm/hand body penalty as a proxy for arm-supported crawling', 'high arm/hand body penalty to discourage raised-arm balance exploits', 'leg joint pose penalty to discourage deep crouch', 'arm joint pose penalty to discourage arm-driven locomotion', 'arm action magnitude penalty to discourage arm-driven locomotion', 'arm joint velocity penalty', 'leg action and pose symmetry penalties', 'target forward velocity reward', 'forward velocity tracking and high-speed penalties', 'lateral velocity penalty', 'low-speed vertical bounce penalty', 'action-rate penalty for smoother motion', 'vertical velocity penalty to discourage bouncing', 'non-foot low-body proxy penalty', 'feet airborne and foot-slip proxy penalties', 'single-foot contact, foot-switch, no-contact, double-contact, and foot-balance terms', 'soft foot-contact transition reward', 'soft single-support and foot-height-difference rewards', 'swing-foot clearance and step-length rewards', 'foot lateral spread penalty', 'optional curriculum ramp for gait/contact shaping', "custom reward diagnostics under extras['log']"] |
| `reward.notes` | ['V10 targets the V9 failure mode of stable forward motion with strong left/right contact imbalance and lateral drift.', "It keeps V9's permissive survival envelope, because V8 showed that hard step constraints can collapse episode length.", 'It strengthens lateral-velocity and long-term foot-contact balance penalties.', 'It reduces the soft single-support, step-length, and foot-height-difference rewards so one-legged shuffling is less attractive.', 'It uses a slightly longer gait curriculum so balance/contact pressure ramps in after upright locomotion is established.'] |
| `training.algorithm` | RSL-RL PPO |
| `training.loss_version` | isaac_rsl_rl_ppo_default |
| `training.loss_note` | Isaac shaped variants change reward coefficients only; PPO loss is unchanged. |
| `training.num_envs` | 4096 |
| `training.num_steps_per_env` | 32 |
| `training.max_iterations` | 1526 |
| `training.configured_total_timesteps` | 200000000 |
| `training.expected_env_steps` | 200015872 |
| `training.device` | cuda:0 |
