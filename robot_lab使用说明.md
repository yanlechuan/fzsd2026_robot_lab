### 涉及到的主要文件目录

```bash
├── logs/
│   └── rsl_rl/ 存放强化学习过程中产生的日志文件
├── outputs/ 存放训练的最终产物
├── scripts/ 存放可执行脚本
│   ├── reinforcement_learning/ 强化学习相关脚本（对应不同的强化学习算法库）
│   │   ├── cusrl/
│   │   │   ├── play.py
│   │   │   └── train.py
│   │   ├── rsl_rl/
│   │   │   ├── cli_args.py
│   │   │   ├── play_cs.py
│   │   │   ├── play.py
│   │   │   └── train.py
│   │   ├── skrl/
│   │   │   ├── play.py
│   │   │   └── train.py
│   │   └── rl_utils.py
│   └── tools/ 各种工具脚本
│       ├── clean_trash.py
│       ├── convert_mjcf.py 将其他格式的机器人模型issac sim可使用的usd格式
│       ├── convert_urdf.py 
│       ├── list_envs.py 列出当前项目中所有可用的训练环境
│       ├── random_agent.py 使用随机策略或者令动作控制机器人，测试训练环境是否正常
│       └── zero_agent.py
├── source/ 项目核心源代码
│   └── robot_lab/ 安装到isaac sim的拓展包
│       ├── config/ 拓展的清单文件
│       │   └── extension.toml
│       ├── data/ 存放资源文件，如机器人模型
│       │   └── Robots/ my_dog机器人资产示例
│       │       └── my_dog/
│       │           ├── configuration/
│       │           │   ├── my_dog_description_base.usd
│       │           │   ├── my_dog_description_physics.usd
│       │           │   ├── my_dog_description_robot.usd
│       │           │   └── my_dog_description_sensor.usd
│       │           ├── config.yaml
│       │           ├── my_dog_description.urdf
│       │           └── my_dog_description.usd
│       ├── robot_lab/ 拓展的Python源码
│       │   ├── assets/ 机器人资产的定义，将data/中的资源文件封装成isaac sim可识别的类
│       │   │   ├── __init__.py 
│       │   │   └── my_dog.py 定义了Mydog类，是仿真中机器人实例的蓝图
│       │   ├── tasks/ 任务定义，是框架的核心
│       │   │   ├── manager_based/ 
│       │   │   │   ├── locomotion/
│       │   │   │   │   ├── velocity/ 一个具体的任务--基于速度指令的足式机器人移动
│       │   │   │   │   │   ├── config/ 任务和算法的配置文件目录
│       │   │   │   │   │   │   ├── quadruped/ 
│       │   │   │   │   │   │   │   ├── my_dog/ 为my_dog机器人配置不同的训练环境
│       │   │   │   │   │   │   │   │   ├── agents/ 不同强化学习算法针对此机器人的超参数配置
│       │   │   │   │   │   │   │   │   │   ├── cusrl_ppo_cfg.py
│       │   │   │   │   │   │   │   │   │   ├── __init__.py
│       │   │   │   │   │   │   │   │   │   └── rsl_rl_ppo_cfg.py
│       │   │   │   │   │   │   │   │   ├── flat_env_cfg.py 平坦环境的配置
│       │   │   │   │   │   │   │   │   ├── __init__.py 
│       │   │   │   │   │   │   │   │   └── rough_env_cfg.py
│       │   │   │   │   │   │   │   ├── unitree_go2/
│       │   │   │   │   │   │   │   │   ├── agents/
│       │   │   │   │   │   │   │   │   │   ├── cusrl_ppo_cfg.py
│       │   │   │   │   │   │   │   │   │   ├── __init__.py
│       │   │   │   │   │   │   │   │   │   └── rsl_rl_ppo_cfg.py
│       │   │   │   │   │   │   │   │   ├── flat_env_cfg.py
│       │   │   │   │   │   │   │   │   ├── __init__.py
│       │   │   │   │   │   │   │   │   └── rough_env_cfg.py
│       │   │   │   │   │   │   │   └── __init__.py
│       │   │   │   │   │   │   └── __init__.py
│       │   │   │   │   │   ├── mdp/ 定义了强化学习的马尔科夫决策各个组件
│       │   │   │   │   │   │   ├── symmetry/ 
│       │   │   │   │   │   │   │   ├── anymal.py
│       │   │   │   │   │   │   │   └── __init__.py
│       │   │   │   │   │   │   ├── commands.py 生成指挥机器人运动的命令
│       │   │   │   │   │   │   ├── curriculums.py 课程学习设置
│       │   │   │   │   │   │   ├── events.py 随机化事件
│       │   │   │   │   │   │   ├── __init__.py
│       │   │   │   │   │   │   ├── observations.py 给智能体的观测
│       │   │   │   │   │   │   ├── rewards.py 奖励函数的设计
│       │   │   │   │   │   │   └── utils.py 
│       │   │   │   │   │   ├── __init__.py
│       │   │   │   │   │   └── velocity_env_cfg.py
│       │   │   │   │   └── __init__.py
│       │   │   │   └── __init__.py
│       │   │   └── __init__.py
│       │   ├── __init__.py
│       │   └── ui_extension_example.py
│       ├── pyproject.toml
│       └── setup.py
├── CONTRIBUTORS.md
├── LICENSE
├── pyproject.toml
├── README.md
└── VERSION
```

