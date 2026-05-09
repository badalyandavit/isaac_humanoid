from __future__ import annotations

import torch

from isaaclab.utils import configclass
from isaaclab_tasks.direct.humanoid.humanoid_env import HumanoidEnv, HumanoidEnvCfg


@configclass
class HumanoidV4EnvCfg(HumanoidEnvCfg):
    height_target: float = 1.35
    height_bonus_scale: float = 4.0
    height_tracking_penalty_scale: float = 0.0
    low_height_threshold: float = 1.15
    low_height_penalty_scale: float = 6.0
    high_height_threshold: float = 1.60
    high_height_penalty_scale: float = 0.0
    torso_low_height: float = 1.10
    torso_low_penalty_scale: float = 4.0
    arm_low_height: float = 0.65
    arm_low_penalty_scale: float = 4.0
    leg_pose_penalty_scale: float = 0.6
    arm_pose_penalty_scale: float = 0.8
    action_rate_penalty_scale: float = 0.04
    vertical_velocity_penalty_scale: float = 0.0
    arm_action_penalty_scale: float = 0.0
    arm_velocity_penalty_scale: float = 0.0
    leg_action_symmetry_penalty_scale: float = 0.0
    leg_pose_symmetry_penalty_scale: float = 0.0
    non_foot_low_height: float = 0.55
    non_foot_low_penalty_scale: float = 0.0
    foot_air_height: float = 0.20
    foot_air_penalty_scale: float = 0.0
    foot_slip_height: float = 0.16
    foot_slip_penalty_scale: float = 0.0


