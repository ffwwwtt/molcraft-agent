"""科研可视化增强库 —— 供 Agent 在 execute_code 中调用来生成高级图表。

功能:
    - plot_iteration_progress: 迭代指标变化曲线
    - plot_metric_comparison: 多指标对比图
    - plot_ablation_study: 消融实验对比
    - plot_correlation_heatmap: 指标相关性热力图
    - plot_summary_dashboard: 综合仪表盘
"""
import json
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

CHARTS_DIR = Path(__file__).resolve().parent.parent / "workspace" / "charts"
ITERATION_LOG = Path(__file__).resolve().parent.parent / "workspace" / "experiments" / "iteration_log.jsonl"

# === 中文支持 ===
import matplotlib.font_manager as fm

_CHINESE_FONT_FOUND = False
for font_name in ["Microsoft YaHei", "SimHei", "WenQuanYi Micro Hei", "Noto Sans CJK SC"]:
    for f in fm.fontManager.ttflist:
        if font_name in f.name:
            plt.rcParams["font.sans-serif"] = [f.name, "sans-serif"]
            plt.rcParams["axes.unicode_minus"] = False
            _CHINESE_FONT_FOUND = True
            break
    if _CHINESE_FONT_FOUND:
        break
# === 中文支持 ===

plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "figure.dpi": 150,
})


def _load_records() -> list[dict]:
    if not ITERATION_LOG.exists():
        return []
    records = []
    for line in ITERATION_LOG.read_text(encoding="utf-8").strip().split("\n"):
        if line.strip():
            records.append(json.loads(line))
    return records


def plot_iteration_progress(
    metric_name: str,
    title: str = "",
    y_label: str = "",
    filename: str = "",
    lower_is_better: bool = False,
) -> str:
    records = _load_records()
    rounds = []
    values = []

    for rec in records:
        metrics = rec.get("metrics", {})
        val = metrics.get(metric_name)
        if val is not None:
            rounds.append(rec.get("round", 0))
            values.append(float(val))

    if not rounds:
        return ""

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(rounds, values, marker="o", color="#2196F3", linewidth=2, markersize=8)
    ax.set_title(title or f"{metric_name} 迭代趋势")
    ax.set_xlabel("迭代轮次")
    ax.set_ylabel(y_label or metric_name)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.grid(True, alpha=0.3)

    if lower_is_better:
        best_idx = np.argmin(values)
    else:
        best_idx = np.argmax(values)
    ax.annotate(
        f"Best: {values[best_idx]:.4f}",
        xy=(rounds[best_idx], values[best_idx]),
        xytext=(rounds[best_idx], values[best_idx] + (max(values) - min(values)) * 0.15),
        arrowprops=dict(arrowstyle="->", color="#FF5722"),
        fontsize=11,
        fontweight="bold",
        color="#FF5722",
    )

    fig.tight_layout()
    save_path = CHARTS_DIR / (filename or f"progress_{metric_name}.png")
    fig.savefig(str(save_path), bbox_inches="tight")
    plt.close(fig)
    return str(save_path.relative_to(CHARTS_DIR.parent))


def plot_metric_comparison(
    metrics: list[str],
    title: str = "多指标对比",
    filename: str = "metric_comparison.png",
) -> str:
    records = _load_records()

    all_rounds = sorted(set(r.get("round", 0) for r in records if "round" in r))
    data = {m: [] for m in metrics}

    for rnd in all_rounds:
        rnd_recs = [r for r in records if r.get("round") == rnd]
        for m in metrics:
            vals = [float(r["metrics"][m]) for r in rnd_recs if m in r.get("metrics", {})]
            data[m].append(sum(vals) / len(vals) if vals else None)

    fig, axes = plt.subplots(len(metrics), 1, figsize=(10, 4 * len(metrics)), sharex=True)
    if len(metrics) == 1:
        axes = [axes]

    colors = ["#2196F3", "#FF5722", "#4CAF50", "#9C27B0", "#FFC107"]
    for ax, m, c in zip(axes, metrics, colors):
        valid = [(rnd, v) for rnd, v in zip(all_rounds, data[m]) if v is not None]
        if valid:
            rnds, vals = zip(*valid)
            ax.plot(rnds, vals, marker="s", color=c, linewidth=2, markersize=7)
            ax.fill_between(rnds, vals, alpha=0.1, color=c)
        ax.set_ylabel(m)
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    axes[-1].set_xlabel("迭代轮次")
    fig.suptitle(title, fontweight="bold")
    fig.tight_layout()

    save_path = CHARTS_DIR / filename
    fig.savefig(str(save_path), bbox_inches="tight")
    plt.close(fig)
    return str(save_path.relative_to(CHARTS_DIR.parent))