### 一、导入自己的my_dog

注释：强化学习需要调整的参数及其含义已经在环境配置文件`flat_env_cfg.py`和`rough_env_cfg.py`中注明，并备注初始值。

1. 在`source/robot_lab/data/Robots`下创建`my_dog`文件夹，该文件夹需要包含urdf文件`my_dog_description.urdf`和`meshes文件夹`（包含stl文件）

   ![image-20260305013805961](/home/ylc/snap/typora/110/.config/Typora/typora-user-images/image-20260305013805961.png)
2. 在`source/robot_lab/robot_lab/assets`创建资产文件`my_dog.py`,目前是用go2的进行换皮，主要替换有类名改为`MY_DOG_CFG`，`asset_path= [地址改为1中urdf的文件地址]`，其他数值改动已经在注释中标出.

   ![image-20260305013940479](/home/ylc/snap/typora/110/.config/Typora/typora-user-images/image-20260305013940479.png)

### 二、为my_dog配置并注册环境

1. 配置过程：在`source/robot_lab/robot_lab/tasks/manager_based/locomotion/velocity/config/quadruped`中复制一份go2的环境配置文件夹`unitree_b2`,在`flat_env_cfg.py`和`rough_env_cfg.py`中将所有go2相关的命名（如`UnitreeGo2`,`unitree`,`UNITREE_GO2_CFG`）改为my_dog相关的命名(`My_dog`,`my_dog`,`MY_DOG_CFG`)。

   需要注意的是在运行训练命令时，目前以用的urdf模型中的foot会和calf合并，导致检测不到foot部分。所以主要改动foot_link_name变量的赋值，从`".*_foot"`变为` ".*_calf"`（改动后虽然目前对训练没有什么影响，但是觉得还是得想办法直接使用foot部分而不是用_calf的末端代替）.还有需要注意的是urdf关节名称的修改，在参数joint_names的赋值中都是以`_joint`结尾，如有不同对应的urdf和stl文件命名也应该对应修改。
