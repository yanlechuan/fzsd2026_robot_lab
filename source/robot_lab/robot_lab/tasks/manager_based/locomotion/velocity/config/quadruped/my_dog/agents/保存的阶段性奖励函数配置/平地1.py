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
        self.actions.joint_pos.scale = {".*_hip_joint": 0.125, "^(?!.*_hip_joint).*": 0.25}  # 含义：各关节动作缩放；目标趋势：髋关节更保守、其余关节保持足够驱动。
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
        self.events.randomize_reset_joints.params = {
            "position_range": (0.9, 1.1),  # 含义：重置时关节初始位置缩放随机范围；目标趋势：在默认姿态附近注入扰动提升鲁棒性。
            "velocity_range": (0.0, 0.0),  # 含义：重置时关节初始速度范围；目标趋势：保持零初速，避免额外不稳定因素。
        }
        self.events.randomize_rigid_body_mass_base.params["asset_cfg"].body_names = [self.base_link_name]  # 含义：基座质量随机化作用体；目标趋势：仅在基座注入质量不确定性。
        self.events.randomize_rigid_body_mass_others.params["asset_cfg"].body_names = [
            f"^(?!.*{self.base_link_name}).*"
        ]  # 含义：非基座质量随机化作用体；目标趋势：其余刚体进行比例缩放随机化。
        self.events.randomize_com_positions.params["asset_cfg"].body_names = [self.base_link_name]  # 含义：质心随机化作用体；目标趋势：仅扰动基座质心。
        self.events.randomize_apply_external_force_torque.params["asset_cfg"].body_names = [self.base_link_name]  # 含义：外力外矩作用体；目标趋势：冲击集中在基座以考验姿态稳定。
        self.events.randomize_actuator_gains = None  # ActuatorNet 不使用 stiffness/damping，关闭该随机化项。
        self.events.randomize_rigid_body_mass_base.mode = "startup"
        self.events.randomize_rigid_body_mass_others.mode = "startup"
        self.events.randomize_com_positions.params["com_range"]["x"] = (-0.03, 0.03)
        self.events.randomize_com_positions.params["com_range"]["y"] = (-0.03, 0.03)
        self.events.randomize_com_positions.params["com_range"]["z"] = (-0.02, 0.02)
        self.events.randomize_apply_external_force_torque.params["force_range"] = (-15.0, 15.0)
        self.events.randomize_apply_external_force_torque.params["torque_range"] = (-15.0, 15.0)
        self.events.randomize_push_robot.interval_range_s = (10.0, 15.0)
        ''' # 角速度噪声 (rad/s)
        if getattr(self.observations.policy, "base_ang_vel", None) is not None:
            self.observations.policy.base_ang_vel.noise = {
                "func": "isaaclab.utils.noise.noise_model:uniform_noise",
                "operation": "add",
                "n_min": -0.03,
                "n_max":  0.03,
            }

        # 线加速度噪声 (m/s^2)
        if getattr(self.observations.policy, "base_lin_acc", None) is not None:
            self.observations.policy.base_lin_acc.noise = {
                "func": "isaaclab.utils.noise.noise_model:uniform_noise",
                "operation": "add",
                "n_min": -0.15,
                "n_max":  0.15,
            }
        '''
        # ------------------------------Rewards------------------------------ 奖励配置
        # General 通用奖励配置
        self.rewards.is_terminated.weight = 0  # 含义：终止惩罚权重；目标趋势：关闭该项避免与其他惩罚重复。

        # Root penalties 根部惩罚
        self.rewards.lin_vel_z_l2.weight = -2.0  # 含义：机体 z 向速度惩罚；目标趋势：抑制跳动和竖向晃动。
        self.rewards.ang_vel_xy_l2.weight = -0.05  # 含义：机体横滚/俯仰角速度惩罚；目标趋势：减小侧翻倾向。
        self.rewards.flat_orientation_l2.weight = -2.0  # 含义：机体水平姿态惩罚权重；目标趋势：关闭该项并由其他稳定项约束。
        self.rewards.base_height_l2.weight = -15.0  # 含义：机体高度偏差惩罚；目标趋势：贴近目标高度 0.28。
        self.rewards.base_height_l2.params["sensor_cfg"] = None  # 含义：高度项传感器配置；目标趋势：使用无传感器版本计算。
        self.rewards.base_height_l2.params["target_height"] = 0.32 # 含义：目标机身高度；目标趋势：稳定在 0.28m 附近。
        self.rewards.base_height_l2.params["asset_cfg"].body_names = [self.base_link_name]  # 含义：高度项作用刚体；目标趋势：仅约束基座高度。
        self.rewards.body_lin_acc_l2.weight = 0  # 含义：机体线加速度惩罚权重；目标趋势：关闭该项避免过强抑制动作。
        self.rewards.body_lin_acc_l2.params["asset_cfg"].body_names = [self.base_link_name]  # 含义：线加速度项作用刚体；目标趋势：仅基座参与。

        # Joint penalties 关节惩罚
        self.rewards.joint_torques_l2.weight = -2.5e-5  # 含义：关节力矩惩罚；目标趋势：限制能耗与过猛驱动。
        self.rewards.joint_vel_l2.weight = 0  # 含义：关节速度惩罚权重；目标趋势：暂时关闭避免与任务速度冲突。
        self.rewards.joint_acc_l2.weight = -2.5e-7  # 含义：关节加速度惩罚；目标趋势：轻度平滑动作。
        # self.rewards.create_joint_deviation_l1_rewterm("joint_deviation_hip_l1", -0.2, [".*_hip_joint"]) # 关节偏离惩罚，仅针对hip关节，原为-0.2
        self.rewards.joint_pos_limits.weight = -5.0  # 含义：关节位置越界惩罚；目标趋势：强约束不触碰极限。
        self.rewards.joint_vel_limits.weight = 0  # 含义：关节速度越界惩罚权重；目标趋势：关闭硬惩罚避免过度束缚。
        self.rewards.joint_power.weight = -2e-5  # 含义：关节功率惩罚；目标趋势：降低高功率持续输出。
        self.rewards.stand_still.weight = -5  # 含义：零指令下静止约束惩罚；目标趋势：减少无指令抖动。
        self.rewards.joint_pos_penalty.weight = -2.0  # 含义：关节姿态偏离惩罚；目标趋势：收敛到更自然站姿。
        self.rewards.joint_mirror.weight = -0.2  # 含义：对角关节镜像差异惩罚；目标趋势：增强步态左右对称。
        self.rewards.joint_mirror.params["mirror_joints"] = [
            ["FR_(hip|thigh|calf).*", "RL_(hip|thigh|calf).*"],
            ["FL_(hip|thigh|calf).*", "RR_(hip|thigh|calf).*"],
        ]  # 含义：镜像关节配对规则；目标趋势：维持对角腿协同。

        # Action penalties 动作惩罚
        self.rewards.action_rate_l2.weight = -0.08  # 含义：动作变化率惩罚；目标趋势：抑制高频抖动控制。

        # Contact sensor 接触传感器相关奖励
        self.rewards.undesired_contacts.weight = -1.0  # 含义：非足端接触惩罚；目标趋势：减少躯干/腿段碰撞。
        self.rewards.undesired_contacts.params["sensor_cfg"].body_names = [f"^(?!.*{self.foot_link_name}).*"]  # 含义：非期望接触筛选体；目标趋势：排除足端仅惩罚其他刚体。
        self.rewards.contact_forces.weight = -1.5e-4  # 含义：足端接触力惩罚；目标趋势：抑制过大冲击力。
        self.rewards.contact_forces.params["sensor_cfg"].body_names = [self.foot_link_name]  # 含义：接触力项筛选体；目标趋势：仅统计足端接触。

        # Velocity-tracking rewards 速度追踪奖励
        self.rewards.track_lin_vel_xy_exp.weight = 5.0  # 含义：平面线速度跟踪奖励；目标趋势：提高对速度指令跟随度。
        self.rewards.track_ang_vel_z_exp.weight = 3.0  # 含义：偏航角速度跟踪奖励；目标趋势：提高转向跟随度。

        # Others 其他奖励
        self.rewards.feet_air_time.weight = 6.0  # 含义：足端腾空时间奖励；目标趋势：鼓励迈步但避免拖地。
        self.rewards.feet_air_time.params["threshold"] = 0.5  # 含义：腾空判定阈值；目标趋势：保持中等摆动时长。
        self.rewards.feet_air_time.params["sensor_cfg"].body_names = [self.foot_link_name]  # 含义：腾空项统计体；目标趋势：仅统计足端。
        self.rewards.feet_air_time_variance.weight = -1.0  # 含义：各足腾空时间方差惩罚；目标趋势：减小步态不均匀性。
        self.rewards.feet_air_time_variance.params["sensor_cfg"].body_names = [self.foot_link_name]  # 含义：腾空方差项统计体；目标趋势：仅统计足端。
        self.rewards.feet_contact.weight = 0  # 含义：足端接触奖励权重；目标趋势：关闭该项避免重复约束。
        self.rewards.feet_contact.params["sensor_cfg"].body_names = [self.foot_link_name]  # 含义：足端接触项统计体；目标趋势：仅统计足端。
        self.rewards.feet_contact_without_cmd.weight = 0.1  # 含义：无指令时足端接触奖励；目标趋势：增强静止站立稳定性。
        self.rewards.feet_contact_without_cmd.params["sensor_cfg"].body_names = [self.foot_link_name]  # 含义：无指令接触项统计体；目标趋势：仅统计足端。
        self.rewards.feet_stumble.weight = 0  # 含义：绊脚惩罚权重；目标趋势：关闭该项避免过度惩罚探索。
        self.rewards.feet_stumble.params["sensor_cfg"].body_names = [self.foot_link_name]  # 含义：绊脚项统计体；目标趋势：仅统计足端。
        self.rewards.feet_slide.weight = -1.0  # 含义：足端滑移惩罚；目标趋势：降低触地相滑动。
        self.rewards.feet_slide.params["sensor_cfg"].body_names = [self.foot_link_name]  # 含义：滑移项接触统计体；目标趋势：仅统计足端。
        self.rewards.feet_slide.params["asset_cfg"].body_names = [self.foot_link_name]  # 含义：滑移项运动学统计体；目标趋势：仅统计足端。
        self.rewards.feet_height.weight = 0.2  # 含义：足高奖励权重；目标趋势：关闭该项简化目标。
        self.rewards.feet_height.params["asset_cfg"].body_names = [self.foot_link_name]  # 含义：足高项统计体；目标趋势：仅统计足端。
        self.rewards.feet_height_body.weight = -5.0  # 含义：足端相对机体高度惩罚；目标趋势：抑制过高抬腿。
        self.rewards.feet_height_body.params["target_height"] = -0.22 # 含义：足端相对机体目标高度；目标趋势：稳定在 -0.2m 附近。
        self.rewards.feet_height_body.params["asset_cfg"].body_names = [self.foot_link_name]  # 含义：相对足高项统计体；目标趋势：仅统计足端。
        self.rewards.feet_gait.weight = 0.0  # 含义：步态节律奖励；目标趋势：提升对角步态一致性。
        self.rewards.feet_gait.params["synced_feet_pair_names"] = (("FL_calf_link", "RR_calf_link"), ("FR_calf_link", "RL_calf_link"))  # 含义：对角同步足端配对；目标趋势：保持 trot 节律。
        self.rewards.upward.weight = 2.0  # 含义：机体竖直朝上奖励；目标趋势：保持机体正向朝上。
        self.rewards.heading_alignment.weight = -2.0  # 含义：朝向指令对齐惩罚；目标趋势 : 鼓励机体朝向与速度指令一致。
        self.rewards.feet_distance_y_exp.weight = -2.0  # 含义：左右足间距奖励；目标趋势：鼓励适度的站立宽度。
        '''self.rewards.feet_distance_y_exp.params["asset_cfg"].body_names = [self.foot_link_name]  # 含义：滑移项运动学统计体；目标趋势：仅统计足端。
        self.rewards.feet_distance_y_exp.params["stance_width"] = 0.24
        self.rewards.feet_distance_y_exp.params["std"] = 0.08
        self.rewards.base_height_hold_time_bonus.weight = 1.0  # 含义：基座高度保持奖励；目标趋势：奖励持续保持目标高度的时间。
        self.rewards.base_height_hold_time_bonus.params["asset_cfg"].body_names = [self.foot_link_name]  # 含义：滑移项运动学统计体；目标趋势：仅统计足端。
        self.rewards.base_height_hold_time_bonus.params["target_height"] = 0.28  # 含义：基座高度保持目标；目标趋势：与 base_height_l2 目标一致。
        '''
        # If the weight of rewards is 0, set rewards to None #
        if self.__class__.__name__ == "My_dogRoughEnvCfg":
            self.disable_zero_weight_rewards()  # 含义：删除权重为0的奖励项；目标趋势：减少无效计算并保持配置简洁。

        # ------------------------------Terminations------------------------------ 终止条件配置
        self.terminations.illegal_contact.params["sensor_cfg"].body_names = [self.base_link_name, ".*_hip_link",".*_thigh_link"]  # 含义：非法接触终止检测体；目标趋势：重点约束躯干与髋部碰撞。
        # self.terminations.illegal_contact = None

        # ------------------------------Curriculums------------------------------ 课程学习配置
        self.curriculum.terrain_levels = None  # 含义：地形难度课程；目标趋势：平地任务关闭地形课程。
        self.curriculum.command_levels_lin_vel.params["range_multiplier"] = (0.05, 1.5)  # 含义：线速度课程倍率范围；目标趋势：由易到难逐步放宽指令。
        self.curriculum.command_levels_ang_vel.params["range_multiplier"] = (0.05, 1.5)  # 含义：角速度课程倍率范围；目标趋势：由易到难逐步放宽转向。
        # self.curriculum.command_levels_lin_vel = None
        # self.curriculum.command_levels_ang_vel = None

        # ------------------------------Commands------------------------------ 速度指令配置
        # self.commands.base_velocity.ranges.lin_vel_x = (-1.0, 1.0)  # 含义：前后线速度指令范围；目标趋势：覆盖正反向移动。
        # self.commands.base_velocity.ranges.lin_vel_y = (-0.5, 0.5)  # 含义：横向线速度指令范围；目标趋势：适中侧移能力。
        # self.commands.base_velocity.ranges.ang_vel_z = (-1.0, 1.0)  # 含义：偏航角速度指令范围；目标趋势：覆盖双向转向。