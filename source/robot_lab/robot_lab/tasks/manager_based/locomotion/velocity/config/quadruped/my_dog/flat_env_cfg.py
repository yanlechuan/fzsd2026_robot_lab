# Copyright (c) 2024-2026 Ziqi Fan
# SPDX-License-Identifier: Apache-2.0

from isaaclab.utils import configclass

from .rough_env_cfg import My_dogRoughEnvCfg


@configclass
class My_dogFlatEnvCfg(My_dogRoughEnvCfg): # 继承自My_dogRoughEnvCfg，适用于平坦环境的配置类
    def __post_init__(self):
        # post init of parent
        super().__post_init__()

        # override rewards
        self.rewards.base_height_l2.params["sensor_cfg"] = None
        # change terrain to flat using a local USD to avoid online asset dependency
        #local_ground_usd = "/home/ylc/robot_lab/source/robot_lab/data/Assets/Isaac/Props/UIElements/default_environment.usd"
        # self.scene.terrain.usd_path = local_ground_usd
        self.scene.terrain.terrain_type = "plane"  # 使用云端库的地形
        # self.scene.terrain.usd_path = local_ground_usd
        self.scene.terrain.terrain_generator = None
        # no height scan
        self.scene.height_scanner = None
        self.observations.policy.height_scan = None
        self.observations.critic.height_scan = None
        # no terrain curriculum
        self.curriculum.terrain_levels = None
        # terrain_out_of_bounds only supports plane/generator in upstream isaaclab_tasks
        self.terminations.terrain_out_of_bounds = None

        # ------------------------------Rewards (IMU+Motor friendly)------------------------------
        
       

       
        # If the weight of rewards is 0, set rewards to None #
        if self.__class__.__name__ == "My_dogFlatEnvCfg":
            self.disable_zero_weight_rewards()  # 含义：删除权重为0的奖励项；
