# Copyright (c) 2024-2026 Ziqi Fan
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Script to train RL agent with RSL-RL."""

"""Launch Isaac Sim Simulator first."""

import argparse
import sys

# 接入 error_tracker 错误日志
sys.path.insert(0, "scripts/tools/error_tracker")
import error_tracker
error_tracker.setup("logs")


from isaaclab.app import AppLauncher
# local imports
import cli_args  # isort: skip

# add argparse arguments
parser = argparse.ArgumentParser(description="Train an RL agent with RSL-RL.")
parser.add_argument("--video", action="store_true", default=False, help="Record videos during training.")
parser.add_argument("--video_length", type=int, default=200, help="Length of the recorded video (in steps).")
parser.add_argument("--video_interval", type=int, default=2000, help="Interval between video recordings (in steps).")
parser.add_argument("--num_envs", type=int, default=None, help="Number of environments to simulate.")
parser.add_argument("--task", type=str, default=None, help="Name of the task.")
parser.add_argument(
    "--agent", type=str, default="rsl_rl_cfg_entry_point", help="Name of the RL agent configuration entry point."
)
parser.add_argument("--seed", type=int, default=None, help="Seed used for the environment")
parser.add_argument("--max_iterations", type=int, default=None, help="RL Policy training iterations.")
parser.add_argument(
    "--distributed", action="store_true", default=False, help="Run training with multiple GPUs or nodes."
)
parser.add_argument("--export_io_descriptors", action="store_true", default=False, help="Export IO descriptors.")
parser.add_argument(
    "--ray-proc-id", "-rid", type=int, default=None, help="Automatically configured by Ray integration, otherwise None."
)
# append RSL-RL cli arguments
cli_args.add_rsl_rl_args(parser)
# append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)
args_cli, hydra_args = parser.parse_known_args()

# always enable cameras to record video
if args_cli.video:
    args_cli.enable_cameras = True

# clear out sys.argv for Hydra
sys.argv = [sys.argv[0]] + hydra_args

# launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""Check for minimum supported RSL-RL version."""

import importlib.metadata as metadata
import platform

from packaging import version

# check minimum supported rsl-rl version
RSL_RL_VERSION = "3.0.1"
installed_version = metadata.version("rsl-rl-lib")
if version.parse(installed_version) < version.parse(RSL_RL_VERSION):
    if platform.system() == "Windows":
        cmd = [r".\isaaclab.bat", "-p", "-m", "pip", "install", f"rsl-rl-lib=={RSL_RL_VERSION}"]
    else:
        cmd = ["./isaaclab.sh", "-p", "-m", "pip", "install", f"rsl-rl-lib=={RSL_RL_VERSION}"]
    print(
        f"Please install the correct version of RSL-RL.\nExisting version is: '{installed_version}'"
        f" and required version is: '{RSL_RL_VERSION}'.\nTo install the correct version, run:"
        f"\n\n\t{' '.join(cmd)}\n"
    )
    exit(1)

"""Rest everything follows."""

import logging
import os
import time
from datetime import datetime

import gymnasium as gym
import torch
from rsl_rl.runners import DistillationRunner, OnPolicyRunner 

from isaaclab.envs import (
    DirectMARLEnv,
    DirectMARLEnvCfg,
    DirectRLEnvCfg,
    ManagerBasedRLEnvCfg,
    multi_agent_to_single_agent,
)
from isaaclab.utils.dict import print_dict
from isaaclab.utils.io import dump_yaml

from isaaclab_rl.rsl_rl import RslRlBaseRunnerCfg, RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg # handle_deprecated_rsl_rl_cfg兼容新版 rsl-rl-lib >=4.x

from isaaclab_tasks.utils import get_checkpoint_path
from isaaclab_tasks.utils.hydra import hydra_task_config

import robot_lab.tasks  # noqa: F401  # isort: skip

# import logger
logger = logging.getLogger(__name__)

# PLACEHOLDER: Extension template (do not remove this comment)

torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
torch.backends.cudnn.deterministic = False
torch.backends.cudnn.benchmark = False


