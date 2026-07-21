#!/usr/bin/env python3
"""Verify whether calf-joint spring torque is present in motor telemetry.

The script expects CSV logs produced by ``scripts/reinforcement_learning/rsl_rl/play.py`` with
``--dump_motor_csv`` enabled.

It can:
- plot torque-angle scatter for calf joints
- compare two runs (spring on/off) by plotting both on the same axes
- print a simple linear fit and correlation summary per joint

Expected CSV columns:
step,time_s,env_id,joint,joint_pos_rad,joint_vel_rad_s,joint_vel_rpm,applied_torque_nm,joint_power_w


新增参数：
--speed-threshold
--angle-min
--angle-max
例如：

只放宽速度，不限制角度
python verify_spring_effect.py on.csv off.csv --speed-threshold 0.1
同时放宽速度和角度
python verify_spring_effect.py on.csv off.csv --speed-threshold 0.1 --angle-min -1.5 --angle-max 1.5


"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np

CALF_JOINTS = ["FR_calf_joint", "FL_calf_joint", "RR_calf_joint", "RL_calf_joint"]


@dataclass
class JointSeries:
    pos: list[float]
    torque: list[float]
    vel: list[float]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify spring effect from motor telemetry CSV.")
    parser.add_argument("csv", nargs="+", type=Path, help="One or two motor_trace.csv files")
    parser.add_argument("--env-id", type=int, default=None, help="Only use one env_id from the logs")
    parser.add_argument("--out-dir", type=Path, default=None, help="Output directory for plots")
    parser.add_argument("--show", action="store_true", help="Show plots interactively")
    parser.add_argument("--speed-threshold", type=float, default=0.05, help="Low-speed filter in rad/s")
    parser.add_argument("--angle-min", type=float, default=None, help="Minimum joint angle to keep, in rad")
    parser.add_argument("--angle-max", type=float, default=None, help="Maximum joint angle to keep, in rad")
    return parser.parse_args()


def load_csv(csv_path: Path, env_id: int | None) -> dict[str, JointSeries]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    required_cols = {"env_id", "joint", "applied_torque_nm"}
    optional_pos_cols = ["joint_pos_rad", "joint_pos"]

    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {csv_path}")
        missing = required_cols.difference(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing))}")
        pos_col = next((name for name in optional_pos_cols if name in reader.fieldnames), None)
        if pos_col is None:
            raise ValueError(
                f"CSV must include one of these columns for joint angle: {', '.join(optional_pos_cols)}"
            )

        series: dict[str, JointSeries] = defaultdict(lambda: JointSeries(pos=[], torque=[], vel=[]))
        for row in reader:
            row_env = int(row["env_id"])
            if env_id is not None and row_env != env_id:
                continue
            joint = row["joint"]
            if joint not in CALF_JOINTS:
                continue
            series[joint].pos.append(float(row[pos_col]))
            series[joint].torque.append(float(row["applied_torque_nm"]))
            vel_value = row.get("joint_vel_rad_s", "0.0")
            series[joint].vel.append(float(vel_value))

    if not series:
        raise ValueError(f"No calf-joint rows found in {csv_path}")

    return dict(series)


def low_speed_mask(vel: Iterable[float], threshold: float) -> np.ndarray:
    vel_arr = np.asarray(list(vel), dtype=float)
    return np.abs(vel_arr) < threshold


def angle_mask(pos: Iterable[float], min_angle: float | None, max_angle: float | None) -> np.ndarray:
    pos_arr = np.asarray(list(pos), dtype=float)
    mask = np.ones(pos_arr.shape, dtype=bool)
    if min_angle is not None:
        mask &= pos_arr >= min_angle
    if max_angle is not None:
        mask &= pos_arr <= max_angle
    return mask


def filtered_joint_data(
    series: JointSeries,
    speed_threshold: float,
    angle_min: float | None,
    angle_max: float | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    pos = np.asarray(series.pos, dtype=float)
    torque = np.asarray(series.torque, dtype=float)
    vel = np.asarray(series.vel, dtype=float)
    mask = low_speed_mask(vel, speed_threshold) & angle_mask(pos, angle_min, angle_max)
    return pos[mask], torque[mask], vel[mask]


def linear_fit(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    if x.size < 2:
        return 0.0, float(y.mean()) if y.size else 0.0, float("nan")
    slope, intercept = np.polyfit(x, y, 1)
    y_pred = slope * x + intercept
    ss_res = float(np.sum((y - y_pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0.0 else float("nan")
    return float(slope), float(intercept), r2


def summarize_series(
    name: str,
    series: dict[str, JointSeries],
    speed_threshold: float,
    angle_min: float | None,
    angle_max: float | None,
) -> None:
    print(f"\n[{name}]")
    for joint in CALF_JOINTS:
        if joint not in series:
            continue
        pos, torque, _ = filtered_joint_data(series[joint], speed_threshold, angle_min, angle_max)
        slope, intercept, r2 = linear_fit(pos, torque)
        corr = float(np.corrcoef(pos, torque)[0, 1]) if pos.size > 1 else float("nan")
        print(
            f"  {joint}: low-speed samples={pos.size}, slope={slope:.6f}, intercept={intercept:.6f}, r2={r2:.4f}, corr={corr:.4f}"
        )


def plot_single_run(
    name: str,
    series: dict[str, JointSeries],
    out_dir: Path,
    speed_threshold: float,
    angle_min: float | None,
    angle_max: float | None,
    show: bool,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=False, sharey=False)
    axes = axes.ravel()

    for ax, joint in zip(axes, CALF_JOINTS):
        if joint not in series:
            ax.set_title(f"{name} - {joint} (missing)")
            ax.axis("off")
            continue

        pos, torque, _ = filtered_joint_data(series[joint], speed_threshold, angle_min, angle_max)

        ax.scatter(pos, torque, s=4, alpha=0.35)
        if pos.size >= 2:
            slope, intercept, _ = linear_fit(pos, torque)
            xs = np.linspace(pos.min(), pos.max(), 100)
            ax.plot(xs, slope * xs + intercept, linewidth=2)
        ax.set_title(joint)
        ax.set_xlabel("joint_pos_rad")
        ax.set_ylabel("applied_torque_nm")
        ax.grid(True, alpha=0.25)

    fig.suptitle(f"{name} torque-angle scatter (low-speed filtered)")
    fig.tight_layout()
    out_path = out_dir / f"{name}_torque_angle.png"
    fig.savefig(out_path, dpi=180)
    print(f"Saved: {out_path}")
    if show:
        plt.show()
    plt.close(fig)


def plot_overlay(
    name_a: str,
    series_a: dict[str, JointSeries],
    name_b: str,
    series_b: dict[str, JointSeries],
    out_dir: Path,
    speed_threshold: float,
    angle_min: float | None,
    angle_max: float | None,
    show: bool,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=False, sharey=False)
    axes = axes.ravel()

    for ax, joint in zip(axes, CALF_JOINTS):
        if joint in series_a:
            pos_a, torque_a, _ = filtered_joint_data(series_a[joint], speed_threshold, angle_min, angle_max)
            ax.scatter(pos_a, torque_a, s=4, alpha=0.28, label=name_a)

        if joint in series_b:
            pos_b, torque_b, _ = filtered_joint_data(series_b[joint], speed_threshold, angle_min, angle_max)
            ax.scatter(pos_b, torque_b, s=4, alpha=0.28, label=name_b)

        ax.set_title(joint)
        ax.set_xlabel("joint_pos_rad")
        ax.set_ylabel("applied_torque_nm")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="best")

    fig.suptitle("Torque-angle comparison (low-speed filtered)")
    fig.tight_layout()
    out_path = out_dir / "overlay_torque_angle.png"
    fig.savefig(out_path, dpi=180)
    print(f"Saved: {out_path}")
    if show:
        plt.show()
    plt.close(fig)


def main() -> None:
    args = parse_args()
    csv_paths = [path.resolve() for path in args.csv]
    if len(csv_paths) > 2:
        raise ValueError("Pass at most two CSV files")

    out_dir = args.out_dir.resolve() if args.out_dir else csv_paths[0].parent / "spring_verification"
    out_dir.mkdir(parents=True, exist_ok=True)

    series_list = [load_csv(path, args.env_id) for path in csv_paths]
    names = [path.stem for path in csv_paths]

    for name, series in zip(names, series_list):
        summarize_series(name, series, args.speed_threshold, args.angle_min, args.angle_max)
        plot_single_run(
            name,
            series,
            out_dir,
            args.speed_threshold,
            args.angle_min,
            args.angle_max,
            args.show,
        )

    if len(series_list) == 2:
        plot_overlay(
            names[0],
            series_list[0],
            names[1],
            series_list[1],
            out_dir,
            args.speed_threshold,
            args.angle_min,
            args.angle_max,
            args.show,
        )

    print(f"Outputs written to: {out_dir}")


if __name__ == "__main__":
    main()