2. 接下来是agent文件夹的修改，修改方式和1相同，只是名称换皮。其中的`rsl_rl_ppo_cfg.py`和`cusrl_ppo_cfg.py`可以调整训练轮数，环境中模型数量等等但是目前使用的只有`rsl_rl_ppo_cfg.py`。

   最后注册是在`source/robot_lab/robot_lab/tasks/manager_based/locomotion/velocity/config/quadruped/my_dog/__init__.py`中修改对应名称。目前已经注册的id为`RobotLab-Isaac-Velocity-Flat-My_dog-v0`和`RobotLab-Isaac-Velocity-Rough-My_dog-v0`这是后续要使用的`<TASK_NAME>`.

   ![image-20260305014142216](/home/ylc/snap/typora/110/.config/Typora/typora-user-images/image-20260305014142216.png)

   至此已经完成了my_dog的导入以及环境的注册.

   参考视频：(https://www.bilibili.com/video/BV17FERz2Eie?spm_id_from=333.788.player.switch&vd_source=11ca289d67c4425f2936bdb3cf77fcff)该视频是在Isaaclab里调整的，仅仅作为参考。

### 三、训练命令的使用

首先运行：

```bash
conda activate my_dog
cd robot_lab
```

进入conda环境并到工作空间内

#### 1、训练命令模板：

```bash
python scripts/reinforcement_learning/rsl_rl/train.py --task=<TASK_NAME>
```

对应到实例：

```bash
python scripts/reinforcement_learning/rsl_rl/train.py --task=RobotLab-Isaac-Velocity-Flat-My_dog-v0 
```

在`/home/ylc/robot_lab/logs/rsl_rl/my_dog_flat/对应日期`的文件夹下会实时生成`model_num.pt`文件，默认每100记录一次，此时还无法用于sim_to_sim的仿真。

在`scripts/reinforcement_learning`下配备了三种强化学习库:`rsl_rl`, `cusrl`以及`skrl`,它们的对比与关联如下：


|   特性   |         RSL_RL         |          CUSRL          |               **SKRL**               |
| :------: | :--------------------: | :---------------------: | :-----------------------------------: |
| 主要领域 | 腿足机器人控制（权威） |    机器人/高性能计算    |           通用机器人/RL研究           |
| 核心优势 | 领域专用、经过实战检验 | 极致训练速度（GPU优化） |         模块化设计、灵活易用         |
| 环境集成 |   深度集成 Isaac Lab   | 通常与高性能仿真器结合 | 支持多种环境（Isaac Lab, PyBullet等） |
| 使用定位 | 生产级机器人控制器训练 |    高性能研究与应用    |            研究与原型开发            |

故目前只使用了rsl_rl进行训练.

#### 2、查看训练效果并导出policy.pt文件

```bash
python scripts/reinforcement_learning/rsl_rl/play.py --task=RobotLab-Isaac-Velocity-Flat-My_dog-v0
```

在无任何参数的情况时，是默认调用`my_dog_flat`中最新的`model_num.pt`文件，并在`logs/rsl_rl/my_dog_flat/对应日期/exported`下生成可用于sim_ro_sim的`policy.pt` 和`policy.onnx`

我在gazebo仿真时用的conda环境：

```bash
conda activate sim_to_sim
```

#### 在命令中可以调整的参数：

```bash
#常用训练控制参数
--headless #无头模式，控制训练时是否可视化，使用则否
--num_env= #设置并行环境实例的数量，默认值通常由配置文件决定
--seed= #设置随机种子，确保实验可复现。
#常用训练控制参数
--load_run #指定要恢复的实验运行目录名称，不是路径，例如：2026-03-04_17-04-30
--checkpoint #指定要加载的具体模型文件名,而不是文件路径，例如：model_6400.pt
--resume  #从之前的运行中恢复训练。通常与 --load_run和 --checkpoint一起使用。如 --resume --load_run 2026-03-04_17-04-30 --checkpoint model_6400.pt
#设备与性能
--sim_device  #指定物理模拟运行设备，例如 cuda:0(GPU) 或 cpu。
--rl_device  #指定强化学习算法（如PPO）运行设备，例如 cuda:0或 cpu。
--torch_threads  #设置PyTorch使用的线程数，可用于优化CPU性能。
```

对应的示例：

```bash
# 1. 从头开始一个新训练，并命名实验
python scripts/reinforcement_learning/rsl_rl/train.py \
  --task=RobotLab-Isaac-Velocity-Flat-My_dog-v0 \
  --experiment_name="my_new_run" \
  --num_envs=2048 \
  --headless

# 2. 从特定检查点恢复训练
python scripts/reinforcement_learning/rsl_rl/train.py \
  --task=RobotLab-Isaac-Velocity-Flat-My_dog-v0 \
  --headless \
  --resume \
  --load_run 2026-03-04_17-04-30 \
  --checkpoint model_6400.pt

# 3. 使用自定义配置文件并设置随机种子
python scripts/reinforcement_learning/rsl_rl/train.py \
  --task=RobotLab-Isaac-Velocity-Flat-My_dog-v0 \
  --cfg=my_custom_ppo_cfg.yaml \
  --seed=42 \
  --headless
```

其他如有差异或想要调节其他参数使用`--help`查看比较妥当。

### 四、文件夹功能的粗略讲解

#### 1、docker(略)

#### 2、logs

该文件夹用于存放强化学习的训练结果，每个以日期命名的文件夹对应一次训练，含有`model_num.pt`文件和`policy.pt`文件。

#### 3、outputs

`config.yaml`：将机器人（My_dog）、任务（在平面上追踪随机速度指令）、学习算法（PPO）和训练范式（并行仿真、课程随机化）封装成一个可执行、可复现、且高度可定制的实验方案，这里并非源文件，修改无效，只是记录。

hydra.yaml文件：通过自动化、标准化的方式，将一次实验的“代码、配置、输出、日志”打包成一个可独立存证、追溯和复现的完整记录单元。

#### 4、scripts

`tool`文件夹：这里含有多种工具，具体功能已经在每个py文件开头注释。

`reinforcement_learning`文件夹：包含了强化学习的三种实现方式，`cusrl`,`rsl_rl`以及`skrl`.大致区别已经在前文提到。每个方式都有train.py和play.py用以训练和导出可用结果。

#### 5、source

最主要的文件夹。

`data`文件夹用于放入各种机器模型,my_dog的urdf就在这里。

`robot_lab`文件夹是这里的重点：

- 其中`assets`文件夹用于配置机器人自身的条件，包括urdf的导入，机器人初始姿态的设置，阻尼的设置，重力的设置，电机的功率等等。（细节已经在文件中标出）
- `tasks`是用于配置训练环境及注册的，包含了多种学习环境，有模仿动作的配置，学习行走的配置等等。

  目前只要聚焦于`tasks/manager_based/locomotion/velocity`文件即可。
- `velocity`文件夹含有`config`和`mdp`两个文件。`config`装有具体机器模型的环境配置。
- `my_dog`的环境配置就在`config/quadruped/my_dog`中，主要有平地环境和复杂环境，通过调用mdp文件夹中的文件实现；环境注册文件也在这里`__init__.py`。
- `mdp`文件包含了各种观测方法，奖励函数，课程学习等等(功能注释在文件开头)。

截至2026年3月17日，rsl_rl最新版本为5.0.1,对配置文件格式要求有较大调整，但是robot_lab作者目前还未进行适配，下面暂时适配方案。

幸运的是，IsaacLab 提供了已弃用的 rsl-rl 版本处理程序和函数，我们可以直接使用它。

三`handle_deprecated_rsl_rl_cfg `

https://github.com/isaac-sim/IsaacLab/issues/2180 (train.py适配方案)

https://x.com/i/grok/share/c2007d4bcfaf444aaae1016c50833284（play.py适配方案，需要先进行与train.py相同的操作）

#### 新增功能

* [play.py](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)

1. [--dump\_motor\_csv](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)

* 开启电机数据导出。

2. [--dump\_motor\_interval](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)

* 每隔多少个控制步采样一次（默认 1）。

3. [--dump\_motor\_env\_id](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)

* 多环境时导出哪个环境编号的数据（默认 0）。

新增了电机数据绘图脚本：

* python scripts/tools/visualize_motor_trace.py --csv logs/rsl_rl/my_dog_flat/日期/motor_trace.csv
