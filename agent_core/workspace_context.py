"""Workspace context — per-user filesystem isolation via contextvars.

Tool handlers cannot accept workspace_id in their signatures (the LLM doesn't know
about multi-tenancy).  Python's contextvars module propagates through asyncio
coroutine chains automatically, so we set the context once in the agent thread
and all tool handlers inherit it.
"""
import contextvars
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Callable, Any, Awaitable


@dataclass(frozen=True)
class WorkspacePaths:
    """Per-workspace directory layout."""
    workspace_id: str
    workspace_dir: Path          # workspace/{ws_id}/
    charts_dir: Path
    data_dir: Path
    scripts_dir: Path
    experiments_dir: Path
    papers_dir: Path
    iteration_log: Path          # workspace/{ws_id}/experiments/iteration_log.jsonl


# ── Context variables (set once per agent thread, inherited by all handlers) ──

_ws_paths_var: contextvars.ContextVar[Optional[WorkspacePaths]] = \
    contextvars.ContextVar('workspace_paths', default=None)

# Optional async callback for DB writes from tool handlers (experiment records)
_db_writer_var: contextvars.ContextVar[Optional[Callable[..., Awaitable[Any]]]] = \
    contextvars.ContextVar('db_writer', default=None)


def set_workspace_paths(paths: WorkspacePaths) -> None:
    """Set the workspace paths for the current agent context."""
    _ws_paths_var.set(paths)


def get_workspace_paths() -> WorkspacePaths:
    """Get workspace paths. Must be called within an agent run (context set)."""
    p = _ws_paths_var.get()
    if p is None:
        raise RuntimeError(
            "WorkspacePaths not set — must be called within an active agent run. "
            "Call set_workspace_paths() before invoking tool handlers."
        )
    return p


def set_db_writer(writer: Callable[..., Awaitable[Any]]) -> None:
    """Set the DB writer callback for experiment record persistence."""
    _db_writer_var.set(writer)


def get_db_writer() -> Optional[Callable[..., Awaitable[Any]]]:
    """Get the DB writer callback, if set."""
    return _db_writer_var.get()


def build_workspace_paths(workspace_id: str, base_dir: Path) -> WorkspacePaths:
    """Create a WorkspacePaths for the given workspace, creating directories on disk.

    Args:
        workspace_id: The workspace UUID string.
        base_dir: Project root (contains the workspace/ directory).

    Returns:
        WorkspacePaths with all subdirectories created.
    """
    ws_dir = base_dir / "workspace" / workspace_id
    charts = ws_dir / "charts"
    data = ws_dir / "data"
    scripts = ws_dir / "scripts"
    experiments = ws_dir / "experiments"
    papers = ws_dir / "papers"

    for d in (charts, data, scripts, experiments, papers):
        d.mkdir(parents=True, exist_ok=True)

    return WorkspacePaths(
        workspace_id=workspace_id,
        workspace_dir=ws_dir,
        charts_dir=charts,
        data_dir=data,
        scripts_dir=scripts,
        experiments_dir=experiments,
        papers_dir=papers,
        iteration_log=experiments / "iteration_log.jsonl",
    )