@hydra_task_config(args_cli.task, args_cli.agent)
def main(env_cfg: ManagerBasedRLEnvCfg | DirectRLEnvCfg | DirectMARLEnvCfg, agent_cfg: RslRlBaseRunnerCfg):
    """Train with RSL-RL agent."""
    # override configurations with non-hydra CLI arguments
    agent_cfg = cli_args.update_rsl_rl_cfg(agent_cfg, args_cli)
    env_cfg.scene.num_envs = args_cli.num_envs if args_cli.num_envs is not None else env_cfg.scene.num_envs
    agent_cfg.max_iterations = (
        args_cli.max_iterations if args_cli.max_iterations is not None else agent_cfg.max_iterations
    )
    # === 新增这两行（处理弃用配置）===
    # handle deprecated configurations（兼容新版 rsl-rl-lib >=4.x）
    agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, installed_version)
    # set the environment seed
    # note: certain randomizations occur in the environment initialization so we set the seed here
    env_cfg.seed = agent_cfg.seed
    env_cfg.sim.device = args_cli.device if args_cli.device is not None else env_cfg.sim.device
    # check for invalid combination of CPU device with distributed training
    if args_cli.distributed and args_cli.device is not None and "cpu" in args_cli.device:
        raise ValueError(
            "Distributed training is not supported when using CPU device. "
            "Please use GPU device (e.g., --device cuda) for distributed training."
        )

    # multi-gpu training configuration
    if args_cli.distributed:
        env_cfg.sim.device = f"cuda:{app_launcher.local_rank}"
        agent_cfg.device = f"cuda:{app_launcher.local_rank}"

        # set seed to have diversity in different threads
        seed = agent_cfg.seed + app_launcher.local_rank
        env_cfg.seed = seed
        agent_cfg.seed = seed

    # specify directory for logging experiments
    log_root_path = os.path.join("logs", "rsl_rl", agent_cfg.experiment_name)
    log_root_path = os.path.abspath(log_root_path)
    print(f"[INFO] Logging experiment in directory: {log_root_path}")
    # specify directory for logging runs: {time-stamp}_{run_name}
    log_dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # The Ray Tune workflow extracts experiment name using the logging line below, hence, do not
    # change it (see PR #2346, comment-2819298849)
    print(f"Exact experiment name requested from command line: {log_dir}")
    if agent_cfg.run_name:
        log_dir += f"_{agent_cfg.run_name}"
    log_dir = os.path.join(log_root_path, log_dir)

    # set the IO descriptors export flag if requested
    if isinstance(env_cfg, ManagerBasedRLEnvCfg):
        env_cfg.export_io_descriptors = args_cli.export_io_descriptors
    else:
        logger.warning(
            "IO descriptors are only supported for manager based RL environments. No IO descriptors will be exported."
        )

    # set the log directory for the environment (works for all environment types)
    env_cfg.log_dir = log_dir

    # create isaac environment
    env = gym.make(args_cli.task, cfg=env_cfg, render_mode="rgb_array" if args_cli.video else None)
    
    # convert to single-agent instance if required by the RL algorithm
    if isinstance(env.unwrapped, DirectMARLEnv):
        env = multi_agent_to_single_agent(env)

    # save resume path before creating a new log_dir
    if agent_cfg.resume or agent_cfg.algorithm.class_name == "Distillation":
        resume_path = get_checkpoint_path(log_root_path, agent_cfg.load_run, agent_cfg.load_checkpoint)

    # wrap for video recording
    if args_cli.video:
        video_kwargs = {
            "video_folder": os.path.join(log_dir, "videos", "train"),
            "step_trigger": lambda step: step % args_cli.video_interval == 0,
            "video_length": args_cli.video_length,
            "disable_logger": True,
        }
        print("[INFO] Recording videos during training.")
        print_dict(video_kwargs, nesting=4)
        env = gym.wrappers.RecordVideo(env, **video_kwargs)

    start_time = time.time()

    # save unwrapped gym env reference for curriculum check (VecEnv wrapper loses access)
    gym_env = env

    # wrap around environment for rsl-rl
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)

    # create runner from rsl-rl
    if agent_cfg.class_name == "OnPolicyRunner":
        runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=log_dir, device=agent_cfg.device)
    elif agent_cfg.class_name == "DistillationRunner":
        runner = DistillationRunner(env, agent_cfg.to_dict(), log_dir=log_dir, device=agent_cfg.device)
    else:
        raise ValueError(f"Unsupported runner class: {agent_cfg.class_name}")
    # write git state to logs
    runner.add_git_repo_to_log(__file__)
    # load the checkpoint
    if agent_cfg.resume or agent_cfg.algorithm.class_name == "Distillation":
        print(f"[INFO]: Loading model checkpoint from: {resume_path}")
        # load previously trained model
        runner.load(resume_path)

    # dump the configuration into log-directory
    dump_yaml(os.path.join(log_dir, "params", "env.yaml"), env_cfg)
    dump_yaml(os.path.join(log_dir, "params", "agent.yaml"), agent_cfg)

    # run training with curriculum-aware auto-stop
    # ------------------------------------------------------------------
    # 自定义训练循环：当课程学习 (command_levels) 达到 1.0 时，
    # 自动将 max_iterations 调整为 "课程完成轮数 × 2"
    # ------------------------------------------------------------------
    # Randomize initial episode lengths (for exploration)
    env.episode_length_buf = torch.randint_like(
        env.episode_length_buf, high=int(env.max_episode_length)
    )

    obs = env.get_observations().to(agent_cfg.device)
    runner.alg.train_mode()

    if getattr(runner, "is_distributed", False):
        runner.alg.broadcast_parameters()

    runner.logger.init_logging_writer()

    curriculum_done_iteration = None
    start_it = runner.current_learning_iteration
    total_it = start_it + agent_cfg.max_iterations

    for it in range(start_it, total_it):
        start = time.time()
        # Rollout
        with torch.inference_mode():
            for _ in range(agent_cfg.num_steps_per_env):
                actions = runner.alg.act(obs)
                obs, rewards, dones, extras = env.step(actions.to(env.device))
                if getattr(agent_cfg, "check_for_nan", True):
                    from rsl_rl.utils import check_nan

                    check_nan(obs, rewards, dones)
                obs, rewards, dones = (
                    obs.to(agent_cfg.device),
                    rewards.to(agent_cfg.device),
                    dones.to(agent_cfg.device),
                )
                runner.alg.process_env_step(obs, rewards, dones, extras)
                intrinsic_rewards = (
                    runner.alg.intrinsic_rewards
                    if getattr(agent_cfg.algorithm, "rnd_cfg", None)
                    else None
                )
                runner.logger.process_env_step(rewards, dones, extras, intrinsic_rewards)

            stop = time.time()
            collect_time = stop - start
            start = stop
            runner.alg.compute_returns(obs)

        # Update policy
        loss_dict = runner.alg.update()
        stop = time.time()
        learn_time = stop - start
        runner.current_learning_iteration = it

        # Log
        runner.logger.log(
            it=it,
            start_it=start_it,
            total_it=total_it,
            collect_time=collect_time,
            learn_time=learn_time,
            loss_dict=loss_dict,
            learning_rate=runner.alg.learning_rate,
            action_std=runner.alg.get_policy().output_std,
            rnd_weight=runner.alg.rnd.weight if getattr(agent_cfg.algorithm, "rnd_cfg", None) else None,
        )

        # Save model
        if runner.logger.writer is not None and it % agent_cfg.save_interval == 0:
            runner.save(os.path.join(runner.logger.log_dir, f"model_{it}.pt"))

        # === 课程学习完成检查 ===
        if curriculum_done_iteration is None:
            try:
                cm = gym_env.command_manager
                lin_max = cm.get_term("base_velocity").cfg.ranges.lin_vel_x[1]
                ang_max = cm.get_term("base_velocity").cfg.ranges.ang_vel_z[1]
                if lin_max >= 1.0 and ang_max >= 1.0:
                    curriculum_done_iteration = it
                    new_total = curriculum_done_iteration * 2
                    print(f"\n{'=' * 60}")
                    print(f"[CURRICULUM] 课程学习达到上限 (lin={lin_max}, ang={ang_max})")
                    print(f"[CURRICULUM] 完成轮数: {curriculum_done_iteration}")
                    print(f"[CURRICULUM] 新 max_iterations: {new_total} (2×)")
                    print(f"{'=' * 60}\n")
                    total_it = new_total
            except Exception:
                pass  # 静默失败，不影响训练

    # Final save
    if runner.logger.writer is not None:
        runner.save(os.path.join(runner.logger.log_dir, f"model_{runner.current_learning_iteration}.pt"))
        runner.logger.stop_logging_writer()

    # Final save
    if runner.logger.writer is not None:
        runner.save(os.path.join(runner.logger.log_dir, f"model_{runner.current_learning_iteration}.pt"))
        runner.logger.stop_logging_writer()

    print(f"Training time: {round(time.time() - start_time, 2)} seconds")

    # close the simulator
    env.close()


if __name__ == "__main__":
    # run the main function
    main()
    # close sim app
    simulation_app.close()