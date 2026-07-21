# Copyright (c) 2024-2026 Ziqi Fan
# SPDX-License-Identifier: Apache-2.0

from isaaclab.utils import configclass

from robot_lab.tasks.manager_based.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg

##
# Pre-defined configs
##
# # use cloud assets
# from isaaclab_assets.robots.unitree import UNITREE_GO2_CFG  # isort: skip
# use local assets
#from robot_lab.assets.unitree import UNITREE_GO2_CFG  # isort: skip

#目前这套配置的训练结果是在8000轮左右原地站立抖动很小但是继续训练的话原地站立抖动会增大，向前走时，四肢会往中间收，向后却不会
from robot_lab.assets.my_dog import MY_DOG_CFG 

@configclass
class My_dogRoughEnvCfg(LocomotionVelocityRoughEnvCfg):
    base_link_name = "base_link"  # 含义：机器人基座刚体名；目标趋势：保持固定基座参考点，避免误匹配。
    foot_link_name = ".*_calf_link"  # 含义：足端刚体筛选正则；目标趋势：统一匹配四足末端并提高接触相关项一致性。
    # fmt: off
    joint_names = [
        "FR_hip_joint", "FR_thigh_joint", "FR_calf_joint",
        "FL_hip_joint", "FL_thigh_joint", "FL_calf_joint",
        "RR_hip_joint", "RR_thigh_joint", "RR_calf_joint",
        "RL_hip_joint", "RL_thigh_joint", "RL_calf_joint",
    ]  # 含义：策略观测与动作控制的关节白名单；目标趋势：保持关节顺序稳定，减少训练输入输出漂移。
    # fmt: on  关闭格式化，保持关节名称列表的清晰结构

    def __post_init__(self):
        # post init of parent
        super().__post_init__()

        # ------------------------------Sence------------------------------ 场景配置
        self.scene.robot = MY_DOG_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")  # 含义：机器人资产配置；目标趋势：固定到 my_dog 资产，减少资产差异。
        self.scene.height_scanner.prim_path = "{ENV_REGEX_NS}/Robot/" + self.base_link_name  # 含义：高度扫描器挂载位置；目标趋势：与基座对齐保持坐标一致。
        self.scene.height_scanner_base.prim_path = "{ENV_REGEX_NS}/Robot/" + self.base_link_name  # 含义：基准高度扫描器位置；目标趋势：保持与基座同源参考。
        self.scene.height_scanner = None  # 含义：策略高度扫描观测源；目标趋势：关闭该观测以简化输入。

        # ------------------------------Observations------------------------------ 观测配置
        self.observations.policy.base_lin_vel.scale = 2.0  # 含义：策略端机体线速度缩放；目标趋势：放大有效信号但保持数值稳定。
        self.observations.policy.base_ang_vel.scale = 0.25  # 含义：策略端机体角速度缩放；目标趋势：抑制角速度噪声主导。
        self.observations.policy.joint_pos.scale = 1.0  # 含义：策略端关节位置缩放；目标趋势：保持原量纲便于学习。
        self.observations.policy.joint_vel.scale = 0.05  # 含义：策略端关节速度缩放；目标趋势：降低高频速度抖动影响。
        self.observations.policy.base_lin_vel = None  # 含义：策略端线速度观测项；目标趋势：\
        self.observations.policy.height_scan = None  # 含义：策略端高度扫描观测项；目标趋势：关闭地形高度依赖。
        self.observations.critic.height_scan = None  # 含义：价值网络高度扫描观测项；目标趋势：与策略端一致关闭。
        self.observations.policy.joint_pos.params["asset_cfg"].joint_names = self.joint_names  # 含义：关节位置观测关节集；目标趋势：限定为控制关节集合。
        self.observations.policy.joint_vel.params["asset_cfg"].joint_names = self.joint_names  # 含义：关节速度观测关节集；目标趋势：限定为控制关节集合。

        # ------------------------------Actions------------------------------ 动作配置
        self.actions.joint_pos.scale = {".*_hip_joint": 0.125, "^(?!.*_hip_joint).*": 0.25}  # Sim2Real：减小动作缩放，降低真机噪声敏感度
        self.actions.joint_pos.clip = {".*": (-100.0, 100.0)}  # 含义：动作裁剪范围；目标趋势：保持宽裁剪避免过早饱和。
        self.actions.joint_pos.joint_names = self.joint_names  # 含义：动作生效关节；目标趋势：严格限制到目标关节集。

        # ------------------------------Events------------------------------ 事件配置
        self.events.randomize_reset_base.params = {  # 含义：重置时根状态随机范围；目标趋势：适度随机增强泛化且避免初值过激。
            "pose_range": {
                "x": (-0.5, 0.5),  # 含义：重置位置 x 范围；目标趋势：中等平移扰动。
                "y": (-0.5, 0.5),  # 含义：重置位置 y 范围；目标趋势：中等横向扰动。
                "z": (0.0, 0.2),  # 含义：重置位置 z 范围；目标趋势：固定初始高度。
                "roll": (-0.3, 0.3),  # 含义：重置横滚范围；目标趋势：小角度姿态扰动。
                "pitch": (-0.3, 0.3),  # 含义：重置俯仰范围；目标趋势：小角度姿态扰动。
                "yaw": (-3.14, 3.14),  # 含义：重置偏航范围；目标趋势：全向朝向随机化。
            },
            "velocity_range": {  # 含义：重置线/角速度随机范围；目标趋势：中等速度扰动提升恢复能力。
                "x": (-0.5, 0.5),  # 含义：线速度 x 范围；目标趋势：保持中等前后速度随机。
                "y": (-0.5, 0.5),  # 含义：线速度 y 范围；目标趋势：保持中等横向速度随机。
                "z": (-0.5, 0.5),  # 含义：线速度 z 范围；目标趋势：保留适度竖直扰动。
                "roll": (-0.5, 0.5),  # 含义：角速度 roll 范围；目标趋势：中等滚转角速度扰动。
                "pitch": (-0.5, 0.5),  # 含义：角速度 pitch 范围；目标趋势：中等俯仰角速度扰动。
                "yaw": (-0.5, 0.5),  # 含义：角速度 yaw 范围；目标趋势：中等偏航角速度扰动。
            },
        }  # 含义：reset 根状态随机化配置；目标趋势：维持复现实验所需随机强度。
        #self.events.randomize_reset_joints.params = {
         #   "position_range": (0.9, 1.1),  # 含义：重置时关节初始位置缩放随机范围；目标趋势：在默认姿态附近注入扰动提升鲁棒性。
         #   "velocity_range": (0.0, 0.0),  # 含义：重置时关节初始速度范围；目标趋势：保持零初速，避免额外不稳定因素。
        #}
        self.events.randomize_rigid_body_mass_base.params["asset_cfg"].body_names = [self.base_link_name]
        self.events.randomize_rigid_body_mass_others.params["asset_cfg"].body_names = [f"^(?!.*{self.base_link_name}).*"]
        self.events.randomize_com_positions.params["asset_cfg"].body_names = [self.base_link_name]
        self.events.randomize_apply_external_force_torque.params["asset_cfg"].body_names = [self.base_link_name]
        self.events.randomize_apply_external_force_torque.params["force_range"] = (-10.0, 10.0)
        self.events.randomize_apply_external_force_torque.params["torque_range"] = (-10.0, 10.0)
       

        # ------------------------------Rewards------------------------------ 奖励配置
        # General 通用奖励配置
        self.rewards.is_terminated.weight = 0

        self.rewards.lin_vel_z_l2.weight = -4.0  # 减少起步下沉：加强垂直速度惩罚，抑制突然下蹲
        self.rewards.ang_vel_xy_l2.weight = -0.15  # 减少身体晃动：加强角速度惩罚，抑制身体摇摆
        self.rewards.flat_orientation_l2.weight = -30.0  # 减少身体晃动：加强姿态倾斜惩罚，保持身体水平

        self.rewards.base_height_l2.weight = -50.0  # 减少起步下沉：加强高度保持惩罚
        self.rewards.base_height_l2.params["target_height"] = 0.52
        self.rewards.base_height_l2.params["asset_cfg"].body_names = [self.base_link_name]
        self.rewards.base_height_l2.params["sensor_cfg"] = None

        self.rewards.joint_torques_l2.weight = -2.5e-5
        self.rewards.joint_acc_l2.weight = -2.5e-7
        self.rewards.joint_pos_limits.weight = -5.0
        self.rewards.joint_vel_limits = getattr(self.rewards, "joint_vel_limits", None)
        self.rewards.joint_power.weight = -2.0e-5

        self.rewards.stand_still.weight = -5
        self.rewards.joint_pos_penalty.weight = -2.0
        self.rewards.joint_mirror.weight = -0.2
        self.rewards.joint_mirror.params["mirror_joints"] = [
            ["FR_(hip|thigh|calf).*", "RL_(hip|thigh|calf).*"],
            ["FL_(hip|thigh|calf).*", "RR_(hip|thigh|calf).*"],
        ]

        self.rewards.action_rate_l2.weight = -0.25  # Sim2Real：加强动作平滑惩罚，抑制真机高频抖动

        self.rewards.undesired_contacts.weight = -1.0
        self.rewards.undesired_contacts.params["sensor_cfg"].body_names = [f"^(?!.*{self.foot_link_name}).*"]

        self.rewards.contact_forces.weight = -0.00015
        self.rewards.contact_forces.params["sensor_cfg"].body_names = [self.foot_link_name]

        self.rewards.track_lin_vel_xy_exp.weight = 6.0
        self.rewards.track_ang_vel_z_exp.weight = 3.0

        self.rewards.feet_air_time.weight = 15.0  # 降低步频：鼓励更长的离地时间
        self.rewards.feet_air_time.params["threshold"] = 0.5  # 降低步频：更易达成的离地时间阈值，避免为达标而踮脚快走
        self.rewards.feet_air_time.params["sensor_cfg"].body_names = [self.foot_link_name]

        self.rewards.feet_air_time_variance.weight = -2.0
        self.rewards.feet_air_time_variance.params["sensor_cfg"].body_names = [self.foot_link_name]

        self.rewards.feet_contact_without_cmd.weight = 0.1
        self.rewards.feet_contact_without_cmd.params["sensor_cfg"].body_names = [self.foot_link_name]

        self.rewards.feet_slide.weight = -1.5  # 防止拖地：加强滑足惩罚，抑制支撑相脚在地面拖动
        self.rewards.feet_slide.params["sensor_cfg"].body_names = [self.foot_link_name]
        self.rewards.feet_slide.params["asset_cfg"].body_names = [self.foot_link_name]

        self.rewards.feet_height.weight = 15.0  # 防止拖地：加强抬脚奖励权重
        self.rewards.feet_height.params["asset_cfg"].body_names = [self.foot_link_name]
        self.rewards.feet_height.params["target_height"] = 0.15  # 防止拖地：提高抬脚目标到0.18m

        self.rewards.feet_height_body.weight = -5.0
        self.rewards.feet_height_body.params["target_height"] = -0.24
        self.rewards.feet_height_body.params["asset_cfg"].body_names = [self.foot_link_name]

        self.rewards.upward.weight = 2.0
        self.rewards.heading_alignment.weight = -2.0

        self.rewards.feet_distance_y_exp.weight = 2.0  # 含义：左右足间距奖励；目标趋势：鼓励适度的站立宽度。
        self.rewards.feet_distance_y_exp.params["asset_cfg"].body_names = [self.foot_link_name]  # 含义：滑移项运动学统计体；目标趋势：仅统计足端。
        self.rewards.feet_distance_y_exp.params["stance_width"] = 0.36
        self.rewards.feet_distance_y_exp.params["std"] = 0.08
        #self.rewards.base_height_hold_time_bonus.weight = 1.0  # 含义：基座高度保持奖励；目标趋势：奖励持续保持目标高度的时间。
        #self.rewards.base_height_hold_time_bonus.params["asset_cfg"].body_names = [self.foot_link_name]  # 含义：滑移项运动学统计体；目标趋势：仅统计足端。
        #self.rewards.base_height_hold_time_bonus.params["target_height"] = 0.28  # 含义：基座高度保持目标；目标趋势：与 base_height_l2 目标一致。
        
        # If the weight of rewards is 0, set rewards to None #
        if self.__class__.__name__ == "My_dogRoughEnvCfg":
            self.disable_zero_weight_rewards()  # 含义：删除权重为0的奖励项；目标趋势：减少无效计算并保持配置简洁。

        # ------------------------------Terminations------------------------------ 终止条件配置
        self.terminations.illegal_contact.params["sensor_cfg"].body_names = [self.base_link_name, ".*_hip_link",".*_thigh_link"]  # 含义：非法接触终止检测体；目标趋势：重点约束躯干与髋部碰撞。
        # self.terminations.illegal_contact = None

        # ------------------------------Curriculums------------------------------ 课程学习配置
        self.curriculum.terrain_levels = None  # 含义：地形难度课程；目标趋势：平地任务关闭地形课程。
        self.curriculum.command_levels_lin_vel.params["range_multiplier"] = (0.2, 1.0)  # 含义：线速度课程倍率范围；目标趋势：由易到难逐步放宽指令。
        self.curriculum.command_levels_ang_vel.params["range_multiplier"] = (0.2, 1.0)  # 含义：角速度课程倍率范围；目标趋势：由易到难逐步放宽转向。
        # self.curriculum.command_levels_lin_vel = None
        # self.curriculum.command_levels_ang_vel = None

        # ------------------------------Commands------------------------------ 速度指令配置
        # self.commands.base_velocity.ranges.lin_vel_x = (-1.0, 1.0)  # 含义：前后线速度指令范围；目标趋势：覆盖正反向移动。
        # self.commands.base_velocity.ranges.lin_vel_y = (-0.5, 0.5)  # 含义：横向线速度指令范围；目标趋势：适中侧移能力。
        # self.commands.base_velocity.ranges.ang_vel_z = (-1.0, 1.0)  # 含义：偏航角速度指令范围；目标趋势：覆盖双向转向。