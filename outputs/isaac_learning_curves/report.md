# Isaac Learning Curves

## Runs
- `2026-05-09_13-06-26_baseline` -> Isaac V0
- `2026-05-09_13-04-55_upright_controlled_v1` -> Isaac V1
- `2026-05-09_17-11-38_morphology_reward_v4` -> Isaac V4
- `2026-05-09_20-51-36_curriculum_gait_v9` -> Isaac V9
- `2026-05-09_23-41-39_cadence_gait_v14` -> Isaac V14
- `2026-05-10_01-00-17_stable_lower_arms_v16` -> Isaac V16

## Figures
- [isaac_reward.png](isaac_reward.png)
- [isaac_episode_length.png](isaac_episode_length.png)
- [isaac_losses.png](isaac_losses.png)
- [isaac_throughput.png](isaac_throughput.png)
- [isaac_action_noise.png](isaac_action_noise.png)

## Available Scalar Tags
- **Isaac V0**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time
- **Isaac V1**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time
- **Isaac V14**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time, custom/action_rate_penalty, custom/arm_action_penalty, custom/arm_high_penalty, custom/arm_low_penalty, custom/arm_neutral_height_penalty, custom/arm_pose_penalty, custom/arm_velocity_penalty, custom/double_foot_contact_penalty, custom/foot_air_penalty, custom/foot_air_time_penalty, custom/foot_contact_balance_penalty, custom/foot_contact_switch_reward, custom/foot_contact_transition_reward, custom/foot_dominance_time, custom/foot_height_difference, custom/foot_height_difference_penalty, custom/foot_height_difference_reward, custom/foot_lateral_distance, custom/foot_lateral_distance_penalty, custom/foot_slip_penalty, custom/forward_velocity, custom/forward_velocity_reward, custom/forward_velocity_tracking_penalty, custom/gait_curriculum_scale, custom/height_bonus, custom/height_tracking_penalty, custom/high_forward_velocity_penalty, custom/high_height_penalty, custom/lateral_velocity, custom/lateral_velocity_penalty, custom/left_foot_contact, custom/leg_action_symmetry_penalty, custom/leg_pose_penalty, custom/leg_pose_symmetry_penalty, custom/low_height_penalty, custom/low_speed_vertical_penalty, custom/max_foot_air_time, custom/mean_foot_air_time, custom/no_foot_contact_penalty, custom/non_foot_low_penalty, custom/right_foot_contact, custom/root_height, custom/single_foot_contact_reward, custom/soft_foot_contact_switch_reward, custom/soft_single_foot_contact_reward, custom/stance_duration_penalty, custom/stance_foot_slip_penalty, custom/step_length, custom/step_length_reward, custom/swing_foot_clearance_reward, custom/swing_foot_high_penalty, custom/torso_low_penalty, custom/total_reward, custom/touchdown_reward, custom/underused_foot_contact_reward, custom/vertical_velocity_penalty
- **Isaac V16**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time, custom/action_rate_penalty, custom/arm_action_penalty, custom/arm_high_penalty, custom/arm_low_penalty, custom/arm_neutral_height_penalty, custom/arm_pose_penalty, custom/arm_velocity_penalty, custom/double_foot_contact_penalty, custom/foot_air_penalty, custom/foot_air_time_penalty, custom/foot_contact_balance_penalty, custom/foot_contact_switch_reward, custom/foot_contact_transition_reward, custom/foot_dominance_time, custom/foot_height_difference, custom/foot_height_difference_penalty, custom/foot_height_difference_reward, custom/foot_lateral_distance, custom/foot_lateral_distance_penalty, custom/foot_slip_penalty, custom/forward_velocity, custom/forward_velocity_reward, custom/forward_velocity_tracking_penalty, custom/gait_curriculum_scale, custom/height_bonus, custom/height_tracking_penalty, custom/high_forward_velocity_penalty, custom/high_height_penalty, custom/lateral_velocity, custom/lateral_velocity_penalty, custom/left_foot_contact, custom/leg_action_symmetry_penalty, custom/leg_pose_penalty, custom/leg_pose_symmetry_penalty, custom/low_height_penalty, custom/low_speed_vertical_penalty, custom/max_foot_air_time, custom/mean_foot_air_time, custom/no_foot_contact_penalty, custom/non_foot_low_penalty, custom/right_foot_contact, custom/root_height, custom/single_foot_contact_reward, custom/soft_foot_contact_switch_reward, custom/soft_single_foot_contact_reward, custom/stance_duration_penalty, custom/stance_foot_slip_penalty, custom/step_length, custom/step_length_reward, custom/swing_foot_clearance_reward, custom/swing_foot_high_penalty, custom/torso_low_penalty, custom/total_reward, custom/touchdown_reward, custom/underused_foot_contact_reward, custom/vertical_velocity_penalty
- **Isaac V4**: Loss/entropy, Loss/learning_rate, Loss/surrogate, Loss/value_function, Perf/collection time, Perf/learning_time, Perf/total_fps, Policy/mean_noise_std, Train/mean_episode_length, Train/mean_episode_length/time, Train/mean_reward, Train/mean_reward/time
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
| Isaac V14 | Loss/entropy | 1525 | -26.805021286010742 |
| Isaac V14 | Loss/learning_rate | 1525 | 9.999999747378752e-06 |
| Isaac V14 | Loss/surrogate | 1525 | 0.0017700997414067388 |
| Isaac V14 | Loss/value_function | 1525 | 36.70099639892578 |
| Isaac V14 | Perf/collection time | 1525 | 0.3104865550994873 |
| Isaac V14 | Perf/learning_time | 1525 | 0.05545377731323242 |
| Isaac V14 | Perf/total_fps | 1525 | 358178.0 |
| Isaac V14 | Policy/mean_noise_std | 1525 | 0.0974554717540741 |
| Isaac V14 | Train/mean_episode_length | 1525 | 899.0 |
| Isaac V14 | Train/mean_episode_length/time | 594 | 899.0 |
| Isaac V14 | Train/mean_reward | 1525 | 2799.899169921875 |
| Isaac V14 | Train/mean_reward/time | 594 | 2799.899169921875 |
| Isaac V14 | custom/action_rate_penalty | 1525 | 0.01978950947523117 |
| Isaac V14 | custom/arm_action_penalty | 1525 | 0.028343476355075836 |
| Isaac V14 | custom/arm_high_penalty | 1525 | 0.020950572565197945 |
| Isaac V14 | custom/arm_low_penalty | 1525 | 0.0 |
| Isaac V14 | custom/arm_neutral_height_penalty | 1525 | 0.13684943318367004 |
| Isaac V14 | custom/arm_pose_penalty | 1525 | 0.5732733607292175 |
| Isaac V14 | custom/arm_velocity_penalty | 1525 | 0.039734695106744766 |
| Isaac V14 | custom/double_foot_contact_penalty | 1525 | 0.04457031190395355 |
| Isaac V14 | custom/foot_air_penalty | 1525 | 0.0 |
| Isaac V14 | custom/foot_air_time_penalty | 1525 | 0.005052168853580952 |
| Isaac V14 | custom/foot_contact_balance_penalty | 1525 | 0.03919413685798645 |
| Isaac V14 | custom/foot_contact_switch_reward | 1525 | 0.007539062760770321 |
| Isaac V14 | custom/foot_contact_transition_reward | 1525 | 0.04644480720162392 |
| Isaac V14 | custom/foot_dominance_time | 1525 | 0.37633463740348816 |
| Isaac V14 | custom/foot_height_difference | 1525 | 0.02912771701812744 |
| Isaac V14 | custom/foot_height_difference_penalty | 1525 | 0.0 |
| Isaac V14 | custom/foot_height_difference_reward | 1525 | 0.0 |
| Isaac V14 | custom/foot_lateral_distance | 1525 | 0.23970508575439453 |
| Isaac V14 | custom/foot_lateral_distance_penalty | 1525 | 3.288145080659888e-07 |
| Isaac V14 | custom/foot_slip_penalty | 1525 | 0.40600889921188354 |
| Isaac V14 | custom/forward_velocity | 1525 | 0.8925864696502686 |
| Isaac V14 | custom/forward_velocity_reward | 1525 | 1.0601978302001953 |
| Isaac V14 | custom/forward_velocity_tracking_penalty | 1525 | 0.012984026223421097 |
| Isaac V14 | custom/gait_curriculum_scale | 1525 | 1.0 |
| Isaac V14 | custom/height_bonus | 1525 | 0.0 |
| Isaac V14 | custom/height_tracking_penalty | 1525 | 0.0002152478409698233 |
| Isaac V14 | custom/high_forward_velocity_penalty | 1525 | 2.6735982828540727e-05 |
| Isaac V14 | custom/high_height_penalty | 1525 | 0.0 |
| Isaac V14 | custom/lateral_velocity | 1525 | -0.001157946651801467 |
| Isaac V14 | custom/lateral_velocity_penalty | 1525 | 0.01502903550863266 |
| Isaac V14 | custom/left_foot_contact | 1525 | 0.5865225791931152 |
| Isaac V14 | custom/leg_action_symmetry_penalty | 1525 | 0.031123295426368713 |
| Isaac V14 | custom/leg_pose_penalty | 1525 | 0.1359366476535797 |
| Isaac V14 | custom/leg_pose_symmetry_penalty | 1525 | 0.014455015771090984 |
| Isaac V14 | custom/low_height_penalty | 1525 | 0.0 |
| Isaac V14 | custom/low_speed_vertical_penalty | 1525 | 0.0023201871663331985 |
| Isaac V14 | custom/max_foot_air_time | 1525 | 0.06525635719299316 |
| Isaac V14 | custom/mean_foot_air_time | 1525 | 0.0334562212228775 |
| Isaac V14 | custom/no_foot_contact_penalty | 1525 | 0.05793457105755806 |
| Isaac V14 | custom/non_foot_low_penalty | 1525 | 0.19160175323486328 |
| Isaac V14 | custom/right_foot_contact | 1525 | 0.4916113018989563 |
| Isaac V14 | custom/root_height | 1525 | 1.265995979309082 |
| Isaac V14 | custom/single_foot_contact_reward | 1525 | 0.03758788853883743 |
| Isaac V14 | custom/soft_foot_contact_switch_reward | 1525 | 0.0017106770537793636 |
| Isaac V14 | custom/soft_single_foot_contact_reward | 1525 | 0.012728096917271614 |
| Isaac V14 | custom/stance_duration_penalty | 1525 | 0.0542219802737236 |
| Isaac V14 | custom/stance_foot_slip_penalty | 1525 | 0.3102819323539734 |
| Isaac V14 | custom/step_length | 1525 | 0.3497161269187927 |
| Isaac V14 | custom/step_length_reward | 1525 | 0.07732146978378296 |
| Isaac V14 | custom/swing_foot_clearance_reward | 1525 | 0.000828742457088083 |
| Isaac V14 | custom/swing_foot_high_penalty | 1525 | 0.0 |
| Isaac V14 | custom/torso_low_penalty | 1525 | 0.12903812527656555 |
| Isaac V14 | custom/total_reward | 1525 | 3.1173095703125 |
| Isaac V14 | custom/touchdown_reward | 1525 | 0.0036625880748033524 |
| Isaac V14 | custom/underused_foot_contact_reward | 1525 | 0.014683257788419724 |
| Isaac V14 | custom/vertical_velocity_penalty | 1525 | 0.13544049859046936 |
| Isaac V16 | Loss/entropy | 1525 | -26.30150604248047 |
| Isaac V16 | Loss/learning_rate | 1525 | 1.4999999621068127e-05 |
| Isaac V16 | Loss/surrogate | 1525 | 0.0021477655973285437 |
| Isaac V16 | Loss/value_function | 1525 | 98.8614273071289 |
| Isaac V16 | Perf/collection time | 1525 | 0.2995891571044922 |
| Isaac V16 | Perf/learning_time | 1525 | 0.05404400825500488 |
| Isaac V16 | Perf/total_fps | 1525 | 370643.0 |
| Isaac V16 | Policy/mean_noise_std | 1525 | 0.08982827514410019 |
| Isaac V16 | Train/mean_episode_length | 1525 | 829.6500244140625 |
| Isaac V16 | Train/mean_episode_length/time | 572 | 829.6500244140625 |
| Isaac V16 | Train/mean_reward | 1525 | 1818.1798095703125 |
| Isaac V16 | Train/mean_reward/time | 572 | 1818.1798095703125 |
| Isaac V16 | custom/action_rate_penalty | 1525 | 0.015415631234645844 |
| Isaac V16 | custom/arm_action_penalty | 1525 | 0.028084367513656616 |
| Isaac V16 | custom/arm_high_penalty | 1525 | 0.00648106262087822 |
| Isaac V16 | custom/arm_low_penalty | 1525 | 2.77097001344373e-06 |
| Isaac V16 | custom/arm_neutral_height_penalty | 1525 | 0.12012026458978653 |
| Isaac V16 | custom/arm_pose_penalty | 1525 | 0.7172633409500122 |
| Isaac V16 | custom/arm_velocity_penalty | 1525 | 0.04872266948223114 |
| Isaac V16 | custom/double_foot_contact_penalty | 1525 | 0.026181641966104507 |
| Isaac V16 | custom/foot_air_penalty | 1525 | 0.0 |
| Isaac V16 | custom/foot_air_time_penalty | 1525 | 0.033188119530677795 |
| Isaac V16 | custom/foot_contact_balance_penalty | 1525 | 0.10855177789926529 |
| Isaac V16 | custom/foot_contact_switch_reward | 1525 | 0.005410156212747097 |
| Isaac V16 | custom/foot_contact_transition_reward | 1525 | 0.045904599130153656 |
| Isaac V16 | custom/foot_dominance_time | 1525 | 0.23123779892921448 |
| Isaac V16 | custom/foot_height_difference | 1525 | 0.053856879472732544 |
| Isaac V16 | custom/foot_height_difference_penalty | 1525 | 0.001196238212287426 |
| Isaac V16 | custom/foot_height_difference_reward | 1525 | 0.0 |
| Isaac V16 | custom/foot_lateral_distance | 1525 | 0.31603866815567017 |
| Isaac V16 | custom/foot_lateral_distance_penalty | 1525 | 6.510395905934274e-05 |
| Isaac V16 | custom/foot_slip_penalty | 1525 | 0.40957945585250854 |
| Isaac V16 | custom/forward_velocity | 1525 | 0.7688556909561157 |
| Isaac V16 | custom/forward_velocity_reward | 1525 | 0.9244624376296997 |
| Isaac V16 | custom/forward_velocity_tracking_penalty | 1525 | 0.04930582642555237 |
| Isaac V16 | custom/gait_curriculum_scale | 1525 | 1.0 |
| Isaac V16 | custom/height_bonus | 1525 | 0.0 |
| Isaac V16 | custom/height_tracking_penalty | 1525 | 0.009992673061788082 |
| Isaac V16 | custom/high_forward_velocity_penalty | 1525 | 0.0010410334216430783 |
| Isaac V16 | custom/high_height_penalty | 1525 | 0.0 |
| Isaac V16 | custom/lateral_velocity | 1525 | 0.12034234404563904 |
| Isaac V16 | custom/lateral_velocity_penalty | 1525 | 0.03605308383703232 |
| Isaac V16 | custom/left_foot_contact | 1525 | 0.523747980594635 |
| Isaac V16 | custom/leg_action_symmetry_penalty | 1525 | 0.04532773420214653 |
| Isaac V16 | custom/leg_pose_penalty | 1525 | 0.1341814398765564 |
| Isaac V16 | custom/leg_pose_symmetry_penalty | 1525 | 0.011705085635185242 |
| Isaac V16 | custom/low_height_penalty | 1525 | 0.005514183547347784 |
| Isaac V16 | custom/low_speed_vertical_penalty | 1525 | 0.0016791007947176695 |
| Isaac V16 | custom/max_foot_air_time | 1525 | 0.15526530146598816 |
| Isaac V16 | custom/mean_foot_air_time | 1525 | 0.08359172195196152 |
| Isaac V16 | custom/no_foot_contact_penalty | 1525 | 0.24891355633735657 |
| Isaac V16 | custom/non_foot_low_penalty | 1525 | 0.20996196568012238 |
| Isaac V16 | custom/right_foot_contact | 1525 | 0.3865540325641632 |
| Isaac V16 | custom/root_height | 1525 | 1.1767139434814453 |
| Isaac V16 | custom/single_foot_contact_reward | 1525 | 0.03455565869808197 |
| Isaac V16 | custom/soft_foot_contact_switch_reward | 1525 | 0.0016450980911031365 |
| Isaac V16 | custom/soft_single_foot_contact_reward | 1525 | 0.018778057768940926 |
| Isaac V16 | custom/stance_duration_penalty | 1525 | 0.0357465036213398 |
| Isaac V16 | custom/stance_foot_slip_penalty | 1525 | 0.214274600148201 |
| Isaac V16 | custom/step_length | 1525 | 0.5049915313720703 |
| Isaac V16 | custom/step_length_reward | 1525 | 0.07479187846183777 |
| Isaac V16 | custom/swing_foot_clearance_reward | 1525 | 0.00540888961404562 |
| Isaac V16 | custom/swing_foot_high_penalty | 1525 | 0.0008079109829850495 |
| Isaac V16 | custom/torso_low_penalty | 1525 | 0.21712088584899902 |
| Isaac V16 | custom/total_reward | 1525 | 2.2751593589782715 |
| Isaac V16 | custom/touchdown_reward | 1525 | 0.005486366339027882 |
| Isaac V16 | custom/underused_foot_contact_reward | 1525 | 0.04398595169186592 |
| Isaac V16 | custom/vertical_velocity_penalty | 1525 | 0.1166941300034523 |
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