def plot_ablation_study(
    data_file: str,
    baseline_label: str = "Baseline",
    title: str = "消融实验对比",
    filename: str = "ablation_study.png",
) -> str:
    import csv
    rows = list(csv.DictReader(Path(data_file).read_text(encoding="utf-8").splitlines()))
    methods = [r.get("method", f"Exp{i}") for i, r in enumerate(rows)]
    metric_cols = [k for k in rows[0].keys() if k != "method"]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(methods))
    n_metrics = len(metric_cols)
    bar_width = 0.8 / n_metrics
    colors = ["#2196F3", "#FF5722", "#4CAF50", "#9C27B0"]

    for i, col in enumerate(metric_cols):
        vals = [float(r.get(col, 0)) for r in rows]
        ax.bar(x + i * bar_width, vals, bar_width, label=col, color=colors[i % len(colors)])

    ax.set_xticks(x + bar_width * (n_metrics - 1) / 2)
    ax.set_xticklabels(methods, rotation=30, ha="right")
    ax.set_title(title, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
    save_path = CHARTS_DIR / filename
    fig.savefig(str(save_path), bbox_inches="tight")
    plt.close(fig)
    return str(save_path.relative_to(CHARTS_DIR.parent))


def plot_correlation_heatmap(
    data_file: str,
    title: str = "指标相关性热力图",
    filename: str = "correlation_heatmap.png",
) -> str:
    import csv
    rows = list(csv.DictReader(Path(data_file).read_text(encoding="utf-8").splitlines()))
    numeric_cols = []
    data = {}

    for key in rows[0].keys():
        vals = []
        for r in rows:
            try:
                vals.append(float(r[key]))
            except (ValueError, TypeError):
                break
        if len(vals) == len(rows):
            numeric_cols.append(key)
            data[key] = vals

    if len(numeric_cols) < 2:
        return ""

    matrix = np.zeros((len(numeric_cols), len(numeric_cols)))
    for i, c1 in enumerate(numeric_cols):
        for j, c2 in enumerate(numeric_cols):
            matrix[i][j] = np.corrcoef(data[c1], data[c2])[0][1]

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(matrix, cmap="RdYlBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(numeric_cols)))
    ax.set_yticks(range(len(numeric_cols)))
    ax.set_xticklabels(numeric_cols, rotation=45, ha="right")
    ax.set_yticklabels(numeric_cols)
    ax.set_title(title, fontweight="bold")

    for i in range(len(numeric_cols)):
        for j in range(len(numeric_cols)):
            ax.text(j, i, f"{matrix[i][j]:.2f}", ha="center", va="center",
                    fontweight="bold", fontsize=10,
                    color="white" if abs(matrix[i][j]) > 0.5 else "black")

    plt.colorbar(im, ax=ax, label="Pearson r")
    fig.tight_layout()
    save_path = CHARTS_DIR / filename
    fig.savefig(str(save_path), bbox_inches="tight")
    plt.close(fig)
    return str(save_path.relative_to(CHARTS_DIR.parent))


def plot_summary_dashboard(filename: str = "experiment_dashboard.png") -> str:
    records = _load_records()
    if not records:
        return ""

    all_metrics = set()
    for r in records:
        all_metrics.update(r.get("metrics", {}).keys())

    if not all_metrics:
        return ""

    successes = sum(1 for r in records if r.get("success") is True)
    fails = sum(1 for r in records if r.get("success") is False)

    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)

    ax_pie = fig.add_subplot(gs[0, 0])
    labels = ["验证通过", "验证驳回"]
    vals = [successes, fails]
    colors_pie = ["#4CAF50", "#FF5722"]
    ax_pie.pie(vals, labels=labels, autopct="%1.1f%%", colors=colors_pie, startangle=90)
    ax_pie.set_title("假设验证结果", fontweight="bold")

    ax_bars = fig.add_subplot(gs[0, 1])
    valid_metrics = []
    for m in sorted(all_metrics):
        history = []
        for rec in records:
            if m in rec.get("metrics", {}):
                history.append((rec.get("round", 0), float(rec["metrics"][m])))
        if history:
            valid_metrics.append(m)
    values = [float(records[-1].get("metrics", {}).get(m, 0)) for m in valid_metrics]
    ax_bars.bar(valid_metrics, values, color="#2196F3")
    ax_bars.set_title("最新指标值", fontweight="bold")
    ax_bars.tick_params(axis="x", rotation=30)

    ax_timeline = fig.add_subplot(gs[1, :])
    rounds_data = {}
    for rec in records:
        rnd = rec.get("round", 0)
        if rnd not in rounds_data:
            rounds_data[rnd] = {"start": rec.get("timestamp", ""), "success": rec.get("success")}
    rnds = sorted(rounds_data.keys())
    if rnds:
        y_pos = [1] * len(rnds)
        colors_tl = ["#4CAF50" if rounds_data[r].get("success") else "#FF5722" for r in rnds]
        ax_timeline.scatter(rnds, y_pos, c=colors_tl, s=200, zorder=5)
        for r in rnds:
            ax_timeline.annotate(
                f"R{r}",
                (r, 1),
                textcoords="offset points",
                xytext=(0, 15),
                ha="center",
                fontweight="bold",
            )
        ax_timeline.set_ylim(0, 2)
        ax_timeline.set_yticks([])
        ax_timeline.set_title("迭代时间线 (绿色=通过, 红色=驳回)", fontweight="bold")
        ax_timeline.set_xlabel("迭代轮次")
        ax_timeline.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    fig.suptitle("实验综合仪表盘", fontsize=16, fontweight="bold")
    save_path = CHARTS_DIR / filename
    fig.savefig(str(save_path), bbox_inches="tight")
    plt.close(fig)
    return str(save_path.relative_to(CHARTS_DIR.parent))