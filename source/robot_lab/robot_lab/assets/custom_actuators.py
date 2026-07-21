# Copyright (c) 2024-2026 Ziqi Fan
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import math

import torch

from isaaclab.actuators import DCMotor, DCMotorCfg
from isaaclab.utils import configclass


class QuadraticTorqueCurveDCMotor(DCMotor):
    """DC motor with a quadratic torque-speed envelope fitted from measured data."""

    cfg: "QuadraticTorqueCurveDCMotorCfg"

    def _clip_effort(self, effort: torch.Tensor) -> torch.Tensor:
        # Convert joint angular speed from rad/s to rpm and use symmetric envelope over |speed|.
        vel_rpm = torch.abs(self._joint_vel) * (60.0 / (2.0 * math.pi))

        # Quadratic fit in rpm: T(n) = a*n^2 + b*n + c.
        torque_quadratic = (
            self.cfg.torque_curve_a * vel_rpm.square()
            + self.cfg.torque_curve_b * vel_rpm
            + self.cfg.torque_curve_c
        )

        # Before the curve's maximum point, use a horizontal line through the maximum.
        if self.cfg.torque_curve_a < 0.0:
            n_peak = -self.cfg.torque_curve_b / (2.0 * self.cfg.torque_curve_a)
            t_peak = (
                self.cfg.torque_curve_a * n_peak * n_peak
                + self.cfg.torque_curve_b * n_peak
                + self.cfg.torque_curve_c
            )
            torque_envelope = torch.where(vel_rpm <= n_peak, torch.full_like(vel_rpm, t_peak), torque_quadratic)
        else:
            torque_envelope = torque_quadratic

        # Keep envelope physically valid and respect continuous torque limit.
        sat_effort = torch.as_tensor(self._saturation_effort, device=effort.device, dtype=effort.dtype)
        torque_envelope = torch.clamp(torque_envelope, min=0.0)
        torque_envelope = torch.minimum(torque_envelope, sat_effort)
        max_effort = torch.minimum(torque_envelope, self.effort_limit)

        return torch.clip(effort, min=-max_effort, max=max_effort)


@configclass
class QuadraticTorqueCurveDCMotorCfg(DCMotorCfg):
    """Configuration for DCMotor with a quadratic torque-speed envelope."""

    class_type: type = QuadraticTorqueCurveDCMotor

    # Torque-speed fit from measured curve (rpm, N*m): T(n)=a*n^2+b*n+c.
    torque_curve_a: float = -0.000341191
    torque_curve_b: float = 0.064565966
    torque_curve_c: float = 13.605312408 #不超过测试值，如果要紧贴测试值则设置为14.0886978
