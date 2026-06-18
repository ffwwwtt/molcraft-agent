"""增强实验记录模块 —— 历史对比、最佳追踪、趋势分析。

每次 record_experiment 和 report_iteration 调用都会追加到
workspace/{ws_id}/experiments/iteration_log.jsonl。本模块提供读取和分析能力。

All read functions accept an optional `iteration_log_path` parameter.
If not provided, falls back to the workspace context (contextvars).
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _resolve_path(iteration_log_path: Optional[Path] = None) -> Path:
    """Resolve the iteration log path. Uses contextvar as fallback."""
    if iteration_log_path is not None:
        return iteration_log_path
    from agent_core.workspace_context import get_workspace_paths
    return get_workspace_paths().iteration_log


def get_all_records(iteration_log_path: Optional[Path] = None) -> list[dict]:
    path = _resolve_path(iteration_log_path)
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").strip().split("\n"):
        if line.strip():
            records.append(json.loads(line))
    return records


def get_latest_round(iteration_log_path: Optional[Path] = None) -> int:
    records = get_all_records(iteration_log_path)
    rounds = [r.get("round", 0) for r in records if "round" in r]
    return max(rounds) if rounds else 0


def get_best_metrics(metric_name: str, lower_is_better: bool = False,
                     iteration_log_path: Optional[Path] = None) -> Optional[dict]:
    records = get_all_records(iteration_log_path)
    best = None
    best_val = float("inf") if lower_is_better else float("-inf")

    for rec in records:
        metrics = rec.get("metrics", {})
        val = metrics.get(metric_name)
        if val is None:
            continue
        if lower_is_better and val < best_val:
            best_val = val
            best = rec
        elif not lower_is_better and val > best_val:
            best_val = val
            best = rec

    if best:
        return {
            "round": best.get("round"),
            "metric_value": best_val,
            "hypothesis": best.get("hypothesis", ""),
            "conclusion": best.get("conclusion", ""),
        }
    return None


def get_metric_history(metric_name: str, iteration_log_path: Optional[Path] = None) -> list[dict]:
    records = get_all_records(iteration_log_path)
    history = []
    for rec in records:
        metrics = rec.get("metrics", {})
        val = metrics.get(metric_name)
        if val is not None:
            history.append({
                "round": rec.get("round"),
                "timestamp": rec.get("timestamp", ""),
                "value": val,
            })
    return sorted(history, key=lambda x: x["round"])


def get_trend_summary(iteration_log_path: Optional[Path] = None) -> dict:
    records = get_all_records(iteration_log_path)
    if not records:
        return {"total_records": 0, "total_rounds": 0, "metrics_tracked": []}

    all_metrics = set()
    for rec in records:
        m = rec.get("metrics", {})
        if isinstance(m, str):
            try:
                m = json.loads(m)
            except json.JSONDecodeError:
                m = {}
        all_metrics.update(m.keys())

    rounds = sorted(set(r.get("round", 0) for r in records if "round" in r))

    metric_trends = {}
    for metric in all_metrics:
        history = []
        for rnd in rounds:
            rnd_records = [r for r in records if r.get("round") == rnd]
            values = [
                r["metrics"][metric]
                for r in rnd_records
                if metric in r.get("metrics", {})
            ]
            if values:
                numeric = []
                for v in values:
                    try:
                        numeric.append(float(v))
                    except (ValueError, TypeError):
                        pass
                if numeric:
                    history.append({"round": rnd, "avg": sum(numeric) / len(numeric), "best": min(numeric)})
        if history:
            metric_trends[metric] = history

    successful = sum(1 for r in records if r.get("success") is True)
    failed = sum(1 for r in records if r.get("success") is False)

    return {
        "total_records": len(records),
        "total_rounds": len(rounds),
        "rounds_completed": rounds,
        "hypotheses_tested": successful + failed,
        "hypotheses_confirmed": successful,
        "hypotheses_rejected": failed,
        "metrics_tracked": sorted(all_metrics),
        "trends": metric_trends,
    }


def export_summary_markdown(iteration_log_path: Optional[Path] = None) -> str:
    summary = get_trend_summary(iteration_log_path)
    lines = [
        "# 实验总结报告",
        "",
        f"生成时间: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"## 总体统计",
        f"- 总记录数: {summary['total_records']}",
        f"- 完成轮次: {summary['total_rounds']}",
        f"- 验证假设: {summary['hypotheses_confirmed']} 通过 | {summary['hypotheses_rejected']} 驳回",
        f"- 追踪指标: {', '.join(summary['metrics_tracked']) if summary['metrics_tracked'] else '无'}",
        "",
    ]

    if summary["trends"]:
        lines.append("## 各指标趋势")
        for metric, trend in summary["trends"].items():
            lines.append(f"\n### {metric}")
            lines.append("| 轮次 | 平均值 | 最佳值 |")
            lines.append("|------|--------|--------|")
            for point in trend:
                lines.append(f"| {point['round']} | {point['avg']:.4f} | {point['best']:.4f} |")

    lines.append("")
    lines.append("## 实验记录详情")
    for rec in get_all_records(iteration_log_path):
        lines.append(f"\n### 第 {rec.get('round', '?')} 轮 — {rec.get('hypothesis_id', '')}")
        lines.append(f"- 假设: {rec.get('hypothesis', 'N/A')}")
        lines.append(f"- 结论: {rec.get('conclusion', 'N/A')}")
        lines.append(f"- 验证: {'✅ 成立' if rec.get('success') else '❌ 驳回'}")
        if rec.get("metrics"):
            lines.append(f"- 指标: {json.dumps(rec['metrics'], ensure_ascii=False)}")

    return "\n".join(lines)


def clear_all_records(iteration_log_path: Optional[Path] = None) -> None:
    """Clear all experiment records."""
    path = _resolve_path(iteration_log_path)
    if path.exists():
        path.write_text("", encoding="utf-8")


# ── DB-backed access (used by API layer for fast queries) ──

async def get_records_from_db(db, workspace_id: str) -> dict:
    """Read experiment records from the ExperimentRecord table (authoritative source).

    Returns the same shape as get_trend_summary + records list for API responses.
    """
    from sqlalchemy import select
    from server.models.experiment import ExperimentRecord

    result = await db.execute(
        select(ExperimentRecord)
        .where(ExperimentRecord.workspace_id == workspace_id)
        .order_by(ExperimentRecord.round_num)
    )
    records = result.scalars().all()

    items = []
    for rec in records:
        items.append({
            "id": rec.id,
            "round": rec.round_num,
            "hypothesis": rec.hypothesis or "",
            "method": rec.method or "",
            "conclusion": rec.conclusion or "",
            "success": rec.success,
            "confirmed": rec.success,
            "metrics": rec.metrics or {},
            "chart_files": rec.chart_files or [],
            "goal": rec.hypothesis or "",
            "iteration": f"Round {rec.round_num}",
            "timestamp": rec.created_at.isoformat() if rec.created_at else "",
            "summary": rec.conclusion or "",
        })

    confirmed = sum(1 for r in records if r.success is True)
    rejected = sum(1 for r in records if r.success is False)

    return {
        "records": items,
        "summary": {"total": len(records), "confirmed": confirmed, "rejected": rejected},
    }
