# Copyright (c) 2024-2026 Ziqi Fan
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass

import cusrl
from cusrl.environment.isaaclab import TrainerCfg


@dataclass
class My_dogRoughTrainerCfg(TrainerCfg):
    max_iterations = 200000 #训练轮数
    save_interval = 100 # 每隔多少轮保存一次模型
    experiment_name = "my_dog_rough" #实验名称，用于保存模型和日志
    agent_factory = cusrl.ActorCritic.Factory( 
        num_steps_per_update=24, #每个环境交互多少步后进行一次更新
        actor_factory=cusrl.Actor.Factory( 
            backbone_factory=cusrl.Mlp.Factory(
                hidden_dims=[512, 256, 128], activation_fn="ELU", ends_with_activation=True
            ), #actor网络的隐藏层维度和激活函数
            distribution_factory=cusrl.NormalDist.Factory(), #动作分布，这里使用正态分布
        ),
        critic_factory=cusrl.Value.Factory(
            backbone_factory=cusrl.Mlp.Factory( 
                hidden_dims=[512, 256, 128], activation_fn="ELU", ends_with_activation=True # critic网络的隐藏层维度和激活函数
            ),
        ),
        optimizer_factory=cusrl.OptimizerFactory("AdamW", defaults={"lr": 1.0e-3}),
        sampler=cusrl.AutoMiniBatchSampler(num_epochs=5, num_mini_batches=4),
        hooks=[ #训练过程中使用的hook列表
            cusrl.hook.ValueComputation(), #计算critic的值函数 
            cusrl.hook.GeneralizedAdvantageEstimation(gamma=0.99, lamda=0.95), #GAE优势估计，gamma是折扣因子，lamda是偏差-方差权衡参数
            cusrl.hook.AdvantageNormalization(), #对优势进行归一化，通常可以提高训练稳定性
            cusrl.hook.ValueLoss(), #计算critic的损失 
            cusrl.hook.OnPolicyPreparation(), #在每次更新前进行的准备工作，如清空经验缓存等
            cusrl.hook.PpoSurrogateLoss(), #计算PPO的surrogate损失，包括clip损失和熵损失
            cusrl.hook.EntropyLoss(weight=0.008), #计算熵损失，weight是熵损失的权重，鼓励策略探索
            cusrl.hook.GradientClipping(max_grad_norm=1.0), #梯度裁剪，max_grad_norm是最大梯度范数，防止梯度爆炸
            cusrl.hook.OnPolicyStatistics(sampler=cusrl.AutoMiniBatchSampler()), #计算和记录训练统计数据，如平均奖励、损失等
            cusrl.hook.AdaptiveLRSchedule(desired_kl_divergence=0.01), #自适应学习率调度，根据KL散度调整学习率，desired_kl_divergence是期望的KL散度值
        ],
    )


@dataclass
class My_dogFlatTrainerCfg(My_dogRoughTrainerCfg):
    max_iterations = 5000 #训练轮数
    experiment_name = "my_dog_flat" #实验名称，用于保存模型和日志


@dataclass
class My_dogStairsTrainerCfg(My_dogRoughTrainerCfg):
    experiment_name = "my_dog_stairs" #实验名称，用于保存模型和日志