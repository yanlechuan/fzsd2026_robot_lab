# Copyright (c) 2024-2026 Ziqi Fan
# SPDX-License-Identifier: Apache-2.0

"""Script to visualize robot initial pose with fixed base."""

"""Launch Isaac Sim Simulator first."""

import argparse
from typing import Any

from isaaclab.app import AppLauncher

# add argparse arguments
parser = argparse.ArgumentParser(description="View initial robot pose with fixed base.")
parser.add_argument(
    "--disable_fabric",
    action="store_true",
    default=False,
    help="Disable fabric and use USD I/O operations.",
)
parser.add_argument("--num_envs", type=int, default=1, help="Number of environments to simulate.")
parser.add_argument("--task", type=str, required=True, help="Name of the task.")
parser.add_argument(
    "--disable_gravity",
    action="store_true",
    default=False,
    help="Disable gravity on the robot rigid bodies.",
)
parser.add_argument(
    "--strict_freeze",
    action="store_true",
    default=True,
    help="Force-write root and joint states to init_state every step.",
)
# append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)
# parse the arguments
args_cli = parser.parse_args()

# launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""Rest everything follows."""

import gymnasium as gym
import robot_lab.tasks  # noqa: F401
import torch

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg


def _set_if_exists(obj, attr_name: str, value):
    """Set a config field only if it exists."""
    if hasattr(obj, attr_name):
        setattr(obj, attr_name, value)


def main():
    """Zero-action loop with fixed-base robot for inspecting init pose."""
    env_cfg = parse_env_cfg(
        args_cli.task,
        device=args_cli.device,
        num_envs=args_cli.num_envs,
        use_fabric=not args_cli.disable_fabric,
    )

    # Force a simple single-scene setup for inspection.
    _set_if_exists(env_cfg.scene, "num_envs", args_cli.num_envs)

    # Disable common disturbances if these fields exist in the task config.
    if hasattr(env_cfg, "events") and env_cfg.events is not None:
        _set_if_exists(env_cfg.events, "randomize_apply_external_force_torque", None)
        _set_if_exists(env_cfg.events, "push_robot", None)

    # Fix robot base in runtime config and optionally disable gravity.
    robot_cfg = getattr(env_cfg.scene, "robot", None)
    if robot_cfg is None or getattr(robot_cfg, "spawn", None) is None:
        raise RuntimeError("Task has no scene.robot.spawn configuration to modify.")

    _set_if_exists(robot_cfg.spawn, "fix_base", True)
    if hasattr(robot_cfg.spawn, "rigid_props") and robot_cfg.spawn.rigid_props is not None:
        _set_if_exists(robot_cfg.spawn.rigid_props, "disable_gravity", args_cli.disable_gravity)

    env = gym.make(args_cli.task, cfg=env_cfg)

    print("[INFO] Running init-pose viewer with fixed base.")
    print(f"[INFO] Task: {args_cli.task}")
    print(f"[INFO] Num envs: {env_cfg.scene.num_envs}")
    print(f"[INFO] fix_base: {getattr(robot_cfg.spawn, 'fix_base', 'unknown')}")
    if hasattr(robot_cfg.spawn, "rigid_props") and robot_cfg.spawn.rigid_props is not None:
        print(f"[INFO] disable_gravity: {getattr(robot_cfg.spawn.rigid_props, 'disable_gravity', 'unknown')}")

    env.reset()
    unwrapped_env: Any = env.unwrapped
    robot = unwrapped_env.scene["robot"]
    env_ids = torch.arange(env_cfg.scene.num_envs, device=unwrapped_env.device, dtype=torch.long)

    # Cache init-state tensors once and reuse them to keep pose fully frozen.
    frozen_root_state = robot.data.default_root_state[env_ids].clone()
    frozen_joint_pos = robot.data.default_joint_pos[env_ids].clone()
    frozen_joint_vel = torch.zeros_like(frozen_joint_pos)

    if args_cli.strict_freeze:
        robot.write_root_state_to_sim(frozen_root_state, env_ids=env_ids)
        robot.write_joint_state_to_sim(frozen_joint_pos, frozen_joint_vel, env_ids=env_ids)

    while simulation_app.is_running():
        with torch.inference_mode():
            action_tensor = getattr(unwrapped_env.action_manager, "action", None)
            if action_tensor is None:
                raise RuntimeError("Unable to infer action tensor from env.unwrapped.action_manager.action")
            actions = torch.zeros_like(action_tensor)
            env.step(actions)

            if args_cli.strict_freeze:
                robot.write_root_state_to_sim(frozen_root_state, env_ids=env_ids)
                robot.write_joint_state_to_sim(frozen_joint_pos, frozen_joint_vel, env_ids=env_ids)

    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
