# robot_lab

[![IsaacSim](https://img.shields.io/badge/IsaacSim-5.1.0-silver.svg)](https://docs.omniverse.nvidia.com/isaacsim/latest/overview.html)
[![Isaac Lab](https://img.shields.io/badge/IsaacLab-2.3.2-silver)](https://isaac-sim.github.io/IsaacLab)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://docs.python.org/3/whatsnew/3.11.html)
[![Linux platform](https://img.shields.io/badge/platform-linux--64-orange.svg)](https://releases.ubuntu.com/22.04/)
[![Windows platform](https://img.shields.io/badge/platform-windows--64-orange.svg)](https://www.microsoft.com/en-us/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![License](https://img.shields.io/badge/license-Apache2.0-yellow.svg)](https://opensource.org/license/apache-2-0)

## Overview

**robot_lab** is a RL extension library for robots, based on IsaacLab. It allows you to develop in an isolated environment, outside of the core Isaac Lab repository.

The table below lists all available environments:

| Category   | Robot Model         | Environment Name (<ENV_NAME>)                                      | Screenshot |
|------------|---------------------|------------------------------------------------------------|------------|
| **Quadruped** | [Anymal D](https://www.anybotics.com/robotics/anymal) | RobotLab-Isaac-Velocity-Rough-Anymal-D-v0 | <img src="./docs/imgs/anymal_d.png" alt="anymal_d" width="75"> |
|            | [Unitree Go2](https://www.unitree.com/go2) | RobotLab-Isaac-Velocity-Rough-Unitree-Go2-v0 | <img src="./docs/imgs/unitree_go2.png" alt="unitree_go2" width="75"> |
|            | [Unitree B2](https://www.unitree.com/b2) | RobotLab-Isaac-Velocity-Rough-Unitree-B2-v0 | <img src="./docs/imgs/unitree_b2.png" alt="unitree_b2" width="75"> |
|            | [Unitree A1](https://www.unitree.com/a1) | RobotLab-Isaac-Velocity-Rough-Unitree-A1-v0 | <img src="./docs/imgs/unitree_a1.png" alt="unitree_a1" width="75"> |
|            | [Deeprobotics Lite3](https://www.deeprobotics.cn/robot/index/product1.html) | RobotLab-Isaac-Velocity-Rough-Deeprobotics-Lite3-v0 | <img src="./docs/imgs/deeprobotics_lite3.png" alt="Lite3" width="75"> |
|            | [Zsibot ZSL1](https://www.zsibot.com/zsl1) | RobotLab-Isaac-Velocity-Rough-Zsibot-ZSL1-v0 | <img src="./docs/imgs/zsibot_zsl1.png" alt="zsibot_zsl1" width="75"> |
|            | [Magiclab MagicDog](https://www.magiclab.top/dog) | RobotLab-Isaac-Velocity-Rough-MagicLab-Dog-v0 | <img src="./docs/imgs/magiclab_magicdog.png" alt="magiclab_magicdog" width="75"> |
| **Wheeled** | [Unitree Go2W](https://www.unitree.com/go2-w) | RobotLab-Isaac-Velocity-Rough-Unitree-Go2W-v0 | <img src="./docs/imgs/unitree_go2w.png" alt="unitree_go2w" width="75"> |
|            | [Unitree B2W](https://www.unitree.com/b2-w) | RobotLab-Isaac-Velocity-Rough-Unitree-B2W-v0 | <img src="./docs/imgs/unitree_b2w.png" alt="unitree_b2w" width="75"> |
|            | [Deeprobotics M20](https://www.deeprobotics.cn/robot/index/lynx.html) | RobotLab-Isaac-Velocity-Rough-Deeprobotics-M20-v0 | <img src="./docs/imgs/deeprobotics_m20.png" alt="deeprobotics_m20" width="75"> |
|            | [DDTRobot Tita](https://directdrive.com/product_TITA) | RobotLab-Isaac-Velocity-Rough-DDTRobot-Tita-v0 | <img src="./docs/imgs/ddtrobot_tita.png" alt="ddtrobot_tita" width="75"> |
|            | [Zsibot ZSL1W](https://www.zsibot.com/zsl1) | RobotLab-Isaac-Velocity-Rough-Zsibot-ZSL1W-v0 | <img src="./docs/imgs/zsibot_zsl1w.png" alt="zsibot_zsl1w" width="75"> |
|            | [Magiclab MagicDog-W](https://www.magiclab.top/dog-w) | RobotLab-Isaac-Velocity-Rough-MagicLab-Dog-W-v0 | <img src="./docs/imgs/magiclab_magicdog_w.png" alt="magiclab_magicdog_w" width="75"> |
| **Humanoid** | [Unitree G1](https://www.unitree.com/g1) | RobotLab-Isaac-Velocity-Rough-Unitree-G1-v0 | <img src="./docs/imgs/unitree_g1.png" alt="unitree_g1" width="75"> |
|             | [Unitree H1](https://www.unitree.com/h1) | RobotLab-Isaac-Velocity-Rough-Unitree-H1-v0 | <img src="./docs/imgs/unitree_h1.png" alt="unitree_h1" width="75"> |
|             | [FFTAI GR1T1](https://www.fftai.com/products-gr1) | RobotLab-Isaac-Velocity-Rough-FFTAI-GR1T1-v0 | <img src="./docs/imgs/fftai_gr1t1.png" alt="fftai_gr1t1" width="75"> |
|             | [FFTAI GR1T2](https://www.fftai.com/products-gr1) | RobotLab-Isaac-Velocity-Rough-FFTAI-GR1T2-v0 | <img src="./docs/imgs/fftai_gr1t2.png" alt="fftai_gr1t2" width="75"> |
|             | [Booster T1](https://www.boosterobotics.com/) | RobotLab-Isaac-Velocity-Rough-Booster-T1-v0 | <img src="./docs/imgs/booster_t1.png" alt="booster_t1" width="75"> |
|             | [RobotEra Xbot](https://www.robotera.com/) | RobotLab-Isaac-Velocity-Rough-RobotEra-Xbot-v0 | <img src="./docs/imgs/robotera_xbot.png" alt="robotera_xbot" width="75"> |
|             | [Openloong Loong](https://www.openloong.net/) | RobotLab-Isaac-Velocity-Rough-Openloong-Loong-v0 | <img src="./docs/imgs/openloong_loong.png" alt="openloong_loong" width="75"> |
|             | [RoboParty ATOM01](https://roboparty.cn/) | RobotLab-Isaac-Velocity-Rough-RoboParty-ATOM01-v0 | <img src="./docs/imgs/roboparty_atom01.png" alt="roboparty_atom01" width="75"> |
|             | [Magiclab MagicBot-Gen1](https://www.magiclab.top/human) | RobotLab-Isaac-Velocity-Rough-MagicLab-Bot-Gen1-v0 | <img src="./docs/imgs/magiclab_magicbot_gen1.png" alt="magiclab_magicbot_gen1" width="75"> |
|             | [Magiclab MagicBot-Z1](https://www.magiclab.top/z1) | RobotLab-Isaac-Velocity-Rough-MagicLab-Bot-Z1-v0 | <img src="./docs/imgs/magiclab_magicbot_z1.png" alt="magiclab_magicbot_z1" width="75"> |

> [!NOTE]
> If you want to run policy in gazebo or real robot, please use [rl_sar](https://github.com/fan-ziqi/rl_sar) project.
>
> Discuss in [Github Discussion](https://github.com/fan-ziqi/robot_lab/discussions) or [Discord](http://www.robotsfan.com/dc_robot_lab).

## My-Dog 机器人

本仓库新增了对 **My-Dog** 自制四足机器人的支持，包括小腿弹簧的物理建模、自定义执行器网络以及多种训练场景配置。

### 小腿弹簧机制

My-Dog 的小腿关节（FR/FL/RR/RL calf）安装了被动弹簧。弹簧产生的力矩与关节角度近似呈线性关系：

$$\tau_{\text{弹簧}} = k \cdot q + b$$

其中 $q$ 为关节角度（rad），$\tau_{\text{弹簧}}$ 为弹簧力矩（N·m）。

#### 测量方法

将小腿电机水平放置，让小腿在限位区间内以极低速度摆动（0.0078 rad/s，360 秒转动约 2.8 rad），近似认为每个角度都处于平衡状态：

1. **有弹簧实验**：安装弹簧，采集约 20,000 行数据
2. **无弹簧实验**：拆卸弹簧，采集约 20,000 行数据
3. **数据处理流程**：
   - 对有弹簧/无弹簧数据做角度插值差分
   - 低速筛选（$|\dot{q}| < 0.05$ rad/s）
   - 按角度分箱平均（箱宽 0.02 rad）
   - 同时做线性和三角函数拟合

#### 弹簧拟合系数

低速平衡状态下，电机力矩与弹簧力矩平衡（$\tau_{\text{电机}} + \tau_{\text{弹簧}} = 0$）。下表中的 $k, b$ 为**电机端实测力矩** $\tau_{\text{电机}} = k q + b$，实际代码中的弹簧力矩取其相反数：

| 关节       | $k$ (N·m/rad) | $b$ (N·m) | $R^2$   | 代码中弹簧力矩 |
|-----------|---------------|-----------|---------|--------------|
| FR_calf   | +1.026        | −1.967    | 0.925   | $\tau_{\text{弹簧}} = -1.026q + 1.967$ |
| FL_calf   | +1.270        | +2.476    | 0.957   | $\tau_{\text{弹簧}} = -1.271q - 2.476$ |
| RR_calf   | +1.078        | −2.154    | 0.926   | $\tau_{\text{弹簧}} = -1.078q + 2.154$ |
| RL_calf   | +1.113        | +2.225    | 0.961   | $\tau_{\text{弹簧}} = -1.113q - 2.225$ |

> **说明**：$b$ 的符号在左右腿间相反，是因为关节角度正方向的定义左右对称。

#### 执行器模型

My-Dog 使用基于神经网络的执行器模型 `MyDogSpringActuatorNetMLP`（位于 `source/robot_lab/robot_lab/assets/my_dog.py`），该类继承自 Isaac Lab 的 `ActuatorNetMLP`。

与传统的 PD 控制器 + 直流电机模型不同，ActuatorNetMLP 是一个**训练好的 MLP 网络**，输入位置误差历史和速度历史，直接输出力矩。在此基础上叠加弹簧补偿：

```python
# MLP 网络输出力矩 + 弹簧补偿力矩
spring_effort = k * joint_pos + b
computed_effort = network_output + spring_effort
```

执行器配置参数（`MY_DOG_CFG`）：

| 参数 | 值 | 说明 |
|------|-----|------|
| `network_file` | `motor.pt` | 训练好的 MLP 网络权重 |
| `enable_calf_spring` | `True` | 启用小腿弹簧补偿 |
| `effort_limit` | 16.8 N·m | 力矩上限 |
| `saturation_effort` | 16.8 N·m | 饱和力矩 |
| `velocity_limit` | 32.5 rad/s | 速度上限 |
| `input_order` | `pos_vel` | 输入顺序：位置误差→速度 |
| `input_idx` | `[0, 1, 2]` | 使用最近 3 帧历史 |

> **注意**：由于使用 ActuatorNetMLP 而非 PD 控制器，训练配置中已关闭 `randomize_actuator_gains` 随机化（ActuatorNet 不使用 stiffness/damping 参数）。

#### 验证工具

使用 `scripts/tools/verify_spring_effect.py` 对比有弹簧/无弹簧的电机遥测数据：

```bash
python scripts/tools/verify_spring_effect.py on.csv off.csv --speed-threshold 0.1
```

### 训练配置

My-Dog 在 `config/quadruped/my_dog/` 下支持以下训练场景：

| 配置文件 | 说明 |
|---------|------|
| `flat_env_cfg.py` | 平地运动 |
| `rough_env_cfg.py` | 崎岖地形运动 |
| `平地暂留配置.py` | 平地暂留（stand still） |

`agents/` 子目录下另有奖励函数的历史存档：

| 路径 | 说明 |
|------|------|
| `agents/保存的阶段性奖励函数配置/平地1.py` | 平地训练变体 |
| `agents/奖励函数参考配置/平地训练过限制高杆.py` | 高杆越障参考 |

### 可用奖励

奖励函数（`rewards.py`）针对 My-Dog 进行了扩展。详见 `可用奖励（仅依赖IMU电机）.md`，其中分类列出了仅依赖 IMU 和电机数据即可在真实机器人上部署的奖励项。

## Version Dependency

| robot_lab Version | Isaac Lab Version             | Isaac Sim Version         |
|------------------ | ----------------------------- | ------------------------- |
| `main` branch     | `main` branch                 | Isaac Sim 4.5 / 5.0 / 5.1 |
| `v2.3.2`          | `v2.3.2`                      | Isaac Sim 4.5 / 5.0 / 5.1 |
| `v2.2.2`          | `v2.2.1`                      | Isaac Sim 4.5 / 5.0       |
| `v2.1.1`          | `v2.1.1`                      | Isaac Sim 4.5             |
| `v1.1`            | `v1.4.1`                      | Isaac Sim 4.2             |

## Installation

- Install Isaac Lab by following the [installation guide](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html). We recommend using the conda installation as it simplifies calling Python scripts from the terminal.

- Clone this repository separately from the Isaac Lab installation (i.e. outside the `IsaacLab` directory):

  ```bash
  git clone https://github.com/fan-ziqi/robot_lab.git
  ```

- Using a python interpreter that has Isaac Lab installed, install the library

  ```bash
  python -m pip install -e source/robot_lab
  ```

- Verify that the extension is correctly installed by running the following command to print all the available environments in the extension:

  ```bash
  python scripts/tools/list_envs.py
  ```

<details>

<summary>Set up IDE (Optional, click to expand)</summary>

To setup the IDE, please follow these instructions:

- Run VSCode Tasks, by pressing `Ctrl+Shift+P`, selecting `Tasks: Run Task` and running the `setup_python_env` in the drop down menu. When running this task, you will be prompted to add the absolute path to your Isaac Sim installation.

If everything executes correctly, it should create a file .python.env in the `.vscode` directory. The file contains the python paths to all the extensions provided by Isaac Sim and Omniverse. This helps in indexing all the python modules for intelligent suggestions while writing code.

</details>

<details>

<summary>Setup as Omniverse Extension (Optional, click to expand)</summary>

We provide an example UI extension that will load upon enabling your extension defined in `source/robot_lab/robot_lab/ui_extension_example.py`.

To enable your extension, follow these steps:

1. **Add the search path of your repository** to the extension manager:
    - Navigate to the extension manager using `Window` -> `Extensions`.
    - Click on the **Hamburger Icon** (☰), then go to `Settings`.
    - In the `Extension Search Paths`, enter the absolute path to `robot_lab/source`
    - If not already present, in the `Extension Search Paths`, enter the path that leads to Isaac Lab's extension directory directory (`IsaacLab/source`)
    - Click on the **Hamburger Icon** (☰), then click `Refresh`.

2. **Search and enable your extension**:
    - Find your extension under the `Third Party` category.
    - Toggle it to enable your extension.

</details>

## Docker setup

<details>

<summary>Click to expand</summary>

### Building Isaac Lab Base Image

Currently, we don't have the Docker for Isaac Lab publicly available. Hence, you'd need to build the docker image
for Isaac Lab locally by following the steps [here](https://isaac-sim.github.io/IsaacLab/main/source/deployment/index.html).

Once you have built the base Isaac Lab image, you can check it exists by doing:

```bash
docker images

# Output should look something like:
#
# REPOSITORY                       TAG       IMAGE ID       CREATED          SIZE
# isaac-lab-base                   latest    28be62af627e   32 minutes ago   18.9GB
```

### Building robot_lab Image

Following above, you can build the docker container for this project. It is called `robot-lab`. However,
you can modify this name inside the [`docker/docker-compose.yaml`](docker/docker-compose.yaml).

```bash
cd docker
docker compose --env-file .env.base --file docker-compose.yaml build robot-lab
```

You can verify the image is built successfully using the same command as earlier:

```bash
docker images

# Output should look something like:
#
# REPOSITORY                       TAG       IMAGE ID       CREATED             SIZE
# robot-lab                        latest    00b00b647e1b   2 minutes ago       18.9GB
# isaac-lab-base                   latest    892938acb55c   About an hour ago   18.9GB
```

### Running the container

After building, the usual next step is to start the containers associated with your services. You can do this with:

```bash
docker compose --env-file .env.base --file docker-compose.yaml up
```

This will start the services defined in your `docker-compose.yaml` file, including robot-lab.

If you want to run it in detached mode (in the background), use:

```bash
docker compose --env-file .env.base --file docker-compose.yaml up -d
```

### Interacting with a running container

If you want to run commands inside the running container, you can use the `exec` command:

```bash
docker exec --interactive --tty -e DISPLAY=${DISPLAY} robot-lab /bin/bash
```

### Shutting down the container

When you are done or want to stop the running containers, you can bring down the services:

```bash
docker compose --env-file .env.base --file docker-compose.yaml down
```

This stops and removes the containers, but keeps the images.

</details>

## Try examples

You can use the following commands to run all environments:

RSL-RL:

```bash
# Train
python scripts/reinforcement_learning/rsl_rl/train.py --task=<TASK_NAME> --headless

# Play
python scripts/reinforcement_learning/rsl_rl/play.py --task=<TASK_NAME>
```

CusRL (**Experimental**):

```bash
# Train
python scripts/reinforcement_learning/cusrl/train.py --task=<TASK_NAME> --headless

# Play
python scripts/reinforcement_learning/cusrl/play.py --task=<TASK_NAME>
```

Running a task with dummy agents (These include dummy agents that output zero or random agents. They are useful to ensure that the environments are configured correctly):

```bash
# Zero-action agent
python scripts/tools/zero_agent.py --task=<TASK_NAME>
# Random-action agent
python scripts/tools/random_agent.py --task=<TASK_NAME>
```

BeyondMimic for Unitree G1:

- Gather the reference motion datasets (please follow the original licenses), we use the same convention as .csv of Unitree's dataset

  - Unitree-retargeted LAFAN1 Dataset is available
    on [HuggingFace](https://huggingface.co/datasets/lvhaidong/LAFAN1_Retargeting_Dataset)
  - Sidekicks are from [KungfuBot](https://kungfu-bot.github.io/)
  - Christiano Ronaldo celebration is from [ASAP](https://github.com/LeCAR-Lab/ASAP).
  - Balance motions are from [HuB](https://hub-robot.github.io/)

- Convert retargeted motions to include the maximum coordinates information (body pose, body velocity, and body acceleration) via forward kinematics

  ```bash
  python scripts/tools/beyondmimic/csv_to_npz.py -f path_to_input.csv --input_fps 60 --headless
  ```

- Replaying the motion in Isaac Sim:

  ```bash
  python scripts/tools/beyondmimic/replay_npz.py -f path_to_motion.npz
  ```

- Training and Evaluation

  ```bash
  # Train
  python scripts/reinforcement_learning/rsl_rl/train.py --task=RobotLab-Isaac-BeyondMimic-Flat-Unitree-G1-v0 --headless

  # Play
  python scripts/reinforcement_learning/rsl_rl/play.py --task=RobotLab-Isaac-BeyondMimic-Flat-Unitree-G1-v0 --num_envs 2
  ```

Others (**Experimental**)

- Train AMP Dance for Unitree G1

  ```bash
  # Train
  python scripts/reinforcement_learning/skrl/train.py --task=RobotLab-Isaac-G1-AMP-Dance-Direct-v0 --algorithm AMP --headless

  # Play
  python scripts/reinforcement_learning/skrl/play.py --task=RobotLab-Isaac-G1-AMP-Dance-Direct-v0 --algorithm AMP --num_envs=32
  ```

- Train Handstand for Unitree A1

  ```bash
  # Train
  python scripts/reinforcement_learning/rsl_rl/train.py --task=RobotLab-Isaac-Velocity-Flat-HandStand-Unitree-A1-v0 --headless

  # Play
  python scripts/reinforcement_learning/rsl_rl/play.py --task=RobotLab-Isaac-Velocity-Flat-HandStand-Unitree-A1-v0
  ```

- Train Anymal D with symmetry

  ```bash
  # Train
  python scripts/reinforcement_learning/rsl_rl/train.py --task=RobotLab-Isaac-Velocity-Rough-Anymal-D-v0 --headless --agent=rsl_rl_with_symmetry_cfg_entry_point --run_name=ppo_with_symmetry_data_augmentation agent.algorithm.symmetry_cfg.use_data_augmentation=true

  # Play
  python scripts/reinforcement_learning/rsl_rl/play.py --task=RobotLab-Isaac-Velocity-Rough-Anymal-D-v0 --agent=rsl_rl_with_symmetry_cfg_entry_point --run_name=ppo_with_symmetry_data_augmentation agent.algorithm.symmetry_cfg.use_data_augmentation=true
  ```

- Training and distilling Anymal D

  ```bash
  # Train the teacher agent
  python scripts/reinforcement_learning/rsl_rl/train.py --task=RobotLab-Isaac-Velocity-Flat-Anymal-D-v0 --headless

  # Distill the teacher agent into a student agent
  python scripts/reinforcement_learning/rsl_rl/train.py --task=RobotLab-Isaac-Velocity-Flat-Anymal-D-v0 --headless --agent=rsl_rl_distillation_cfg_entry_point --load_run teacher_run_folder_name

  # Play the student agent
  python scripts/reinforcement_learning/rsl_rl/play.py --task=RobotLab-Isaac-Velocity-Flat-Anymal-D-v0 --num_envs 64 --agent rsl_rl_distillation_cfg_entry_point
  ```

> [!NOTE]
> If you want to control a **SINGLE ROBOT** with the keyboard during playback, add `--keyboard` at the end of the play script.
>
> ```
> Key bindings:
> ====================== ========================= ========================
> Command                Key (+ve axis)            Key (-ve axis)
> ====================== ========================= ========================
> Move along x-axis      Numpad 8 / Arrow Up       Numpad 2 / Arrow Down
> Move along y-axis      Numpad 4 / Arrow Right    Numpad 6 / Arrow Left
> Rotate along z-axis    Numpad 7 / Z              Numpad 9 / X
> ====================== ========================= ========================
> ```

* You can change `Rough` to `Flat` in the above configs.
* Record video of a trained agent (requires installing `ffmpeg`), add `--video --video_length 200`
* Play/Train with 32 environments, add `--num_envs 32`
* Play on specific folder or checkpoint, add `--load_run run_folder_name --checkpoint /PATH/TO/model.pt`
* Resume training from folder or checkpoint, add `--resume --load_run run_folder_name --checkpoint /PATH/TO/model.pt`
* To train with multiple GPUs, use the following command, where --nproc_per_node represents the number of available GPUs:
    ```bash
    python -m torch.distributed.run --nnodes=1 --nproc_per_node=2 scripts/reinforcement_learning/rsl_rl/train.py --task=<TASK_NAME> --headless --distributed
    ```
* To scale up training beyond multiple GPUs on a single machine, it is also possible to train across multiple nodes. To train across multiple nodes/machines, it is required to launch an individual process on each node.

    For the master node, use the following command, where --nproc_per_node represents the number of available GPUs, and --nnodes represents the number of nodes:
    ```bash
    python -m torch.distributed.run --nproc_per_node=2 --nnodes=2 --node_rank=0 --rdzv_id=123 --rdzv_backend=c10d --rdzv_endpoint=localhost:5555 scripts/reinforcement_learning/rsl_rl/train.py --task=<TASK_NAME> --headless --distributed
    ```
    Note that the port (`5555`) can be replaced with any other available port.
    For non-master nodes, use the following command, replacing `--node_rank` with the index of each machine:
    ```bash
    python -m torch.distributed.run --nproc_per_node=2 --nnodes=2 --node_rank=1 --rdzv_id=123 --rdzv_backend=c10d --rdzv_endpoint=ip_of_master_machine:5555 scripts/reinforcement_learning/rsl_rl/train.py --task=<TASK_NAME> --headless --distributed
    ```

## Add your own robot

Using the core framework developed as part of Isaac Lab, we provide various learning environments for robotics research.
These environments follow the `gym.Env` API from OpenAI Gym version `0.21.0`. The environments are registered using
the Gym registry.

Each environment's name is composed of `Isaac-<Task>-<Robot>-v<X>`, where `<Task>` indicates the skill to learn
in the environment, `<Robot>` indicates the embodiment of the acting agent, and `<X>` represents the version of
the environment (which can be used to suggest different observation or action spaces).

The environments are configured using either Python classes (wrapped using `configclass` decorator) or through
YAML files. The template structure of the environment is always put at the same level as the environment file
itself. However, its various instances are included in directories within the environment directory itself.
This looks like as follows:

```tree
source/robot_lab/assets/
├── __init__.py
└── unitree.py  # <- this is where we define robot assets

source/robot_lab/tasks/manager_based/locomotion/
├── __init__.py
└── velocity
    ├── config
    │   └── unitree_a1
    │       ├── agent  # <- this is where we store the learning agent configurations
    │       ├── __init__.py  # <- this is where we register the environment and configurations to gym registry
    │       ├── flat_env_cfg.py
    │       └── rough_env_cfg.py
    ├── __init__.py
    └── velocity_env_cfg.py  # <- this is the base task configuration
```

The environments are then registered in the `source/robot_lab/tasks/manager_based/locomotion/velocity/config/unitree_a1/__init__.py`:

```python
gym.register(
    id="RobotLab-Isaac-Velocity-Flat-Unitree-A1-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.flat_env_cfg:UnitreeA1FlatEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:UnitreeA1FlatPPORunnerCfg",
        "cusrl_cfg_entry_point": f"{agents.__name__}.cusrl_ppo_cfg:UnitreeA1FlatTrainerCfg",
    },
)

gym.register(
    id="RobotLab-Isaac-Velocity-Rough-Unitree-A1-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.rough_env_cfg:UnitreeA1RoughEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:UnitreeA1RoughPPORunnerCfg",
        "cusrl_cfg_entry_point": f"{agents.__name__}.cusrl_ppo_cfg:UnitreeA1RoughTrainerCfg",
    },
)
```

## Tensorboard

To view tensorboard, run:

```bash
tensorboard --logdir=logs
```

## Code formatting

A pre-commit template is given to automatically format the code.

To install pre-commit:

```bash
pip install pre-commit
```

Then you can run pre-commit with:

```bash
pre-commit run --all-files
```

## Troubleshooting

### Pylance Missing Indexing of Extensions

In some VsCode versions, the indexing of part of the extensions is missing. In this case, add the path to your extension in `.vscode/settings.json` under the key `"python.analysis.extraPaths"`.

**Note: Replace `<path-to-isaac-lab>` with your own IsaacLab path.**

```json
{
    "python.languageServer": "Pylance",
    "python.analysis.extraPaths": [
        "${workspaceFolder}/source/robot_lab",
        "/<path-to-isaac-lab>/source/isaaclab",
        "/<path-to-isaac-lab>/source/isaaclab_assets",
        "/<path-to-isaac-lab>/source/isaaclab_mimic",
        "/<path-to-isaac-lab>/source/isaaclab_rl",
        "/<path-to-isaac-lab>/source/isaaclab_tasks",
    ]
}
```

### Clean USD Caches

Temporary USD files are generated in `/tmp/IsaacLab/usd_{date}_{time}_{random}` during simulation runs. These files can consume significant disk space and can be cleaned by:

```bash
rm -rf /tmp/IsaacLab/usd_*
```

## Citation

Please cite the following if you use this code or parts of it:

```
@software{fan-ziqi2024robot_lab,
  author = {Ziqi Fan},
  title = {robot_lab: RL Extension Library for Robots, Based on IsaacLab.},
  url = {https://github.com/fan-ziqi/robot_lab},
  year = {2024}
}
```

## Acknowledgements

The project uses some code from the following open-source code repositories:

- [linden713/humanoid_amp](https://github.com/linden713/humanoid_amp)
- [HybridRobotics/whole_body_tracking](https://github.com/HybridRobotics/whole_body_tracking)
