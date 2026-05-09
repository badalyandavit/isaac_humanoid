# Isaac Learning Curves

## Runs
- `2026-05-09_13-06-26_baseline` -> Isaac V0
- `2026-05-09_13-04-55_upright_controlled_v1` -> Isaac V1
- `2026-05-09_13-35-58_mild_upright_v2` -> Isaac V2
- `2026-05-09_13-55-22_tall_upright_v3` -> Isaac V3
- `2026-05-09_17-11-38_morphology_reward_v4` -> Isaac V4
- `2026-05-09_17-26-36_anti_jump_morphology_v5` -> Isaac V5
- `2026-05-09_17-48-40_diagnostic_gait_v6` -> Isaac V6
- `2026-05-09_18-15-12_contact_gait_v7` -> Isaac V7
- `2026-05-09_20-17-00_step_transition_v8` -> Isaac V8
- `2026-05-09_20-51-36_curriculum_gait_v9` -> Isaac V9
- `2026-05-09_21-20-09_balanced_gait_v10` -> Isaac V10
- `2026-05-09_21-56-10_grounded_gait_v11` -> Isaac V11

## Figures
- [isaac_reward.png](isaac_reward.png)
- [isaac_episode_length.png](isaac_episode_length.png)
- [isaac_losses.png](isaac_losses.png)
- [isaac_throughput.png](isaac_throughput.png)
- [isaac_action_noise.png](isaac_action_noise.png)

## Available Scalar Tags
- **Isaac V0**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time
- **Isaac V1**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time
- **Isaac V10**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time, custom/action_rate_penalty, custom/arm_action_penalty, custom/arm_high_penalty, custom/arm_low_penalty, custom/arm_pose_penalty, custom/arm_velocity_penalty, custom/double_foot_contact_penalty, custom/foot_air_penalty, custom/foot_contact_balance_penalty, custom/foot_contact_switch_reward, custom/foot_contact_transition_reward, custom/foot_height_difference, custom/foot_height_difference_reward, custom/foot_lateral_distance, custom/foot_lateral_distance_penalty, custom/foot_slip_penalty, custom/forward_velocity, custom/forward_velocity_reward, custom/forward_velocity_tracking_penalty, custom/gait_curriculum_scale, custom/height_bonus, custom/height_tracking_penalty, custom/high_forward_velocity_penalty, custom/high_height_penalty, custom/lateral_velocity, custom/lateral_velocity_penalty, custom/left_foot_contact, custom/leg_action_symmetry_penalty, custom/leg_pose_penalty, custom/leg_pose_symmetry_penalty, custom/low_height_penalty, custom/low_speed_vertical_penalty, custom/no_foot_contact_penalty, custom/non_foot_low_penalty, custom/right_foot_contact, custom/root_height, custom/single_foot_contact_reward, custom/soft_single_foot_contact_reward, custom/step_length, custom/step_length_reward, custom/swing_foot_clearance_reward, custom/torso_low_penalty, custom/total_reward, custom/vertical_velocity_penalty
- **Isaac V11**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time, custom/action_rate_penalty, custom/arm_action_penalty, custom/arm_high_penalty, custom/arm_low_penalty, custom/arm_pose_penalty, custom/arm_velocity_penalty, custom/double_foot_contact_penalty, custom/foot_air_penalty, custom/foot_contact_balance_penalty, custom/foot_contact_switch_reward, custom/foot_contact_transition_reward, custom/foot_height_difference, custom/foot_height_difference_penalty, custom/foot_height_difference_reward, custom/foot_lateral_distance, custom/foot_lateral_distance_penalty, custom/foot_slip_penalty, custom/forward_velocity, custom/forward_velocity_reward, custom/forward_velocity_tracking_penalty, custom/gait_curriculum_scale, custom/height_bonus, custom/height_tracking_penalty, custom/high_forward_velocity_penalty, custom/high_height_penalty, custom/lateral_velocity, custom/lateral_velocity_penalty, custom/left_foot_contact, custom/leg_action_symmetry_penalty, custom/leg_pose_penalty, custom/leg_pose_symmetry_penalty, custom/low_height_penalty, custom/low_speed_vertical_penalty, custom/no_foot_contact_penalty, custom/non_foot_low_penalty, custom/right_foot_contact, custom/root_height, custom/single_foot_contact_reward, custom/soft_single_foot_contact_reward, custom/step_length, custom/step_length_reward, custom/swing_foot_clearance_reward, custom/swing_foot_high_penalty, custom/torso_low_penalty, custom/total_reward, custom/vertical_velocity_penalty
- **Isaac V2**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time
- **Isaac V3**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time
- **Isaac V4**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time
- **Isaac V5**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time
- **Isaac V6**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time, custom/action_rate_penalty, custom/arm_action_penalty, custom/arm_low_penalty, custom/arm_pose_penalty, custom/arm_velocity_penalty, custom/foot_air_penalty, custom/foot_slip_penalty, custom/height_bonus, custom/height_tracking_penalty, custom/high_height_penalty, custom/leg_action_symmetry_penalty, custom/leg_pose_penalty, custom/leg_pose_symmetry_penalty, custom/low_height_penalty, custom/non_foot_low_penalty, custom/root_height, custom/torso_low_penalty, custom/total_reward, custom/vertical_velocity_penalty
- **Isaac V7**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time, custom/action_rate_penalty, custom/arm_action_penalty, custom/arm_high_penalty, custom/arm_low_penalty, custom/arm_pose_penalty, custom/arm_velocity_penalty, custom/double_foot_contact_penalty, custom/foot_air_penalty, custom/foot_contact_balance_penalty, custom/foot_contact_switch_reward, custom/foot_slip_penalty, custom/forward_velocity, custom/forward_velocity_reward, custom/height_bonus, custom/height_tracking_penalty, custom/high_height_penalty, custom/lateral_velocity, custom/lateral_velocity_penalty, custom/left_foot_contact, custom/leg_action_symmetry_penalty, custom/leg_pose_penalty, custom/leg_pose_symmetry_penalty, custom/low_height_penalty, custom/low_speed_vertical_penalty, custom/no_foot_contact_penalty, custom/non_foot_low_penalty, custom/right_foot_contact, custom/root_height, custom/single_foot_contact_reward, custom/torso_low_penalty, custom/total_reward, custom/vertical_velocity_penalty
- **Isaac V8**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time, custom/action_rate_penalty, custom/arm_action_penalty, custom/arm_high_penalty, custom/arm_low_penalty, custom/arm_pose_penalty, custom/arm_velocity_penalty, custom/double_foot_contact_penalty, custom/foot_air_penalty, custom/foot_contact_balance_penalty, custom/foot_contact_switch_reward, custom/foot_contact_transition_reward, custom/foot_lateral_distance, custom/foot_lateral_distance_penalty, custom/foot_slip_penalty, custom/forward_velocity, custom/forward_velocity_reward, custom/forward_velocity_tracking_penalty, custom/height_bonus, custom/height_tracking_penalty, custom/high_forward_velocity_penalty, custom/high_height_penalty, custom/lateral_velocity, custom/lateral_velocity_penalty, custom/left_foot_contact, custom/leg_action_symmetry_penalty, custom/leg_pose_penalty, custom/leg_pose_symmetry_penalty, custom/low_height_penalty, custom/low_speed_vertical_penalty, custom/no_foot_contact_penalty, custom/non_foot_low_penalty, custom/right_foot_contact, custom/root_height, custom/single_foot_contact_reward, custom/step_length, custom/step_length_reward, custom/swing_foot_clearance_reward, custom/torso_low_penalty, custom/total_reward, custom/vertical_velocity_penalty
- **Isaac V9**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time, custom/action_rate_penalty, custom/arm_action_penalty, custom/arm_high_penalty, custom/arm_low_penalty, custom/arm_pose_penalty, custom/arm_velocity_penalty, custom/double_foot_contact_penalty, custom/foot_air_penalty, custom/foot_contact_balance_penalty, custom/foot_contact_switch_reward, custom/foot_contact_transition_reward, custom/foot_height_difference, custom/foot_height_difference_reward, custom/foot_lateral_distance, custom/foot_lateral_distance_penalty, custom/foot_slip_penalty, custom/forward_velocity, custom/forward_velocity_reward, custom/forward_velocity_tracking_penalty, custom/gait_curriculum_scale, custom/height_bonus, custom/height_tracking_penalty, custom/high_forward_velocity_penalty, custom/high_height_penalty, custom/lateral_velocity, custom/lateral_velocity_penalty, custom/left_foot_contact, custom/leg_action_symmetry_penalty, custom/leg_pose_penalty, custom/leg_pose_symmetry_penalty, custom/low_height_penalty, custom/low_speed_vertical_penalty, custom/no_foot_contact_penalty, custom/non_foot_low_penalty, custom/right_foot_contact, custom/root_height, custom/single_foot_contact_reward, custom/soft_single_foot_contact_reward, custom/step_length, custom/step_length_reward, custom/swing_foot_clearance_reward, custom/torso_low_penalty, custom/total_reward, custom/vertical_velocity_penalty

