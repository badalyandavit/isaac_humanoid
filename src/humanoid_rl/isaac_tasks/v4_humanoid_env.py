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
    target_forward_velocity: float = 0.0
    forward_velocity_reward_scale: float = 0.0
    forward_velocity_sigma: float = 0.6
    lateral_velocity_penalty_scale: float = 0.0
    low_speed_threshold: float = 0.5
    low_speed_vertical_penalty_scale: float = 0.0
    arm_high_height: float = 1.55
    arm_high_penalty_scale: float = 0.0
    foot_contact_height: float = 0.14
    foot_contact_force_threshold: float = 1.0
    single_foot_contact_reward_scale: float = 0.0
    foot_contact_switch_reward_scale: float = 0.0
    no_foot_contact_penalty_scale: float = 0.0
    double_foot_contact_penalty_scale: float = 0.0
    foot_contact_balance_penalty_scale: float = 0.0
    foot_contact_ema_decay: float = 0.98


class HumanoidV4Env(HumanoidEnv):
    cfg: HumanoidV4EnvCfg

    def __init__(self, cfg: HumanoidV4EnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)
        self._previous_actions_for_rate = torch.zeros((self.num_envs, self.cfg.action_space), device=self.device)
        self._arm_body_mask: torch.Tensor | None = None
        self._torso_body_mask: torch.Tensor | None = None
        self._foot_body_mask: torch.Tensor | None = None
        self._left_foot_body_mask: torch.Tensor | None = None
        self._right_foot_body_mask: torch.Tensor | None = None
        self._non_foot_body_mask: torch.Tensor | None = None
        self._arm_joint_mask: torch.Tensor | None = None
        self._leg_joint_mask: torch.Tensor | None = None
        self._left_leg_joint_mask: torch.Tensor | None = None
        self._right_leg_joint_mask: torch.Tensor | None = None
        self._leg_joint_pairs: tuple[torch.Tensor, torch.Tensor] | None = None
        self._previous_root_xy = torch.zeros((self.num_envs, 2), device=self.device)
        self._foot_contact_ema = torch.zeros((self.num_envs, 2), device=self.device)
        self._previous_foot_contact_side = torch.full((self.num_envs,), -1, dtype=torch.long, device=self.device)

    def _reset_idx(self, env_ids):
        super()._reset_idx(env_ids)
        if env_ids is None:
            self._previous_actions_for_rate.zero_()
            self._foot_contact_ema.zero_()
            self._previous_foot_contact_side.fill_(-1)
        else:
            self._previous_actions_for_rate[env_ids] = 0.0
            self._foot_contact_ema[env_ids] = 0.0
            self._previous_foot_contact_side[env_ids] = -1
        self._cache_current_root_xy(env_ids)

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
        root_xy_velocity = self._root_xy_velocity(data)
        forward_velocity = root_xy_velocity[:, 0]
        lateral_velocity = root_xy_velocity[:, 1]
        vertical_velocity = self._root_vertical_velocity(data)
        vertical_velocity_penalty = self.cfg.vertical_velocity_penalty_scale * vertical_velocity.square()
        forward_velocity_reward = self._forward_velocity_reward(forward_velocity)
        lateral_velocity_penalty = self.cfg.lateral_velocity_penalty_scale * lateral_velocity.square()
        low_speed_vertical_penalty = self._low_speed_vertical_penalty(forward_velocity, vertical_velocity)

        body_pos = data.body_pos_w
        body_heights = self._relative_body_heights(body_pos[..., 2])
        self._build_masks(data)
        torso_low_penalty = self._low_body_penalty(
            body_heights, self._torso_body_mask, self.cfg.torso_low_height, self.cfg.torso_low_penalty_scale
        )
        arm_low_penalty = self._low_body_penalty(
            body_heights, self._arm_body_mask, self.cfg.arm_low_height, self.cfg.arm_low_penalty_scale
        )
        arm_high_penalty = self._high_body_penalty(
            body_heights, self._arm_body_mask, self.cfg.arm_high_height, self.cfg.arm_high_penalty_scale
        )
        non_foot_low_penalty = self._low_body_penalty(
            body_heights, self._non_foot_body_mask, self.cfg.non_foot_low_height, self.cfg.non_foot_low_penalty_scale
        )
        foot_air_penalty = self._foot_air_penalty(body_heights)
        foot_slip_penalty = self._foot_slip_penalty(data, body_heights)
        foot_contact_terms = self._foot_contact_terms(data, body_heights)

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
            + forward_velocity_reward
            + foot_contact_terms["single_foot_contact_reward"]
            + foot_contact_terms["foot_contact_switch_reward"]
            - height_tracking_penalty
            - low_height_penalty
            - high_height_penalty
            - torso_low_penalty
            - arm_low_penalty
            - arm_high_penalty
            - non_foot_low_penalty
            - foot_air_penalty
            - foot_slip_penalty
            - foot_contact_terms["no_foot_contact_penalty"]
            - foot_contact_terms["double_foot_contact_penalty"]
            - foot_contact_terms["foot_contact_balance_penalty"]
            - leg_pose_penalty
            - arm_pose_penalty
            - arm_velocity_penalty
            - leg_pose_symmetry_penalty
            - action_rate_penalty
            - arm_action_penalty
            - leg_action_symmetry_penalty
            - vertical_velocity_penalty
            - lateral_velocity_penalty
            - low_speed_vertical_penalty
        )
        self._log_reward_terms(
            root_height=root_height,
            forward_velocity=forward_velocity,
            lateral_velocity=lateral_velocity,
            height_bonus=height_bonus,
            forward_velocity_reward=forward_velocity_reward,
            height_tracking_penalty=height_tracking_penalty,
            low_height_penalty=low_height_penalty,
            high_height_penalty=high_height_penalty,
            torso_low_penalty=torso_low_penalty,
            arm_low_penalty=arm_low_penalty,
            arm_high_penalty=arm_high_penalty,
            non_foot_low_penalty=non_foot_low_penalty,
            foot_air_penalty=foot_air_penalty,
            foot_slip_penalty=foot_slip_penalty,
            single_foot_contact_reward=foot_contact_terms["single_foot_contact_reward"],
            foot_contact_switch_reward=foot_contact_terms["foot_contact_switch_reward"],
            no_foot_contact_penalty=foot_contact_terms["no_foot_contact_penalty"],
            double_foot_contact_penalty=foot_contact_terms["double_foot_contact_penalty"],
            foot_contact_balance_penalty=foot_contact_terms["foot_contact_balance_penalty"],
            left_foot_contact=foot_contact_terms["left_foot_contact"],
            right_foot_contact=foot_contact_terms["right_foot_contact"],
            leg_pose_penalty=leg_pose_penalty,
            arm_pose_penalty=arm_pose_penalty,
            arm_velocity_penalty=arm_velocity_penalty,
            leg_pose_symmetry_penalty=leg_pose_symmetry_penalty,
            action_rate_penalty=action_rate_penalty,
            arm_action_penalty=arm_action_penalty,
            leg_action_symmetry_penalty=leg_action_symmetry_penalty,
            vertical_velocity_penalty=vertical_velocity_penalty,
            lateral_velocity_penalty=lateral_velocity_penalty,
            low_speed_vertical_penalty=low_speed_vertical_penalty,
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

    def _relative_root_xy(self, root_xy: torch.Tensor) -> torch.Tensor:
        env_origins = getattr(self.scene, "env_origins", None)
        if env_origins is not None:
            return root_xy - env_origins[:, :2]
        return root_xy

    def _cache_current_root_xy(self, env_ids=None) -> None:
        try:
            root_xy = self._relative_root_xy(self._robot_ref().data.root_pos_w[:, :2])
        except Exception:
            return
        if env_ids is None:
            self._previous_root_xy[:] = root_xy.detach()
        else:
            self._previous_root_xy[env_ids] = root_xy[env_ids].detach()

    def _root_xy_velocity(self, data) -> torch.Tensor:
        for attr in ("root_lin_vel_w", "root_link_lin_vel_w", "root_com_lin_vel_w"):
            value = getattr(data, attr, None)
            if value is not None:
                return value[:, :2]
        state = getattr(data, "root_state_w", None)
        if state is not None and state.shape[-1] >= 9:
            return state[:, 7:9]
        root_xy = self._relative_root_xy(data.root_pos_w[:, :2])
        velocity = (root_xy - self._previous_root_xy) / max(1.0e-6, self._control_dt())
        self._previous_root_xy[:] = root_xy.detach()
        return velocity

    def _root_vertical_velocity(self, data) -> torch.Tensor:
        for attr in ("root_lin_vel_w", "root_link_lin_vel_w", "root_com_lin_vel_w"):
            value = getattr(data, attr, None)
            if value is not None:
                return value[:, 2]
        state = getattr(data, "root_state_w", None)
        if state is not None and state.shape[-1] >= 10:
            return state[:, 9]
        return torch.zeros(self.num_envs, device=self.device)

    def _control_dt(self) -> float:
        for attr in ("step_dt", "physics_dt", "dt"):
            value = getattr(self, attr, None)
            if value is not None:
                return float(value)
        sim_cfg = getattr(self.cfg, "sim", None)
        sim_dt = getattr(sim_cfg, "dt", None)
        decimation = getattr(self.cfg, "decimation", 1)
        if sim_dt is not None:
            return float(sim_dt) * float(decimation)
        return 1.0 / 60.0

    def _build_masks(self, data) -> None:
        if self._arm_body_mask is None:
            body_names = [name.lower() for name in data.body_names]
            arm_body = ["arm" in name or "hand" in name for name in body_names]
            foot_body = ["foot" in name or "ankle" in name or "toe" in name for name in body_names]
            left_foot_body = [is_foot and "left" in name for is_foot, name in zip(foot_body, body_names, strict=False)]
            right_foot_body = [is_foot and "right" in name for is_foot, name in zip(foot_body, body_names, strict=False)]
            torso_body = [
                any(token in name for token in ("torso", "waist", "pelvis", "abdomen", "head"))
                for name in body_names
            ]
            self._arm_body_mask = torch.tensor(arm_body, dtype=torch.bool, device=self.device)
            self._foot_body_mask = torch.tensor(foot_body, dtype=torch.bool, device=self.device)
            self._left_foot_body_mask = torch.tensor(left_foot_body, dtype=torch.bool, device=self.device)
            self._right_foot_body_mask = torch.tensor(right_foot_body, dtype=torch.bool, device=self.device)
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

    def _high_body_penalty(
        self,
        body_heights: torch.Tensor,
        mask: torch.Tensor | None,
        threshold: float,
        scale: float,
    ) -> torch.Tensor:
        if mask is None or not torch.any(mask):
            return torch.zeros(self.num_envs, device=self.device)
        selected_heights = body_heights[:, mask]
        high_fraction = torch.clamp((selected_heights - threshold) / max(1.0e-6, threshold), min=0.0, max=1.0)
        return scale * torch.mean(high_fraction, dim=-1)

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

    def _forward_velocity_reward(self, forward_velocity: torch.Tensor) -> torch.Tensor:
        if self.cfg.forward_velocity_reward_scale == 0.0:
            return torch.zeros(self.num_envs, device=self.device)
        normalized_error = (forward_velocity - self.cfg.target_forward_velocity) / max(
            1.0e-6, self.cfg.forward_velocity_sigma
        )
        return self.cfg.forward_velocity_reward_scale * torch.exp(-normalized_error.square())

    def _low_speed_vertical_penalty(
        self,
        forward_velocity: torch.Tensor,
        vertical_velocity: torch.Tensor,
    ) -> torch.Tensor:
        if self.cfg.low_speed_vertical_penalty_scale == 0.0:
            return torch.zeros(self.num_envs, device=self.device)
        speed_deficit = torch.clamp(
            (self.cfg.low_speed_threshold - torch.clamp(forward_velocity, min=0.0))
            / max(1.0e-6, self.cfg.low_speed_threshold),
            min=0.0,
            max=1.0,
        )
        return self.cfg.low_speed_vertical_penalty_scale * speed_deficit * vertical_velocity.square()

    def _foot_contact_terms(self, data, body_heights: torch.Tensor) -> dict[str, torch.Tensor]:
        zeros = torch.zeros(self.num_envs, device=self.device)
        terms = {
            "single_foot_contact_reward": zeros,
            "foot_contact_switch_reward": zeros,
            "no_foot_contact_penalty": zeros,
            "double_foot_contact_penalty": zeros,
            "foot_contact_balance_penalty": zeros,
            "left_foot_contact": zeros,
            "right_foot_contact": zeros,
        }
        if self._foot_body_mask is None or not torch.any(self._foot_body_mask):
            return terms

        foot_contacts = self._foot_contact_values(data, body_heights)
        left_mask = self._side_mask_with_fallback(self._left_foot_body_mask, prefer_left=True)
        right_mask = self._side_mask_with_fallback(self._right_foot_body_mask, prefer_left=False)
        left_contact = self._masked_max(foot_contacts, left_mask)
        right_contact = self._masked_max(foot_contacts, right_mask)
        contact_pair = torch.stack((left_contact, right_contact), dim=-1)
        contact_binary = (contact_pair > 0.5).float()
        contact_count = torch.sum(contact_binary, dim=-1)

        single_contact = (contact_count == 1.0).float()
        no_contact = (contact_count < 0.5).float()
        double_contact = (contact_count > 1.5).float()
        single_foot_contact_reward = self.cfg.single_foot_contact_reward_scale * single_contact
        no_foot_contact_penalty = self.cfg.no_foot_contact_penalty_scale * no_contact
        double_foot_contact_penalty = self.cfg.double_foot_contact_penalty_scale * double_contact

        decay = min(0.999, max(0.0, float(self.cfg.foot_contact_ema_decay)))
        self._foot_contact_ema.mul_(decay).add_(contact_pair.detach(), alpha=1.0 - decay)
        foot_contact_balance_penalty = self.cfg.foot_contact_balance_penalty_scale * (
            self._foot_contact_ema[:, 0] - self._foot_contact_ema[:, 1]
        ).square()

        current_side = torch.where(
            right_contact > left_contact,
            torch.ones(self.num_envs, dtype=torch.long, device=self.device),
            torch.zeros(self.num_envs, dtype=torch.long, device=self.device),
        )
        current_side = torch.where(contact_count == 1.0, current_side, -torch.ones_like(current_side))
        switched = (
            (self._previous_foot_contact_side >= 0)
            & (current_side >= 0)
            & (self._previous_foot_contact_side != current_side)
        ).float()
        foot_contact_switch_reward = self.cfg.foot_contact_switch_reward_scale * switched
        valid_side = current_side >= 0
        self._previous_foot_contact_side[valid_side] = current_side[valid_side].detach()

        return {
            "single_foot_contact_reward": single_foot_contact_reward,
            "foot_contact_switch_reward": foot_contact_switch_reward,
            "no_foot_contact_penalty": no_foot_contact_penalty,
            "double_foot_contact_penalty": double_foot_contact_penalty,
            "foot_contact_balance_penalty": foot_contact_balance_penalty,
            "left_foot_contact": left_contact,
            "right_foot_contact": right_contact,
        }

    def _foot_contact_values(self, data, body_heights: torch.Tensor) -> torch.Tensor:
        foot_heights = body_heights[:, self._foot_body_mask]
        force_norm = self._body_contact_force_norm(data, body_heights.shape[1])
        if force_norm is not None:
            if force_norm.shape[1] == body_heights.shape[1]:
                force_norm = force_norm[:, self._foot_body_mask]
            if force_norm.shape[1] == foot_heights.shape[1]:
                return torch.clamp(force_norm / max(1.0e-6, self.cfg.foot_contact_force_threshold), 0.0, 1.0)
        return torch.clamp(
            (self.cfg.foot_contact_height - foot_heights) / max(1.0e-6, self.cfg.foot_contact_height),
            min=0.0,
            max=1.0,
        )

    def _body_contact_force_norm(self, data, body_count: int) -> torch.Tensor | None:
        for source in (data, getattr(getattr(self, "_contact_sensor", None), "data", None)):
            if source is None:
                continue
            for attr in (
                "body_net_contact_forces_w",
                "net_contact_forces_w",
                "net_forces_w",
                "contact_forces_w",
                "contact_forces",
            ):
                value = getattr(source, attr, None)
                if value is None or not torch.is_tensor(value) or value.ndim < 3:
                    continue
                if value.shape[0] != self.num_envs:
                    continue
                force = value
                while force.ndim > 3:
                    force = torch.sum(force, dim=-2)
                if force.shape[-1] < 3:
                    continue
                if force.shape[1] == body_count or force.shape[1] == int(torch.sum(self._foot_body_mask).item()):
                    return torch.linalg.norm(force[..., :3], dim=-1)
        return None

    def _side_mask_with_fallback(self, side_mask: torch.Tensor | None, prefer_left: bool) -> torch.Tensor:
        foot_count = int(torch.sum(self._foot_body_mask).item()) if self._foot_body_mask is not None else 0
        if side_mask is not None and self._foot_body_mask is not None:
            selected = side_mask[self._foot_body_mask]
            if torch.any(selected):
                return selected
        fallback = torch.zeros(foot_count, dtype=torch.bool, device=self.device)
        if foot_count == 0:
            return fallback
        if foot_count == 1:
            fallback[0] = True
            return fallback
        midpoint = max(1, foot_count // 2)
        if prefer_left:
            fallback[:midpoint] = True
        else:
            fallback[midpoint:] = True
        return fallback

    def _masked_max(self, values: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        if values.shape[1] == 0 or not torch.any(mask):
            return torch.zeros(self.num_envs, device=self.device)
        return torch.amax(values[:, mask], dim=-1)

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
