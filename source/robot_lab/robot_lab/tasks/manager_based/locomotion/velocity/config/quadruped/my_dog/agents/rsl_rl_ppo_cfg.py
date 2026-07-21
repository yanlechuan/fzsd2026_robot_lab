# Copyright (c) 2024-2026 Ziqi Fan
# SPDX-License-Identifier: Apache-2.0

from isaaclab.utils import configclass

from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg, RslRlPpoAlgorithmCfg


@configclass
class My_dogRoughPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 24 #每个环境交互多少步后进行一次更新
    max_iterations = 2000000000 #训练轮数
    save_interval = 100 #每隔多少轮保存一次模型
    experiment_name = "my_dog_rough" #实验名称，用于保存模型和日志
    policy = RslRlPpoActorCriticCfg(
        init_noise_std=1.0, #初始动作噪声标准差
        actor_obs_normalization=True, #是否对actor的观察进行归一化 （与 flat checkpoint 对齐）
        critic_obs_normalization=True,#是否对critic的观察进行归一化 （与 flat checkpoint 对齐）
        actor_hidden_dims=[512, 256, 128], #actor网络隐藏层维度 
        critic_hidden_dims=[512, 256, 128], #critic网络隐藏层维度
        activation="elu", #actor和critic网络的激活函数
    )
    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=1.0, #critic损失的权重 
        use_clipped_value_loss=True, #是否使用clip的critic损失
        clip_param=0.2, #ppo的clip参数epsilon
        entropy_coef=0.01, #熵损失的权重
        num_learning_epochs=5,#每次更新的学习轮数 
        num_mini_batches=4, #每次更新的mini-batch数量
        learning_rate=1.0e-3, #学习率
        schedule="adaptive", #学习率调度方式，"adaptive"表示根据KL散度自动调整
        gamma=0.99, #折扣因子
        lam=0.95, #GAE的lambda参数
        desired_kl=0.01, #自适应学习率调度中期望的KL散度
        max_grad_norm=1.0, #梯度裁剪的最大范数
    )


@configclass
class My_dogFlatPPORunnerCfg(My_dogRoughPPORunnerCfg):
    def __post_init__(self):
        super().__post_init__()

        self.num_steps_per_env = 32 #平地任务每次更新使用更长rollout，降低梯度方差
        self.max_iterations = 20000 #平地任务通常更快收敛，避免超长训练
        self.save_interval = 50 #更频繁保存，便于挑选最佳checkpoint
        self.experiment_name = "my_dog_flat" #实验名称，用于保存模型和日志
        self.policy.init_noise_std = 0.8
        self.policy.actor_obs_normalization = True
        self.policy.critic_obs_normalization = True
        self.algorithm.learning_rate = 5.0e-4
        self.algorithm.entropy_coef = 0.005


@configclass
class My_dogStairsPPORunnerCfg(My_dogRoughPPORunnerCfg):
    def __post_init__(self):
        super().__post_init__()

        self.experiment_name = "my_dog_stairs" #实验名称，用于保存模型和日志