## Latest Scalar Values
| method | tag | step | value |
| --- | --- | --- | --- |
| Isaac V0 | Loss/entropy | 114 | 26.17148780822754 |
| Isaac V0 | Loss/learning_rate | 114 | 0.00039018443203531206 |
| Isaac V0 | Loss/surrogate | 114 | 0.011929751373827457 |
| Isaac V0 | Loss/value_function | 114 | 628.869140625 |
| Isaac V0 | Perf/collection time | 114 | 0.2526280879974365 |
| Isaac V0 | Perf/learning_time | 114 | 0.05297064781188965 |
| Isaac V0 | Perf/total_fps | 114 | 428902.0 |
| Isaac V0 | Policy/mean_noise_std | 114 | 0.8439362049102783 |
| Isaac V0 | Train/mean_episode_length | 114 | 87.0999984741211 |
| Isaac V0 | Train/mean_episode_length/time | 37 | 87.0999984741211 |
| Isaac V0 | Train/mean_reward | 114 | 371.790771484375 |
| Isaac V0 | Train/mean_reward/time | 37 | 371.790771484375 |
| Isaac V1 | Loss/entropy | 114 | 25.798765182495117 |
| Isaac V1 | Loss/learning_rate | 114 | 0.00296296295709908 |
| Isaac V1 | Loss/surrogate | 114 | 0.00032487482530996203 |
| Isaac V1 | Loss/value_function | 114 | 485.10235595703125 |
| Isaac V1 | Perf/collection time | 114 | 0.26283812522888184 |
| Isaac V1 | Perf/learning_time | 114 | 0.05739426612854004 |
| Isaac V1 | Perf/total_fps | 114 | 409302.0 |
| Isaac V1 | Policy/mean_noise_std | 114 | 0.8269090056419373 |
| Isaac V1 | Train/mean_episode_length | 114 | 75.22000122070312 |
| Isaac V1 | Train/mean_episode_length/time | 40 | 75.22000122070312 |
| Isaac V1 | Train/mean_reward | 114 | 259.255615234375 |
| Isaac V1 | Train/mean_reward/time | 40 | 259.255615234375 |
| Isaac V10 | Loss/entropy | 1525 | -26.860942840576172 |
| Isaac V10 | Loss/learning_rate | 1525 | 9.999999747378752e-06 |
| Isaac V10 | Loss/surrogate | 1525 | 0.0039085387252271175 |
| Isaac V10 | Loss/value_function | 1525 | 52.69155502319336 |
| Isaac V10 | Perf/collection time | 1525 | 0.3112647533416748 |
| Isaac V10 | Perf/learning_time | 1525 | 0.05620121955871582 |
| Isaac V10 | Perf/total_fps | 1525 | 356691.0 |
| Isaac V10 | Policy/mean_noise_std | 1525 | 0.08839679509401321 |
| Isaac V10 | Train/mean_episode_length | 1525 | 783.3499755859375 |
| Isaac V10 | Train/mean_episode_length/time | 550 | 783.3499755859375 |
| Isaac V10 | Train/mean_reward | 1525 | 2923.268310546875 |
| Isaac V10 | Train/mean_reward/time | 550 | 2923.268310546875 |
| Isaac V10 | custom/action_rate_penalty | 1525 | 0.11748641729354858 |
| Isaac V10 | custom/arm_action_penalty | 1525 | 0.032235465943813324 |
| Isaac V10 | custom/arm_high_penalty | 1525 | 0.07145131379365921 |
| Isaac V10 | custom/arm_low_penalty | 1525 | 0.0002063737774733454 |
| Isaac V10 | custom/arm_pose_penalty | 1525 | 0.4228827953338623 |
| Isaac V10 | custom/arm_velocity_penalty | 1525 | 0.046324655413627625 |
| Isaac V10 | custom/double_foot_contact_penalty | 1525 | 0.0010253905784338713 |
| Isaac V10 | custom/foot_air_penalty | 1525 | 0.0 |
| Isaac V10 | custom/foot_contact_balance_penalty | 1525 | 0.6498940587043762 |
| Isaac V10 | custom/foot_contact_switch_reward | 1525 | 1.9531249563442543e-05 |
| Isaac V10 | custom/foot_contact_transition_reward | 1525 | 0.017633512616157532 |
| Isaac V10 | custom/foot_height_difference | 1525 | 0.6300363540649414 |
| Isaac V10 | custom/foot_height_difference_reward | 1525 | 0.07362359762191772 |
| Isaac V10 | custom/foot_lateral_distance | 1525 | 0.29757481813430786 |
| Isaac V10 | custom/foot_lateral_distance_penalty | 1525 | 0.00017015388584695756 |
| Isaac V10 | custom/foot_slip_penalty | 1525 | 0.22246423363685608 |
| Isaac V10 | custom/forward_velocity | 1525 | 1.0652201175689697 |
| Isaac V10 | custom/forward_velocity_reward | 1525 | 1.1169227361679077 |
| Isaac V10 | custom/forward_velocity_tracking_penalty | 1525 | 0.032286785542964935 |
| Isaac V10 | custom/gait_curriculum_scale | 1525 | 1.0 |
| Isaac V10 | custom/height_bonus | 1525 | 0.0 |
| Isaac V10 | custom/height_tracking_penalty | 1525 | 0.0018004857702180743 |
| Isaac V10 | custom/high_forward_velocity_penalty | 1525 | 0.003398512490093708 |
| Isaac V10 | custom/high_height_penalty | 1525 | 0.0 |
| Isaac V10 | custom/lateral_velocity | 1525 | 0.045579973608255386 |
| Isaac V10 | custom/lateral_velocity_penalty | 1525 | 0.06801775097846985 |
| Isaac V10 | custom/left_foot_contact | 1525 | 0.021515652537345886 |
| Isaac V10 | custom/leg_action_symmetry_penalty | 1525 | 0.04799335449934006 |
| Isaac V10 | custom/leg_pose_penalty | 1525 | 0.15235251188278198 |
| Isaac V10 | custom/leg_pose_symmetry_penalty | 1525 | 0.02229059301316738 |
| Isaac V10 | custom/low_height_penalty | 1525 | 0.004899327643215656 |
| Isaac V10 | custom/low_speed_vertical_penalty | 1525 | 0.002254553372040391 |
| Isaac V10 | custom/no_foot_contact_penalty | 1525 | 0.0023193359375 |
| Isaac V10 | custom/non_foot_low_penalty | 1525 | 0.10316573083400726 |
| Isaac V10 | custom/right_foot_contact | 1525 | 0.6138292551040649 |
| Isaac V10 | custom/root_height | 1525 | 1.3024311065673828 |
| Isaac V10 | custom/single_foot_contact_reward | 1525 | 0.15824219584465027 |
| Isaac V10 | custom/soft_single_foot_contact_reward | 1525 | 0.11432331800460815 |
| Isaac V10 | custom/step_length | 1525 | 0.27144700288772583 |
| Isaac V10 | custom/step_length_reward | 1525 | 0.04314489662647247 |
| Isaac V10 | custom/swing_foot_clearance_reward | 1525 | 0.11537331342697144 |
| Isaac V10 | custom/torso_low_penalty | 1525 | 0.09255048632621765 |
| Isaac V10 | custom/total_reward | 1525 | 3.7470602989196777 |
| Isaac V10 | custom/vertical_velocity_penalty | 1525 | 0.15160785615444183 |
| Isaac V11 | Loss/entropy | 1525 | -43.349002838134766 |
| Isaac V11 | Loss/learning_rate | 1525 | 9.999999747378752e-06 |
| Isaac V11 | Loss/surrogate | 1525 | 0.003949446603655815 |
| Isaac V11 | Loss/value_function | 1525 | 1.2400249242782593 |
| Isaac V11 | Perf/collection time | 1525 | 0.2566666603088379 |
| Isaac V11 | Perf/learning_time | 1525 | 0.053888797760009766 |
| Isaac V11 | Perf/total_fps | 1525 | 422056.0 |
| Isaac V11 | Policy/mean_noise_std | 1525 | 0.05659311264753342 |
| Isaac V11 | Train/mean_episode_length | 1525 | 899.0 |
| Isaac V11 | Train/mean_episode_length/time | 513 | 899.0 |
| Isaac V11 | Train/mean_reward | 1525 | 3914.06884765625 |
| Isaac V11 | Train/mean_reward/time | 513 | 3914.06884765625 |
| Isaac V11 | custom/action_rate_penalty | 1525 | 0.01273477915674448 |
| Isaac V11 | custom/arm_action_penalty | 1525 | 0.02223561704158783 |
| Isaac V11 | custom/arm_high_penalty | 1525 | 0.0005263654165901244 |
| Isaac V11 | custom/arm_low_penalty | 1525 | 0.0 |
| Isaac V11 | custom/arm_pose_penalty | 1525 | 0.41299140453338623 |
| Isaac V11 | custom/arm_velocity_penalty | 1525 | 0.027369700372219086 |
| Isaac V11 | custom/double_foot_contact_penalty | 1525 | 0.04362793266773224 |
| Isaac V11 | custom/foot_air_penalty | 1525 | 0.0 |
| Isaac V11 | custom/foot_contact_balance_penalty | 1525 | 0.019683700054883957 |
| Isaac V11 | custom/foot_contact_switch_reward | 1525 | 0.0006835937383584678 |
| Isaac V11 | custom/foot_contact_transition_reward | 1525 | 0.01700766570866108 |
| Isaac V11 | custom/foot_height_difference | 1525 | 0.015979483723640442 |
| Isaac V11 | custom/foot_height_difference_penalty | 1525 | 0.0 |
| Isaac V11 | custom/foot_height_difference_reward | 1525 | 0.0 |
| Isaac V11 | custom/foot_lateral_distance | 1525 | 0.08707720041275024 |
| Isaac V11 | custom/foot_lateral_distance_penalty | 1525 | 0.0 |
| Isaac V11 | custom/foot_slip_penalty | 1525 | 0.4926562011241913 |
| Isaac V11 | custom/forward_velocity | 1525 | 1.1100966930389404 |
| Isaac V11 | custom/forward_velocity_reward | 1525 | 1.1044617891311646 |
| Isaac V11 | custom/forward_velocity_tracking_penalty | 1525 | 0.022178081795573235 |
| Isaac V11 | custom/gait_curriculum_scale | 1525 | 1.0 |
| Isaac V11 | custom/height_bonus | 1525 | 0.0 |
| Isaac V11 | custom/height_tracking_penalty | 1525 | 0.00048474789946340024 |
| Isaac V11 | custom/high_forward_velocity_penalty | 1525 | 0.0 |
| Isaac V11 | custom/high_height_penalty | 1525 | 0.0 |
| Isaac V11 | custom/lateral_velocity | 1525 | -0.0906602293252945 |
| Isaac V11 | custom/lateral_velocity_penalty | 1525 | 0.010932441800832748 |
| Isaac V11 | custom/left_foot_contact | 1525 | 0.5572978854179382 |
| Isaac V11 | custom/leg_action_symmetry_penalty | 1525 | 0.017542289569973946 |
| Isaac V11 | custom/leg_pose_penalty | 1525 | 0.19325505197048187 |
| Isaac V11 | custom/leg_pose_symmetry_penalty | 1525 | 0.013833257369697094 |
| Isaac V11 | custom/low_height_penalty | 1525 | 0.0 |
| Isaac V11 | custom/low_speed_vertical_penalty | 1525 | 0.0028603929094970226 |
| Isaac V11 | custom/no_foot_contact_penalty | 1525 | 0.007177733816206455 |
| Isaac V11 | custom/non_foot_low_penalty | 1525 | 0.18800656497478485 |
| Isaac V11 | custom/right_foot_contact | 1525 | 0.4715269207954407 |
| Isaac V11 | custom/root_height | 1525 | 1.2538172006607056 |
| Isaac V11 | custom/single_foot_contact_reward | 1525 | 0.04455077648162842 |
| Isaac V11 | custom/soft_single_foot_contact_reward | 1525 | 0.010686933994293213 |
| Isaac V11 | custom/step_length | 1525 | 0.45980507135391235 |
| Isaac V11 | custom/step_length_reward | 1525 | 0.04878641292452812 |
| Isaac V11 | custom/swing_foot_clearance_reward | 1525 | 0.0 |
| Isaac V11 | custom/swing_foot_high_penalty | 1525 | 0.0 |
| Isaac V11 | custom/torso_low_penalty | 1525 | 0.12940478324890137 |
| Isaac V11 | custom/total_reward | 1525 | 4.342767238616943 |
| Isaac V11 | custom/vertical_velocity_penalty | 1525 | 0.14506235718727112 |
| Isaac V2 | Loss/entropy | 1525 | 11.725503921508789 |
| Isaac V2 | Loss/learning_rate | 1525 | 0.00011390625149942935 |
| Isaac V2 | Loss/surrogate | 1525 | -0.0013880010228604078 |
| Isaac V2 | Loss/value_function | 1525 | 6933.48193359375 |
| Isaac V2 | Perf/collection time | 1525 | 0.28447985649108887 |
| Isaac V2 | Perf/learning_time | 1525 | 0.05452394485473633 |
| Isaac V2 | Perf/total_fps | 1525 | 386638.0 |
| Isaac V2 | Policy/mean_noise_std | 1525 | 0.46027183532714844 |
| Isaac V2 | Train/mean_episode_length | 1525 | 824.1400146484375 |
| Isaac V2 | Train/mean_episode_length/time | 530 | 824.1400146484375 |
| Isaac V2 | Train/mean_reward | 1525 | 17667.873046875 |
| Isaac V2 | Train/mean_reward/time | 530 | 17667.873046875 |
| Isaac V3 | Loss/entropy | 1525 | 10.733534812927246 |
| Isaac V3 | Loss/learning_rate | 1525 | 5.062499985797331e-05 |
| Isaac V3 | Loss/surrogate | 1525 | 0.00015359732788056135 |
| Isaac V3 | Loss/value_function | 1525 | 2669.6484375 |
| Isaac V3 | Perf/collection time | 1525 | 0.2920362949371338 |
| Isaac V3 | Perf/learning_time | 1525 | 0.054163455963134766 |
| Isaac V3 | Perf/total_fps | 1525 | 378602.0 |
| Isaac V3 | Policy/mean_noise_std | 1525 | 0.4356991946697235 |
| Isaac V3 | Train/mean_episode_length | 1525 | 826.8099975585938 |
| Isaac V3 | Train/mean_episode_length/time | 498 | 826.8099975585938 |
| Isaac V3 | Train/mean_reward | 1525 | 14296.09375 |
| Isaac V3 | Train/mean_reward/time | 498 | 14296.09375 |
| Isaac V4 | Loss/entropy | 1525 | 2.9326705932617188 |
| Isaac V4 | Loss/learning_rate | 1525 | 7.593750342493877e-05 |
| Isaac V4 | Loss/surrogate | 1525 | -0.0025717054959386587 |
| Isaac V4 | Loss/value_function | 1525 | 7104.96923828125 |
| Isaac V4 | Perf/collection time | 1525 | 0.2778961658477783 |
| Isaac V4 | Perf/learning_time | 1525 | 0.053562164306640625 |
| Isaac V4 | Perf/total_fps | 1525 | 395440.0 |
| Isaac V4 | Policy/mean_noise_std | 1525 | 0.29771688580513 |
| Isaac V4 | Train/mean_episode_length | 1525 | 836.6599731445312 |
| Isaac V4 | Train/mean_episode_length/time | 537 | 836.6599731445312 |
| Isaac V4 | Train/mean_reward | 1525 | 16887.814453125 |
| Isaac V4 | Train/mean_reward/time | 537 | 16887.814453125 |
| Isaac V5 | Loss/entropy | 1525 | 1.4284675121307373 |
| Isaac V5 | Loss/learning_rate | 1525 | 9.999999747378752e-06 |
| Isaac V5 | Loss/surrogate | 1525 | 0.0006832655053585768 |
| Isaac V5 | Loss/value_function | 1525 | 5133.7421875 |
| Isaac V5 | Perf/collection time | 1525 | 0.30011987686157227 |
| Isaac V5 | Perf/learning_time | 1525 | 0.05384016036987305 |
| Isaac V5 | Perf/total_fps | 1525 | 370301.0 |
| Isaac V5 | Policy/mean_noise_std | 1525 | 0.2821643054485321 |
| Isaac V5 | Train/mean_episode_length | 1525 | 820.280029296875 |
| Isaac V5 | Train/mean_episode_length/time | 541 | 820.280029296875 |
| Isaac V5 | Train/mean_reward | 1525 | 13995.548828125 |
| Isaac V5 | Train/mean_reward/time | 541 | 13995.548828125 |
| Isaac V6 | Loss/entropy | 1525 | -16.1234073638916 |
| Isaac V6 | Loss/learning_rate | 1525 | 2.2500000341096893e-05 |
| Isaac V6 | Loss/surrogate | 1525 | 0.00125967338681221 |
| Isaac V6 | Loss/value_function | 1525 | 507.5947265625 |
| Isaac V6 | Perf/collection time | 1525 | 0.2743830680847168 |
| Isaac V6 | Perf/learning_time | 1525 | 0.05424189567565918 |
| Isaac V6 | Perf/total_fps | 1525 | 398849.0 |
| Isaac V6 | Policy/mean_noise_std | 1525 | 0.13219721615314484 |
| Isaac V6 | Train/mean_episode_length | 1525 | 840.3699951171875 |
| Isaac V6 | Train/mean_episode_length/time | 507 | 840.3699951171875 |
| Isaac V6 | Train/mean_reward | 1525 | 5416.37939453125 |
| Isaac V6 | Train/mean_reward/time | 507 | 5416.37939453125 |
| Isaac V6 | custom/action_rate_penalty | 1525 | 0.04144524037837982 |
| Isaac V6 | custom/arm_action_penalty | 1525 | 0.07851266860961914 |
| Isaac V6 | custom/arm_low_penalty | 1525 | 0.0 |
| Isaac V6 | custom/arm_pose_penalty | 1525 | 0.6928985714912415 |
| Isaac V6 | custom/arm_velocity_penalty | 1525 | 0.12261493504047394 |
| Isaac V6 | custom/foot_air_penalty | 1525 | 0.03251953423023224 |
| Isaac V6 | custom/foot_slip_penalty | 1525 | 0.5743982195854187 |
| Isaac V6 | custom/height_bonus | 1525 | 0.0 |
| Isaac V6 | custom/height_tracking_penalty | 1525 | 0.009271955117583275 |
| Isaac V6 | custom/high_height_penalty | 1525 | 0.0 |
| Isaac V6 | custom/leg_action_symmetry_penalty | 1525 | 0.1174943819642067 |
| Isaac V6 | custom/leg_pose_penalty | 1525 | 0.18695873022079468 |
| Isaac V6 | custom/leg_pose_symmetry_penalty | 1525 | 0.01891234889626503 |
| Isaac V6 | custom/low_height_penalty | 1525 | 0.000562816858291626 |
| Isaac V6 | custom/non_foot_low_penalty | 1525 | 0.14777055382728577 |
| Isaac V6 | custom/root_height | 1525 | 1.2314282655715942 |
| Isaac V6 | custom/torso_low_penalty | 1525 | 0.25146782398223877 |
| Isaac V6 | custom/total_reward | 1525 | 6.539518356323242 |
| Isaac V6 | custom/vertical_velocity_penalty | 1525 | 0.3442801237106323 |
| Isaac V7 | Loss/entropy | 1525 | -20.05060577392578 |
| Isaac V7 | Loss/learning_rate | 1525 | 9.999999747378752e-06 |
| Isaac V7 | Loss/surrogate | 1525 | 0.01694907434284687 |
| Isaac V7 | Loss/value_function | 1525 | 155.17929077148438 |
| Isaac V7 | Perf/collection time | 1525 | 0.3295586109161377 |
| Isaac V7 | Perf/learning_time | 1525 | 0.0575716495513916 |
| Isaac V7 | Perf/total_fps | 1525 | 338573.0 |
| Isaac V7 | Policy/mean_noise_std | 1525 | 0.11687308549880981 |
| Isaac V7 | Train/mean_episode_length | 1525 | 766.77001953125 |
| Isaac V7 | Train/mean_episode_length/time | 534 | 766.77001953125 |
| Isaac V7 | Train/mean_reward | 1525 | 3312.07421875 |
| Isaac V7 | Train/mean_reward/time | 534 | 3312.07421875 |
| Isaac V7 | custom/action_rate_penalty | 1525 | 0.03157026320695877 |
| Isaac V7 | custom/arm_action_penalty | 1525 | 0.04544763267040253 |
| Isaac V7 | custom/arm_high_penalty | 1525 | 0.03842486813664436 |
| Isaac V7 | custom/arm_low_penalty | 1525 | 0.005340077448636293 |
| Isaac V7 | custom/arm_pose_penalty | 1525 | 0.8752660751342773 |
| Isaac V7 | custom/arm_velocity_penalty | 1525 | 0.056041404604911804 |
| Isaac V7 | custom/double_foot_contact_penalty | 1525 | 7.324219041038305e-05 |
| Isaac V7 | custom/foot_air_penalty | 1525 | 0.0003906250058207661 |
| Isaac V7 | custom/foot_contact_balance_penalty | 1525 | 0.16613680124282837 |
| Isaac V7 | custom/foot_contact_switch_reward | 1525 | 0.0002050781185971573 |
| Isaac V7 | custom/foot_slip_penalty | 1525 | 0.734333872795105 |
| Isaac V7 | custom/forward_velocity | 1525 | 1.705736517906189 |
| Isaac V7 | custom/forward_velocity_reward | 1525 | 1.38111412525177 |
| Isaac V7 | custom/height_bonus | 1525 | 0.0 |
| Isaac V7 | custom/height_tracking_penalty | 1525 | 0.004826311022043228 |
| Isaac V7 | custom/high_height_penalty | 1525 | 0.0 |
| Isaac V7 | custom/lateral_velocity | 1525 | -0.08259646594524384 |
| Isaac V7 | custom/lateral_velocity_penalty | 1525 | 0.022164756432175636 |
| Isaac V7 | custom/left_foot_contact | 1525 | 0.4772070646286011 |
| Isaac V7 | custom/leg_action_symmetry_penalty | 1525 | 0.05444374680519104 |
| Isaac V7 | custom/leg_pose_penalty | 1525 | 0.1238674521446228 |
| Isaac V7 | custom/leg_pose_symmetry_penalty | 1525 | 0.014131752774119377 |
| Isaac V7 | custom/low_height_penalty | 1525 | 0.0018887664191424847 |
| Isaac V7 | custom/low_speed_vertical_penalty | 1525 | 0.0017795511521399021 |
| Isaac V7 | custom/no_foot_contact_penalty | 1525 | 0.21730956435203552 |
| Isaac V7 | custom/non_foot_low_penalty | 1525 | 0.18394377827644348 |
| Isaac V7 | custom/right_foot_contact | 1525 | 0.2325674593448639 |
| Isaac V7 | custom/root_height | 1525 | 1.2480545043945312 |
| Isaac V7 | custom/single_foot_contact_reward | 1525 | 0.30322265625 |
| Isaac V7 | custom/torso_low_penalty | 1525 | 0.23142503201961517 |
| Isaac V7 | custom/total_reward | 1525 | 4.339468955993652 |
| Isaac V7 | custom/vertical_velocity_penalty | 1525 | 0.229265958070755 |
| Isaac V8 | Loss/entropy | 1525 | -39.459415435791016 |
| Isaac V8 | Loss/learning_rate | 1525 | 9.999999747378752e-06 |
| Isaac V8 | Loss/surrogate | 1525 | 0.009815449826419353 |
| Isaac V8 | Loss/value_function | 1525 | 43.09384536743164 |
| Isaac V8 | Perf/collection time | 1525 | 0.2792856693267822 |
| Isaac V8 | Perf/learning_time | 1525 | 0.055405378341674805 |
| Isaac V8 | Perf/total_fps | 1525 | 391620.0 |
| Isaac V8 | Policy/mean_noise_std | 1525 | 0.05231582000851631 |
| Isaac V8 | Train/mean_episode_length | 1525 | 108.73999786376953 |
| Isaac V8 | Train/mean_episode_length/time | 560 | 108.73999786376953 |
| Isaac V8 | Train/mean_reward | 1525 | 373.94073486328125 |
| Isaac V8 | Train/mean_reward/time | 560 | 373.94073486328125 |
| Isaac V8 | custom/action_rate_penalty | 1525 | 0.011030454188585281 |
| Isaac V8 | custom/arm_action_penalty | 1525 | 0.02621936798095703 |
| Isaac V8 | custom/arm_high_penalty | 1525 | 0.014442063868045807 |
| Isaac V8 | custom/arm_low_penalty | 1525 | 0.0051171667873859406 |
| Isaac V8 | custom/arm_pose_penalty | 1525 | 0.16998332738876343 |
| Isaac V8 | custom/arm_velocity_penalty | 1525 | 0.06914856284856796 |
| Isaac V8 | custom/double_foot_contact_penalty | 1525 | 0.03217773512005806 |
| Isaac V8 | custom/foot_air_penalty | 1525 | 0.0 |
| Isaac V8 | custom/foot_contact_balance_penalty | 1525 | 0.4176027774810791 |
| Isaac V8 | custom/foot_contact_switch_reward | 1525 | 0.0006835937383584678 |
| Isaac V8 | custom/foot_contact_transition_reward | 1525 | 0.02240467071533203 |
| Isaac V8 | custom/foot_lateral_distance | 1525 | 0.1918540745973587 |
| Isaac V8 | custom/foot_lateral_distance_penalty | 1525 | 0.00010182488767895848 |
| Isaac V8 | custom/foot_slip_penalty | 1525 | 0.18593184649944305 |
| Isaac V8 | custom/forward_velocity | 1525 | 1.1072971820831299 |
| Isaac V8 | custom/forward_velocity_reward | 1525 | 0.9343745112419128 |
| Isaac V8 | custom/forward_velocity_tracking_penalty | 1525 | 0.1542709767818451 |
| Isaac V8 | custom/height_bonus | 1525 | 0.0 |
| Isaac V8 | custom/height_tracking_penalty | 1525 | 0.02958439663052559 |
| Isaac V8 | custom/high_forward_velocity_penalty | 1525 | 0.002420473610982299 |
| Isaac V8 | custom/high_height_penalty | 1525 | 0.0 |
| Isaac V8 | custom/lateral_velocity | 1525 | 0.03399975225329399 |
| Isaac V8 | custom/lateral_velocity_penalty | 1525 | 0.059544533491134644 |
| Isaac V8 | custom/left_foot_contact | 1525 | 0.23551243543624878 |
| Isaac V8 | custom/leg_action_symmetry_penalty | 1525 | 0.0501057431101799 |
| Isaac V8 | custom/leg_pose_penalty | 1525 | 0.1560514271259308 |
| Isaac V8 | custom/leg_pose_symmetry_penalty | 1525 | 0.012679992243647575 |
| Isaac V8 | custom/low_height_penalty | 1525 | 0.38920649886131287 |
| Isaac V8 | custom/low_speed_vertical_penalty | 1525 | 0.006917872466146946 |
| Isaac V8 | custom/no_foot_contact_penalty | 1525 | 0.03974609449505806 |
| Isaac V8 | custom/non_foot_low_penalty | 1525 | 0.15507924556732178 |
| Isaac V8 | custom/right_foot_contact | 1525 | 0.5448521971702576 |
| Isaac V8 | custom/root_height | 1525 | 1.195937991142273 |
| Isaac V8 | custom/single_foot_contact_reward | 1525 | 0.2810424566268921 |
| Isaac V8 | custom/step_length | 1525 | 0.3146679997444153 |
| Isaac V8 | custom/step_length_reward | 1525 | 0.1203833520412445 |
| Isaac V8 | custom/swing_foot_clearance_reward | 1525 | 0.23495391011238098 |
| Isaac V8 | custom/torso_low_penalty | 1525 | 0.25755029916763306 |
| Isaac V8 | custom/total_reward | 1525 | 3.4126319885253906 |
| Isaac V8 | custom/vertical_velocity_penalty | 1525 | 0.16673146188259125 |
| Isaac V9 | Loss/entropy | 1525 | -27.721858978271484 |
| Isaac V9 | Loss/learning_rate | 1525 | 9.999999747378752e-06 |
| Isaac V9 | Loss/surrogate | 1525 | 0.0013601687969639897 |
| Isaac V9 | Loss/value_function | 1525 | 3.094311237335205 |
| Isaac V9 | Perf/collection time | 1525 | 0.2768254280090332 |
| Isaac V9 | Perf/learning_time | 1525 | 0.05401039123535156 |
| Isaac V9 | Perf/total_fps | 1525 | 396184.0 |
| Isaac V9 | Policy/mean_noise_std | 1525 | 0.0792279914021492 |
| Isaac V9 | Train/mean_episode_length | 1525 | 883.1199951171875 |
| Isaac V9 | Train/mean_episode_length/time | 544 | 883.1199951171875 |
| Isaac V9 | Train/mean_reward | 1525 | 4132.2509765625 |
| Isaac V9 | Train/mean_reward/time | 544 | 4132.2509765625 |
| Isaac V9 | custom/action_rate_penalty | 1525 | 0.011620492674410343 |
| Isaac V9 | custom/arm_action_penalty | 1525 | 0.018073568120598793 |
| Isaac V9 | custom/arm_high_penalty | 1525 | 0.0011753641301766038 |
| Isaac V9 | custom/arm_low_penalty | 1525 | 0.0 |
| Isaac V9 | custom/arm_pose_penalty | 1525 | 0.29849207401275635 |
| Isaac V9 | custom/arm_velocity_penalty | 1525 | 0.033625129610300064 |
| Isaac V9 | custom/double_foot_contact_penalty | 1525 | 0.0003808593610301614 |
| Isaac V9 | custom/foot_air_penalty | 1525 | 0.0 |
| Isaac V9 | custom/foot_contact_balance_penalty | 1525 | 0.15062491595745087 |
| Isaac V9 | custom/foot_contact_switch_reward | 1525 | 4.394531060825102e-05 |
| Isaac V9 | custom/foot_contact_transition_reward | 1525 | 0.024587448686361313 |
| Isaac V9 | custom/foot_height_difference | 1525 | 0.11369165778160095 |
| Isaac V9 | custom/foot_height_difference_reward | 1525 | 0.0791800320148468 |
| Isaac V9 | custom/foot_lateral_distance | 1525 | 0.11914199590682983 |
| Isaac V9 | custom/foot_lateral_distance_penalty | 1525 | 0.0 |
| Isaac V9 | custom/foot_slip_penalty | 1525 | 0.2695397138595581 |
| Isaac V9 | custom/forward_velocity | 1525 | 1.2790656089782715 |
| Isaac V9 | custom/forward_velocity_reward | 1525 | 1.060199499130249 |
| Isaac V9 | custom/forward_velocity_tracking_penalty | 1525 | 0.047552213072776794 |
| Isaac V9 | custom/gait_curriculum_scale | 1525 | 1.0 |
| Isaac V9 | custom/height_bonus | 1525 | 0.0 |
| Isaac V9 | custom/height_tracking_penalty | 1525 | 0.0029727118089795113 |
| Isaac V9 | custom/high_forward_velocity_penalty | 1525 | 2.183087963203434e-05 |
| Isaac V9 | custom/high_height_penalty | 1525 | 0.0 |
| Isaac V9 | custom/lateral_velocity | 1525 | -0.3535189628601074 |
| Isaac V9 | custom/lateral_velocity_penalty | 1525 | 0.06390887498855591 |
| Isaac V9 | custom/left_foot_contact | 1525 | 0.4094141125679016 |
| Isaac V9 | custom/leg_action_symmetry_penalty | 1525 | 0.02676556073129177 |
| Isaac V9 | custom/leg_pose_penalty | 1525 | 0.10190249234437943 |
| Isaac V9 | custom/leg_pose_symmetry_penalty | 1525 | 0.007163833826780319 |
| Isaac V9 | custom/low_height_penalty | 1525 | 0.0 |
| Isaac V9 | custom/low_speed_vertical_penalty | 1525 | 0.0016659273533150554 |
| Isaac V9 | custom/no_foot_contact_penalty | 1525 | 0.33984375 |
| Isaac V9 | custom/non_foot_low_penalty | 1525 | 0.1845557689666748 |
| Isaac V9 | custom/right_foot_contact | 1525 | 0.07945585250854492 |
| Isaac V9 | custom/root_height | 1525 | 1.233633041381836 |
| Isaac V9 | custom/single_foot_contact_reward | 1525 | 0.09786621481180191 |
| Isaac V9 | custom/soft_single_foot_contact_reward | 1525 | 0.1286221444606781 |
| Isaac V9 | custom/step_length | 1525 | 0.47883015871047974 |
| Isaac V9 | custom/step_length_reward | 1525 | 0.05692555382847786 |
| Isaac V9 | custom/swing_foot_clearance_reward | 1525 | 0.03200078755617142 |
| Isaac V9 | custom/torso_low_penalty | 1525 | 0.15852373838424683 |
| Isaac V9 | custom/total_reward | 1525 | 4.691680908203125 |
| Isaac V9 | custom/vertical_velocity_penalty | 1525 | 0.16558541357517242 |

Raw scalar data is stored in `isaac_scalars.csv`.