class HumanoidV4Env(HumanoidEnv):
    cfg: HumanoidV4EnvCfg

    def __init__(self, cfg: HumanoidV4EnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)
        self._previous_actions_for_rate = torch.zeros((self.num_envs, self.cfg.action_space), device=self.device)
        self._arm_body_mask: torch.Tensor | None = None
        self._torso_body_mask: torch.Tensor | None = None
        self._foot_body_mask: torch.Tensor | None = None
        self._non_foot_body_mask: torch.Tensor | None = None
        self._arm_joint_mask: torch.Tensor | None = None
        self._leg_joint_mask: torch.Tensor | None = None
        self._left_leg_joint_mask: torch.Tensor | None = None
        self._right_leg_joint_mask: torch.Tensor | None = None
        self._leg_joint_pairs: tuple[torch.Tensor, torch.Tensor] | None = None

    def _reset_idx(self, env_ids):
        super()._reset_idx(env_ids)
        if env_ids is None:
            self._previous_actions_for_rate.zero_()
        else:
            self._previous_actions_for_rate[env_ids] = 0.0

    def _get_rewards(self) -> torch.Tensor:
        base_reward = super()._get_rewards()
        robot = self._robot_ref()
        data = robot.data

        root_height = self._relative_root_height(data.root_pos_w[:, 2])
        height_progress = torch.clamp(
            (root_height - self.cfg.low_height_threshold)
            / max(1.0e-6, self.cfg.height_target - self.cfg.low_height_threshold),
            min=0.0,
            max=1.0,
        )
        height_bonus = self.cfg.height_bonus_scale * height_progress
        height_tracking_penalty = self.cfg.height_tracking_penalty_scale * (
            (root_height - self.cfg.height_target) / max(1.0e-6, self.cfg.height_target)
        ).square()
        low_height_penalty = self.cfg.low_height_penalty_scale * torch.clamp(
            (self.cfg.low_height_threshold - root_height) / 0.25,
            min=0.0,
            max=1.5,
        )
        high_height_penalty = self.cfg.high_height_penalty_scale * torch.clamp(
            (root_height - self.cfg.high_height_threshold) / 0.25,
            min=0.0,
            max=1.5,
        )
        vertical_velocity_penalty = self.cfg.vertical_velocity_penalty_scale * self._root_vertical_velocity(data).square()

        body_pos = data.body_pos_w
        body_heights = self._relative_body_heights(body_pos[..., 2])
        self._build_masks(data)
        torso_low_penalty = self._low_body_penalty(
            body_heights, self._torso_body_mask, self.cfg.torso_low_height, self.cfg.torso_low_penalty_scale
        )
        arm_low_penalty = self._low_body_penalty(
            body_heights, self._arm_body_mask, self.cfg.arm_low_height, self.cfg.arm_low_penalty_scale
        )
        non_foot_low_penalty = self._low_body_penalty(
            body_heights, self._non_foot_body_mask, self.cfg.non_foot_low_height, self.cfg.non_foot_low_penalty_scale
        )
        foot_air_penalty = self._foot_air_penalty(body_heights)
        foot_slip_penalty = self._foot_slip_penalty(data, body_heights)

        leg_pose_penalty = self._masked_square_penalty(
            self.dof_pos_scaled, self._leg_joint_mask, self.cfg.leg_pose_penalty_scale
        )
        arm_pose_penalty = self._masked_square_penalty(
            self.dof_pos_scaled, self._arm_joint_mask, self.cfg.arm_pose_penalty_scale
        )
        arm_velocity_penalty = self._masked_square_penalty(
            data.joint_vel, self._arm_joint_mask, self.cfg.arm_velocity_penalty_scale
        )
        leg_pose_symmetry_penalty = self._paired_square_penalty(
            self.dof_pos_scaled, self._leg_joint_pairs, self.cfg.leg_pose_symmetry_penalty_scale
        )

        action_rate_penalty = torch.zeros_like(base_reward)
        arm_action_penalty = torch.zeros_like(base_reward)
        leg_action_symmetry_penalty = torch.zeros_like(base_reward)
        actions = getattr(self, "actions", None)
        if actions is not None and actions.shape == self._previous_actions_for_rate.shape:
            action_delta = actions - self._previous_actions_for_rate
            action_rate_penalty = self.cfg.action_rate_penalty_scale * torch.mean(action_delta.square(), dim=-1)
            arm_action_penalty = self._masked_square_penalty(
                actions, self._arm_joint_mask, self.cfg.arm_action_penalty_scale
            )
            leg_action_symmetry_penalty = self._paired_square_penalty(
                actions, self._leg_joint_pairs, self.cfg.leg_action_symmetry_penalty_scale
            )
            self._previous_actions_for_rate[:] = actions.detach()

        total_reward = (
            base_reward
            + height_bonus
            - height_tracking_penalty
            - low_height_penalty
            - high_height_penalty
            - torso_low_penalty
            - arm_low_penalty
            - non_foot_low_penalty
            - foot_air_penalty
            - foot_slip_penalty
            - leg_pose_penalty
            - arm_pose_penalty
            - arm_velocity_penalty
            - leg_pose_symmetry_penalty
            - action_rate_penalty
            - arm_action_penalty
            - leg_action_symmetry_penalty
            - vertical_velocity_penalty
        )
        self._log_reward_terms(
            root_height=root_height,
            height_bonus=height_bonus,
            height_tracking_penalty=height_tracking_penalty,
            low_height_penalty=low_height_penalty,
            high_height_penalty=high_height_penalty,
            torso_low_penalty=torso_low_penalty,
            arm_low_penalty=arm_low_penalty,
            non_foot_low_penalty=non_foot_low_penalty,
            foot_air_penalty=foot_air_penalty,
            foot_slip_penalty=foot_slip_penalty,
            leg_pose_penalty=leg_pose_penalty,
            arm_pose_penalty=arm_pose_penalty,
            arm_velocity_penalty=arm_velocity_penalty,
            leg_pose_symmetry_penalty=leg_pose_symmetry_penalty,
            action_rate_penalty=action_rate_penalty,
            arm_action_penalty=arm_action_penalty,
            leg_action_symmetry_penalty=leg_action_symmetry_penalty,
            vertical_velocity_penalty=vertical_velocity_penalty,
            total_reward=total_reward,
        )
        return total_reward

    def _robot_ref(self):
        robot = getattr(self, "robot", None) or getattr(self, "_robot", None)
        if robot is None:
            robot = self.scene["robot"]
        return robot

    def _relative_root_height(self, root_z: torch.Tensor) -> torch.Tensor:
        env_origins = getattr(self.scene, "env_origins", None)
        if env_origins is not None:
            return root_z - env_origins[:, 2]
        return root_z

    def _relative_body_heights(self, body_z: torch.Tensor) -> torch.Tensor:
        env_origins = getattr(self.scene, "env_origins", None)
        if env_origins is not None:
            return body_z - env_origins[:, 2].unsqueeze(-1)
        return body_z

    def _root_vertical_velocity(self, data) -> torch.Tensor:
        for attr in ("root_lin_vel_w", "root_link_lin_vel_w", "root_com_lin_vel_w"):
            value = getattr(data, attr, None)
            if value is not None:
                return value[:, 2]
        state = getattr(data, "root_state_w", None)
        if state is not None and state.shape[-1] >= 10:
            return state[:, 9]
        return torch.zeros(self.num_envs, device=self.device)

    def _build_masks(self, data) -> None:
        if self._arm_body_mask is None:
            body_names = [name.lower() for name in data.body_names]
            arm_body = ["arm" in name or "hand" in name for name in body_names]
            foot_body = ["foot" in name or "ankle" in name or "toe" in name for name in body_names]
            torso_body = [
                any(token in name for token in ("torso", "waist", "pelvis", "abdomen", "head"))
                for name in body_names
            ]
            self._arm_body_mask = torch.tensor(arm_body, dtype=torch.bool, device=self.device)
            self._foot_body_mask = torch.tensor(foot_body, dtype=torch.bool, device=self.device)
            self._torso_body_mask = torch.tensor(torso_body, dtype=torch.bool, device=self.device)
            self._non_foot_body_mask = ~self._foot_body_mask

        if self._arm_joint_mask is None:
            joint_names = [name.lower() for name in data.joint_names]
            arm_joint = ["arm" in name or "shoulder" in name or "elbow" in name for name in joint_names]
            leg_joint = [
                any(token in name for token in ("thigh", "knee", "shin", "ankle", "foot", "hip"))
                for name in joint_names
            ]
            left_leg_joint = [is_leg and "left" in name for is_leg, name in zip(leg_joint, joint_names, strict=False)]
            right_leg_joint = [is_leg and "right" in name for is_leg, name in zip(leg_joint, joint_names, strict=False)]
            self._arm_joint_mask = torch.tensor(arm_joint, dtype=torch.bool, device=self.device)
            self._leg_joint_mask = torch.tensor(leg_joint, dtype=torch.bool, device=self.device)
            self._left_leg_joint_mask = torch.tensor(left_leg_joint, dtype=torch.bool, device=self.device)
            self._right_leg_joint_mask = torch.tensor(right_leg_joint, dtype=torch.bool, device=self.device)
            self._leg_joint_pairs = self._paired_joint_indices(joint_names, self._leg_joint_mask)

    def _low_body_penalty(
        self,
        body_heights: torch.Tensor,
        mask: torch.Tensor | None,
        threshold: float,
        scale: float,
    ) -> torch.Tensor:
        if mask is None or not torch.any(mask):
            return torch.zeros(self.num_envs, device=self.device)
        selected_heights = body_heights[:, mask]
        low_fraction = torch.clamp((threshold - selected_heights) / max(1.0e-6, threshold), min=0.0, max=1.0)
        return scale * torch.mean(low_fraction, dim=-1)

    def _masked_square_penalty(
        self,
        values: torch.Tensor,
        mask: torch.Tensor | None,
        scale: float,
    ) -> torch.Tensor:
        if mask is None or not torch.any(mask):
            return torch.zeros(self.num_envs, device=self.device)
        return scale * torch.mean(values[:, mask].square(), dim=-1)

    def _paired_square_penalty(
        self,
        values: torch.Tensor,
        pairs: tuple[torch.Tensor, torch.Tensor] | None,
        scale: float,
    ) -> torch.Tensor:
        if pairs is None or pairs[0].numel() == 0:
            return torch.zeros(self.num_envs, device=self.device)
        left_idx, right_idx = pairs
        return scale * torch.mean((values[:, left_idx].abs() - values[:, right_idx].abs()).square(), dim=-1)

    def _foot_air_penalty(self, body_heights: torch.Tensor) -> torch.Tensor:
        if self._foot_body_mask is None or not torch.any(self._foot_body_mask):
            return torch.zeros(self.num_envs, device=self.device)
        foot_heights = body_heights[:, self._foot_body_mask]
        both_feet_high = torch.amin(foot_heights, dim=-1) > self.cfg.foot_air_height
        return self.cfg.foot_air_penalty_scale * both_feet_high.float()

    def _foot_slip_penalty(self, data, body_heights: torch.Tensor) -> torch.Tensor:
        if self._foot_body_mask is None or not torch.any(self._foot_body_mask):
            return torch.zeros(self.num_envs, device=self.device)
        body_vel = getattr(data, "body_lin_vel_w", None)
        if body_vel is None:
            body_state = getattr(data, "body_state_w", None)
            if body_state is not None and body_state.shape[-1] >= 10:
                body_vel = body_state[..., 7:10]
        if body_vel is None:
            return torch.zeros(self.num_envs, device=self.device)
        foot_heights = body_heights[:, self._foot_body_mask]
        foot_xy_vel = body_vel[:, self._foot_body_mask, :2]
        near_ground = (foot_heights < self.cfg.foot_slip_height).float()
        slip = torch.linalg.norm(foot_xy_vel, dim=-1).square() * near_ground
        return self.cfg.foot_slip_penalty_scale * torch.mean(slip, dim=-1)

    def _paired_joint_indices(
        self,
        joint_names: list[str],
        leg_mask: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        left_indices: list[int] = []
        right_indices: list[int] = []
        leg_flags = [bool(value) for value in leg_mask.detach().cpu().tolist()]
        normalized_to_index = {self._normalize_joint_side(name): idx for idx, name in enumerate(joint_names)}
        for idx, name in enumerate(joint_names):
            if not leg_flags[idx] or "left" not in name:
                continue
            mate = normalized_to_index.get(self._normalize_joint_side(name).replace("left", "right", 1))
            if mate is not None and leg_flags[mate]:
                left_indices.append(idx)
                right_indices.append(mate)
        return (
            torch.tensor(left_indices, dtype=torch.long, device=self.device),
            torch.tensor(right_indices, dtype=torch.long, device=self.device),
        )

    @staticmethod
    def _normalize_joint_side(name: str) -> str:
        return name.lower().replace("left_", "left").replace("right_", "right")

    def _log_reward_terms(self, **terms: torch.Tensor) -> None:
        log = self.extras.setdefault("log", {})
        for name, value in terms.items():
            log[f"custom/{name}"] = torch.mean(value.detach())
