import asyncio, json, os, sys, time, threading, uuid, uvicorn
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*loop_writing.*')
from datetime import datetime, timezone
from pathlib import Path
from contextlib import asynccontextmanager
from io import StringIO

# Load .env before importing other modules
from dotenv import load_dotenv
_ENV_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_ENV_DIR / '.env')

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

BASE_DIR = _ENV_DIR
sys.path.insert(0, str(BASE_DIR))

from agent_core.engine import ResearchAgent
from agent_core.tools import OPENAI_TOOLS, TOOL_HANDLERS
from agent_core.experiments import (
    get_all_records, get_trend_summary,
    export_summary_markdown, clear_all_records,
)

from server.database import get_db, init_db, DB_FILE
from server.models.user import User
from server.models.workspace import Workspace
from server.models.conversation import Conversation, ConversationLog
from server.models.experiment import ExperimentRecord
from server.auth import create_access_token, decode_token, get_user_by_id
from server.dependencies import get_current_user, get_current_user_ws, get_optional_user
from server.schemas import ConfigUpdate, AgentStartRequest
from server.routers.auth import router as auth_router
from server.encryption import encrypt, decrypt

# ── Paths ──

STATIC_DIR = BASE_DIR / 'server' / 'static'
WORKSPACE_DIR = BASE_DIR / 'workspace'


def _workspace_dir(workspace_id: str, subdir: str = "") -> Path:
    """Return the per-workspace directory path, creating it if needed."""
    p = WORKSPACE_DIR / workspace_id
    if subdir:
        p = p / subdir
    p.mkdir(parents=True, exist_ok=True)
    return p

# ── Per-workspace runtime state (replaces global agent_state) ──
# In production Phase 2+, this moves to Redis
_workspace_state: dict[str, dict] = {}  # workspace_id -> {running, stop, ws_connections[], ...}


def _get_ws_state(workspace_id: str) -> dict:
    if workspace_id not in _workspace_state:
        _workspace_state[workspace_id] = {
            "running": False,
            "stop": False,
            "stopped_by_user": False,
            "ws_connections": [],
            "current_iteration": 0,
            "total_iterations": 0,
        }
    return _workspace_state[workspace_id]


# ── Model pricing ──

MODEL_PRICING = {
    "gpt-5.5": (5.00, 30.00), "gpt-5.4": (2.50, 15.00), "gpt-5.4-mini": (0.25, 2.00),
    "gpt-4.1": (2.00, 8.00), "gpt-4.1-mini": (0.40, 1.60), "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60), "gpt-4-turbo": (10.00, 30.00), "gpt-4": (30.00, 60.00),
    "gpt-3.5-turbo": (0.50, 1.50), "o4-mini": (1.10, 4.40), "o3-mini": (1.10, 4.40),
    "deepseek-v4-flash": (0.14, 0.28), "deepseek-v4-pro": (0.44, 0.87),
    "deepseek-chat": (0.14, 0.28), "deepseek-reasoner": (0.14, 0.28),
    "deepseek-v3": (0.14, 0.28), "deepseek-r1": (0.55, 2.19),
    "qwen3.7-max": (2.50, 7.50), "qwen3.6-plus": (0.50, 3.00),
    "qwen3.6-flash": (0.10, 0.40), "qwen-plus": (0.80, 3.20), "qwen-max": (2.50, 7.50),
    "qwen-flash": (0.10, 0.40), "qwen-turbo": (0.30, 1.20),
    "kimi-k2.6": (0.95, 4.00), "moonshot-v1-8k": (1.00, 1.00),
    "moonshot-v1-32k": (2.00, 2.00), "moonshot-v1-128k": (5.00, 5.00),
    "glm-5.1": (1.26, 3.96), "glm-5": (0.80, 2.40), "glm-4.7": (0.54, 1.98),
    "glm-4-plus": (1.00, 1.00), "glm-4-flash": (0, 0),
    "claude-sonnet-4": (3.00, 15.00), "claude-sonnet-4-6": (3.00, 15.00),
    "claude-opus-4-7": (5.00, 25.00), "claude-opus-4-8": (5.00, 25.00),
    "claude-3.5": (3.00, 15.00), "claude-sonnet": (3.00, 15.00), "claude-opus": (15.00, 75.00),
    "gemini-2.5-flash": (0.30, 2.50), "gemini-2.5-pro": (1.25, 10.00), "gemini": (1.25, 5.00),
}


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int):
    model_lower = model.lower()
    for key, (in_price, out_price) in sorted(MODEL_PRICING.items(), key=lambda x: -len(x[0])):
        if key in model_lower:
            return round((prompt_tokens / 1_000_000) * in_price + (completion_tokens / 1_000_000) * out_price, 6), True
    return 0.0, False


# ── Default system prompt ──

DEFAULT_SYSTEM_PROMPT = (
    "You are a scientific research agent. Your workspace is organized as follows:\n"
    "  data/     - CSV, JSON, PDF, DOCX, PPTX, XLSX, audio, images, and other raw data files\n"
    "  scripts/  - Python scripts generated during experiments\n"
    "  charts/   - PNG chart images (save with plt.savefig('charts/xxx.png'))\n"
    "  experiments/ - Experiment trace logs (.jsonl, .log)\n"
    "  papers/   - Generated research papers (.md, .docx)\n"
    "\n"
    "FILE READING: read_file supports 20+ formats (PDF/DOCX/PPTX/XLSX/EPUB/CSV/HTML/JSON/\n"
    "  images/audio/plain text). You can explore and read files from ANY folder — the\n"
    "  workspace root contains all uploaded files. Use read_file to list and inspect\n"
    "  everything that might be relevant to the task.\n"
    "\n"
    "IMPORTANT RULES:\n"
    "1. All file paths must be relative to the project root, e.g. 'data/file.csv'\n"
    "2. Use read_file to explore any folder and read any file format — it handles PDF, DOCX, PPTX, XLSX, CSV, images, audio, and more.\n"
    "3. When execute_code output is truncated, use read_file on the saved output file.\n"
    "4. Save charts with plt.savefig('charts/xxx.png'), dpi=150.\n"
    "5. Use analyze_data for quick statistical summaries of CSV/JSON files.\n"
    "6. Break large data analysis into step-by-step execute_code calls to avoid output truncation.\n"
    "7. After ALL iterations, call report_iteration to record results.\n"
    "8. When the experiment is done, use delete_file to clean up unnecessary scripts.\n"
    "9. Use search_literature to find background information, methods, and datasets on the web.\n"
    "10. Use fetch_url to read full webpage content.\n"
    "11. Use deep_research for comprehensive literature surveys.\n"
    "12. When the user asks for a report or paper, you MUST call BOTH write_paper AND write_file:\n"
    "    - write_paper: generates the .docx formatted paper for download\n"
    "    - write_file: saves the .md markdown version to workspace/papers/\n"
    "    Do NOT skip either one. Both formats are required.\n"
    "\n"
    "PAPER GENERATION (call write_paper tool):\n"
    "- The sections must contain Markdown with image references using ![](charts/xxx.png)\n"
    "- Always include charts and figures you generated.\n"
)


# ── WebSocket helpers ──

async def broadcast_log(msg, workspace_id: str, conv_id: str = "", seq: int = -1):
    data = json.dumps({"type": "log", "data": msg, "conv_id": conv_id, "seq": seq})
    for ws in _get_ws_state(workspace_id)["ws_connections"][:]:
        try:
            await ws.send_text(data)
        except Exception:
            try:
                _get_ws_state(workspace_id)["ws_connections"].remove(ws)
            except Exception:
                pass


async def broadcast_thinking(text, workspace_id: str):
    data = json.dumps({"type": "thinking", "data": text})
    for ws in _get_ws_state(workspace_id)["ws_connections"][:]:
        try:
            await ws.send_text(data)
        except Exception:
            pass


async def broadcast_tool_call_chunk(tool_name: str, chunk: str, workspace_id: str, conv_id: str = ""):
    """Broadcast streaming tool call arguments to frontend."""
    data = json.dumps({"type": "tool_call_chunk", "tool": tool_name, "data": chunk, "conv_id": conv_id})
    for ws in _get_ws_state(workspace_id)["ws_connections"][:]:
        try:
            await ws.send_text(data)
        except Exception:
            pass


async def broadcast_usage(usage_data, workspace_id: str):
    data = json.dumps({"type": "usage", "data": usage_data})
    for ws in _get_ws_state(workspace_id)["ws_connections"][:]:
        try:
            await ws.send_text(data)
        except Exception:
            pass


async def broadcast_status(workspace_id: str):
    state = _get_ws_state(workspace_id)
    data = json.dumps({
        "type": "status",
        "data": {"running": state["running"], "current_iteration": state["current_iteration"], "total_iterations": state["total_iterations"]}
    })
    for ws in state["ws_connections"][:]:
        try:
            await ws.send_text(data)
        except Exception:
            try:
                state["ws_connections"].remove(ws)
            except Exception:
                pass


async def broadcast_charts_update(workspace_id: str):
    charts = get_charts_list(workspace_id)
    data = json.dumps({"type": "charts_update", "data": charts})
    for ws in _get_ws_state(workspace_id)["ws_connections"][:]:
        try:
            await ws.send_text(data)
        except Exception:
            pass


async def broadcast_api_latency(latency_data: dict, workspace_id: str):
    """Broadcast per-API-call timing to frontend."""
    data = json.dumps({"type": "api_latency", "data": latency_data})
    for ws in _get_ws_state(workspace_id)["ws_connections"][:]:
        try:
            await ws.send_text(data)
        except Exception:
            pass


# ── Helpers ──

def get_charts_list(workspace_id: str):
    charts_dir = _workspace_dir(workspace_id, "charts")
    charts = []
    for f in sorted(charts_dir.glob("*.png"), reverse=True):
        charts.append({"name": f.name, "size": f.stat().st_size,
                       "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                       "url": f"/api/charts/{f.name}"})
    return charts


def get_files_list(workspace_id: str):
    data_dir = _workspace_dir(workspace_id, "data")
    scripts_dir = _workspace_dir(workspace_id, "scripts")
    papers_dir = _workspace_dir(workspace_id, "papers")
    ws_root = WORKSPACE_DIR / workspace_id
    files = []
    for f in sorted(data_dir.iterdir()):
        files.append({"name": f.name, "path": str(f.relative_to(ws_root)),
                       "size": f.stat().st_size, "type": "data",
                       "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()})
    for f in sorted(scripts_dir.glob("*.py"), reverse=True):
        files.append({"name": f.name, "path": str(f.relative_to(ws_root)),
                       "size": f.stat().st_size, "type": "scripts",
                       "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()})
    for f in sorted(papers_dir.glob("*"), reverse=True)[:30]:
        if f.suffix in (".md", ".docx"):
            files.append({"name": f.name, "path": str(f.relative_to(ws_root)),
                           "size": f.stat().st_size, "type": "papers",
                           "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()})
    return files


# ── App setup ──

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("✓ Database initialized")

    # ── Migration: move shared workspace files to per-workspace directories ──
    _migrate_marker = WORKSPACE_DIR / ".migrated"
    if not _migrate_marker.exists():
        try:
            _migrate_to_multitenant()
            _migrate_marker.touch()
            print("✓ Data migrated to per-workspace directories")
        except Exception as e:
            print(f"⚠ Migration error (non-fatal): {e}")
    yield


def _migrate_to_multitenant():
    """One-time migration: move shared workspace/ files into per-workspace dirs."""
    import shutil
    # Find all workspaces
    import sqlite3 as _sql
    db_path = str(DB_FILE)
    if not Path(db_path).exists():
        return
    conn = _sql.connect(db_path)
    ws_rows = conn.execute("SELECT id FROM workspaces").fetchall()
    conn.close()
    if not ws_rows:
        return

    # Shared dirs that may contain old files
    old_dirs = {
        "charts": WORKSPACE_DIR / "charts",
        "data": WORKSPACE_DIR / "data",
        "scripts": WORKSPACE_DIR / "scripts",
        "papers": WORKSPACE_DIR / "papers",
        "experiments": WORKSPACE_DIR / "experiments",
    }

    # Move all old files to the first user's workspace
    first_ws = ws_rows[0][0]
    for subdir, old_path in old_dirs.items():
        if not old_path.exists():
            continue
        new_dir = _workspace_dir(first_ws, subdir)
        for f in old_path.iterdir():
            if f.is_file():
                dest = new_dir / f.name
                if not dest.exists():
                    shutil.move(str(f), str(dest))
        # Remove old dir if empty
        try:
            if not any(old_path.iterdir()):
                old_path.rmdir()
        except Exception:
            pass

    # Import existing JSONL into experiment_records
    old_jsonl = WORKSPACE_DIR / "experiments" / "iteration_log.jsonl"
    new_jsonl = _workspace_dir(first_ws, "experiments") / "iteration_log.jsonl"
    if old_jsonl.exists() and not new_jsonl.exists():
        shutil.move(str(old_jsonl), str(new_jsonl))

    # Import JSONL records into DB
    if new_jsonl.exists():
        _import_jsonl_to_db(first_ws, new_jsonl)


def _import_jsonl_to_db(workspace_id: str, jsonl_path: Path):
    """Import iteration_log.jsonl records into experiment_records table."""
    import sqlite3 as _sql
    import uuid as _uuid
    db_path = str(DB_FILE)
    if not jsonl_path.exists():
        return
    conn = _sql.connect(db_path)
    for line in jsonl_path.read_text(encoding="utf-8").strip().split("\n"):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid = _uuid.uuid4().hex[:16]
        rd = rec.get("round", 0)
        hyp = rec.get("hypothesis", rec.get("hypothesis_id", ""))
        method = rec.get("method", "")
        conc = rec.get("conclusion", rec.get("summary", ""))
        success = rec.get("success", None)
        metrics = json.dumps(rec.get("metrics", {}), ensure_ascii=False)
        charts = json.dumps(rec.get("chart_files", []), ensure_ascii=False)
        rtype = rec.get("record_type", "experiment")
        ts = rec.get("timestamp", "")
        try:
            conn.execute(
                "INSERT OR IGNORE INTO experiment_records "
                "(id, workspace_id, round_num, hypothesis, method, conclusion, success, metrics, chart_files, record_type, timestamp, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (rid, workspace_id, rd, hyp, method, conc, success, metrics, charts, rtype, ts, datetime.now(timezone.utc).isoformat()),
            )
        except Exception:
            pass
    conn.commit()
    conn.close()
    print(f"  Imported experiment records from {jsonl_path}")

app = FastAPI(title="MolCraft API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(auth_router)


@app.get("/")
async def index():
    return HTMLResponse(
        (STATIC_DIR / "index.html").read_text(encoding="utf-8"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )


# ── Workspace routes ──

@app.get("/api/workspaces")
async def list_workspaces(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workspace).where(Workspace.user_id == user.id).order_by(Workspace.created_at))
    workspaces = result.scalars().all()
    return [{"id": w.id, "name": w.name, "created_at": w.created_at.isoformat()} for w in workspaces]


@app.post("/api/workspaces")
async def create_workspace(data: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ws = Workspace(user_id=user.id, name=data.get("name", "New Workspace"))
    db.add(ws)
    await db.commit()
    return {"id": ws.id, "name": ws.name}


# ── Config routes (per-user, keys encrypted) ──

@app.get("/api/config")
async def get_config(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Return user config — API key is masked, never exposed.

    API credentials (base_url, api_key, model) are NEVER read from stored conversation
    configs — they stay empty until the user explicitly types them in settings.
    Other settings (temperature, iterations, etc.) persist from the last saved config.
    """
    conv = await db.execute(
        select(Conversation).where(Conversation.workspace_id.in_(
            select(Workspace.id).where(Workspace.user_id == user.id)
        )).order_by(Conversation.updated_at.desc()).limit(1)
    )
    last_config = {}
    last_conv = conv.scalar_one_or_none()
    if last_conv and last_conv.config:
        last_config = last_conv.config

    return {
        "base_url": "",      # never pre-fill — user must enter it
        "api_key": "",       # never return the real key
        "api_key_configured": False,  # never reveal whether a key exists
        "model": "",         # never pre-fill — user must enter it
        "temperature": last_config.get("temperature", 0.3),
        "max_iterations": last_config.get("max_iterations", 3),
        "max_minutes": last_config.get("max_minutes", 90),
        "system_prompt": DEFAULT_SYSTEM_PROMPT,  # always return latest default
        "write_paper": last_config.get("write_paper", False),
    }


@app.post("/api/config")
async def update_config(data: ConfigUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Save user config. API key is encrypted before storage."""
    config_data = data.model_dump()
    if config_data.get("api_key"):
        config_data["api_key_enc"] = encrypt(config_data["api_key"])
    config_data.pop("api_key", None)  # don't store plaintext

    # Store on the user's latest conversation, or create a placeholder
    result = await db.execute(
        select(Conversation).where(Conversation.workspace_id.in_(
            select(Workspace.id).where(Workspace.user_id == user.id)
        )).order_by(Conversation.updated_at.desc()).limit(1)
    )
    conv = result.scalar_one_or_none()
    if conv:
        conv.config = {**conv.config, **config_data}
    else:
        # Ensure user has a workspace
        ws_result = await db.execute(
            select(Workspace).where(Workspace.user_id == user.id).limit(1)
        )
        ws = ws_result.scalar_one_or_none()
        if not ws:
            ws = Workspace(user_id=user.id, name="My Workspace")
            db.add(ws)
            await db.flush()
        conv = Conversation(workspace_id=ws.id, title="Config", config=config_data)
        db.add(conv)
    await db.commit()
    return {"status": "ok"}


# ── Conversation routes (DB-backed, workspace-scoped) ──

@app.get("/api/conversations")
async def list_conversations(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from sqlalchemy.orm import selectinload
    from sqlalchemy import func
    result = await db.execute(
        select(Conversation).options(selectinload(Conversation.logs))
        .join(Workspace).where(Workspace.user_id == user.id)
        .order_by(Conversation.updated_at.desc()).limit(100)
    )
    convs = result.unique().scalars().all()
    return [{
        "id": c.id, "title": c.title, "status": c.status,
        "created_at": c.created_at.isoformat(), "updated_at": c.updated_at.isoformat(),
        "goal_preview": (c.goal or "")[:80],
        "log_count": len(list(c.logs)) if c.logs else 0,
    } for c in convs]


@app.post("/api/conversations")
async def create_conversation(data: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workspace).where(Workspace.user_id == user.id).limit(1))
    ws = result.scalar_one_or_none()
    if not ws:
        ws = Workspace(user_id=user.id, name="My Workspace")
        db.add(ws)
        await db.flush()

    conv = Conversation(
        workspace_id=ws.id,
        title=data.get("title", "Untitled Research"),
        goal=data.get("goal", ""),
        config=data.get("config", {}),
    )
    db.add(conv)
    await db.commit()
    return {"id": conv.id, "title": conv.title}


@app.get("/api/conversations/{conv_id}")
async def get_conversation(conv_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Conversation).options(selectinload(Conversation.logs))
        .join(Workspace).where(
            Conversation.id == conv_id, Workspace.user_id == user.id
        )
    )
    conv = result.unique().scalar_one_or_none()
    if not conv:
        raise HTTPException(404, "Conversation not found")
    return {
        "id": conv.id, "title": conv.title, "goal": conv.goal,
        "status": conv.status, "config": conv.config,
        "token_usage": conv.token_usage,
        "created_at": conv.created_at.isoformat(), "updated_at": conv.updated_at.isoformat(),
        "logs": [{"seq": l.seq, "content": l.content, "created_at": l.created_at.isoformat()} for l in (list(conv.logs) if conv.logs else [])],
    }


@app.put("/api/conversations/{conv_id}")
async def update_conversation(conv_id: str, data: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Conversation).join(Workspace).where(
            Conversation.id == conv_id, Workspace.user_id == user.id
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(404, "Conversation not found")
    for k in ["title", "status", "goal", "config"]:
        if k in data:
            setattr(conv, k, data[k])
    # Handle clear_logs: delete all log entries for this conversation
    if data.get("clear_logs"):
        from sqlalchemy import delete as _delete
        await db.execute(_delete(ConversationLog).where(ConversationLog.conversation_id == conv_id))
    await db.commit()
    return {"status": "ok"}


@app.post("/api/conversations/{conv_id}/append_log")
async def append_log(conv_id: str, data: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Conversation).options(selectinload(Conversation.logs))
        .join(Workspace).where(
            Conversation.id == conv_id, Workspace.user_id == user.id
        )
    )
    conv = result.unique().scalar_one_or_none()
    if not conv:
        raise HTTPException(404, "Conversation not found")
    log_line = data.get("log", "")
    if log_line:
        log_list = list(conv.logs) if conv.logs else []
        seq = len(log_list)
        db.add(ConversationLog(conversation_id=conv.id, seq=seq, content=log_line))
    await db.commit()
    return {"status": "ok"}


@app.delete("/api/conversations/{conv_id}")
async def delete_conversation(conv_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Conversation).join(Workspace).where(
            Conversation.id == conv_id, Workspace.user_id == user.id
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(404, "Conversation not found")
    await db.delete(conv)
    await db.commit()
    return {"status": "deleted"}


# ── Agent runtime ──

class LogCapture(StringIO):
    """Captures stdout and broadcasts each line via WebSocket (using main loop)."""
    def __init__(self, workspace_id, main_loop):
        super().__init__()
        self._workspace_id = workspace_id
        self._main_loop = main_loop
        self._buffer = ""

    def write(self, s):
        super().write(s)
        self._buffer += s
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line.strip() and self._main_loop:
                asyncio.run_coroutine_threadsafe(
                    broadcast_log(line.strip(), self._workspace_id), self._main_loop
                )

    def flush(self):
        if self._buffer.strip() and self._main_loop:
            asyncio.run_coroutine_threadsafe(
                broadcast_log(self._buffer.strip(), self._workspace_id), self._main_loop
            )
            self._buffer = ""


_main_loop = None  # reference to the main server event loop


def run_agent_loop(
    user_id: str, workspace_id: str, conv_id: str,
    goal: str, config: dict, write_paper: bool,
    max_iterations: int, max_minutes: int,
):
    """Runs the research agent in a background thread. Publishes progress via broadcast."""
    agent_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(agent_loop)

    # Capture a reference to the main loop for cross-thread broadcasting
    try:
        main_loop = asyncio.get_running_loop()
    except RuntimeError:
        main_loop = _main_loop

    state = _get_ws_state(workspace_id)
    state["running"] = True
    state["stop"] = False
    state["stopped_by_user"] = False
    state["current_iteration"] = 0
    state["total_iterations"] = max_iterations

    # Bridge threading.Event (set from main thread) → asyncio.Event (for run_round)
    _stop_th_evt = state.get("stop_event")
    _stop_evt = asyncio.Event()

    async def _poll_stop():
        while _stop_th_evt and not _stop_th_evt.is_set():
            await asyncio.sleep(0.3)
        _stop_evt.set()
        state["stop"] = True

    start_time = time.time()
    deadline = start_time + max_minutes * 60
    agent = None

    # ── Database-backed logging (sync sqlite3 to avoid event loop issues) ──
    import sqlite3 as _sqlite3
    _DB_PATH = str(DB_FILE)  # use the same DB file as the main server

    def _db_log(msg, broadcast=True):
        """Write a log line to DB. If broadcast=True, also push via WebSocket."""
        seq = -1
        # 1. Persist to database
        try:
            conn = _sqlite3.connect(_DB_PATH, timeout=10)
            cur = conn.execute(
                "INSERT INTO conversation_logs (conversation_id, seq, content, created_at) "
                "VALUES (?, (SELECT COALESCE(MAX(seq), -1) + 1 FROM conversation_logs WHERE conversation_id = ?), ?, ?)",
                (conv_id, conv_id, msg, datetime.now(timezone.utc).isoformat()))
            conn.commit()
            row = conn.execute(
                "SELECT seq FROM conversation_logs WHERE rowid = ?", (cur.lastrowid,)
            ).fetchone()
            if row:
                seq = row[0]
            conn.close()
        except Exception as e:
            import traceback
            traceback.print_exc()
        # 2. Broadcast via WebSocket for instant frontend display
        if broadcast and main_loop:
            asyncio.run_coroutine_threadsafe(
                broadcast_log(msg, workspace_id, conv_id=conv_id, seq=seq), main_loop
            )

    def _bcast_status():
        if main_loop:
            asyncio.run_coroutine_threadsafe(broadcast_status(workspace_id), main_loop)

    def _bcast_usage(usage_data):
        if main_loop:
            asyncio.run_coroutine_threadsafe(
                broadcast_usage(usage_data, workspace_id), main_loop
            )

    def _bcast_latency(latency_data):
        if main_loop:
            asyncio.run_coroutine_threadsafe(
                broadcast_api_latency(latency_data, workspace_id), main_loop
            )

    async def _run():
        nonlocal agent
        try:
            # Get decrypted API key
            api_key_enc = config.get("api_key_enc", "")
            api_key = decrypt(api_key_enc) if api_key_enc else ""
            base_url = config.get("base_url", "")
            model = config.get("model", "")

            # Validate required config — no env var fallback, user must configure explicitly
            missing = []
            if not base_url.strip(): missing.append("API Base URL")
            if not api_key.strip(): missing.append("API Key")
            if not model.strip(): missing.append("Model")
            if missing:
                _db_log(f"✗ 缺少必要配置: {', '.join(missing)}，请在设置页面填写")
                state["running"] = False
                _bcast_status()
                return
            system_prompt = config.get("system_prompt") or DEFAULT_SYSTEM_PROMPT
            temperature = config.get("temperature", 0.3)

            _db_log(f"Starting research agent with model: {model}")
            _db_log(f"Goal: {goal[:200]}")

            # ── Set up per-workspace isolation ──
            from agent_core.workspace_context import build_workspace_paths, set_workspace_paths, set_db_writer

            ws_paths = build_workspace_paths(workspace_id, BASE_DIR)
            set_workspace_paths(ws_paths)

            # DB writer callback for experiment record persistence
            async def _db_write_exp(workspace_id, round_num, hypothesis, method, conclusion,
                                    success, metrics, chart_files, record_type):
                from server.database import async_session as _async_sess
                from server.models.experiment import ExperimentRecord
                async with _async_sess() as _db:
                    import uuid as _uuid
                    rec = ExperimentRecord(
                        id=_uuid.uuid4().hex[:16],
                        workspace_id=workspace_id,
                        conversation_id=conv_id,
                        round_num=round_num,
                        hypothesis=hypothesis,
                        method=method,
                        conclusion=conclusion,
                        success=success,
                        metrics=metrics or {},
                        chart_files=chart_files or [],
                        record_type=record_type,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    )
                    _db.add(rec)
                    try:
                        await _db.commit()
                    except Exception:
                        await _db.rollback()
            set_db_writer(_db_write_exp)
            # ── End workspace setup ──

            agent = ResearchAgent(
                api_key=api_key, base_url=base_url, model=model,
                tools=OPENAI_TOOLS, tool_handlers=TOOL_HANDLERS,
                system_prompt=system_prompt, temperature=temperature,
            )

            # Hook: log tool START immediately (before execution)
            async def _on_tool_start(tool_name, args):
                try:
                    args_str = json.dumps(args, ensure_ascii=False)
                    _db_log(f"[TOOL] {tool_name} | {args_str}")
                except Exception as ex:
                    _db_log(f"[ERROR] Tool start callback: {ex}")

            # Hook: log tool RESULT after execution
            async def _on_tool_log(tool_name, args, result):
                try:
                    if result:
                        # Truncate long content fields BEFORE serializing, so the
                        # JSON stays valid (truncating after serialization breaks JSON).
                        _safe = dict(result) if isinstance(result, dict) else result
                        if isinstance(_safe, dict):
                            for _key in ("content", "stdout", "text"):
                                _val = _safe.get(_key)
                                if isinstance(_val, str) and len(_val) > 1500:
                                    _safe[_key] = _val[:1500] + "...(truncated)"
                        result_str = json.dumps(_safe, ensure_ascii=False, default=str)
                        _db_log(result_str)
                    # Notify frontend when charts/papers/experiments are created
                    if tool_name in ("generate_chart", "write_paper", "record_experiment", "report_iteration"):
                        if main_loop:
                            asyncio.run_coroutine_threadsafe(
                                broadcast_charts_update(workspace_id), main_loop
                            )
                except Exception as ex:
                    _db_log(f"[ERROR] Tool log callback: {ex}")

            agent.on_tool_start = _on_tool_start
            agent.on_tool_call = _on_tool_log

            # Hook: broadcast thinking chunks + persist to DB on __END__
            _thinking_buf = []

            def _on_thinking(chunk_text):
                if chunk_text == '__END__':
                    full_text = ''.join(_thinking_buf)
                    _thinking_buf.clear()
                    if full_text.strip():
                        # Persist to DB but don't WS-broadcast —
                        # the live thinking bubble already shows it via broadcast_thinking
                        _db_log(f"[THINKING] {full_text}", broadcast=False)
                else:
                    _thinking_buf.append(chunk_text)
                if main_loop:
                    asyncio.run_coroutine_threadsafe(
                        broadcast_thinking(chunk_text, workspace_id), main_loop
                    )

            agent.on_thinking_chunk = _on_thinking

            # Hook: broadcast streaming tool call arguments (code, query, etc.)
            _tool_call_buf = {}  # idx -> [chunks]

            def _on_tool_call_chunk(tool_name, chunk):
                if main_loop:
                    asyncio.run_coroutine_threadsafe(
                        broadcast_tool_call_chunk(tool_name, chunk, workspace_id, conv_id), main_loop
                    )

            agent.on_tool_call_chunk = _on_tool_call_chunk

            async def _on_api_latency(latency_data):
                _bcast_latency(latency_data)
                # Also log in real-time (not via captured stdout which is delayed)
                ttfb = latency_data.get('ttfb_s', 0)
                total = latency_data.get('total_s', 0)
                chunks = latency_data.get('chunk_count', 0)
                _db_log('[API] TTFB={:.1f}s, total={:.1f}s, {} chunks'.format(ttfb, total, chunks))

            agent.on_api_latency = _on_api_latency

            # Start stop-polling task
            _stop_watcher = asyncio.ensure_future(_poll_stop())

            # Main iteration loop
            for iteration in range(max_iterations):
                if _stop_evt.is_set():
                    _db_log("Experiment stopped by user")
                    state["stopped_by_user"] = True
                    break

                if time.time() > deadline:
                    _db_log("⏰ Time limit reached")
                    break

                state["current_iteration"] = iteration + 1
                _bcast_status()
                _db_log(f"══ Iteration {iteration + 1}/{max_iterations} ══")

                combined_goal = goal
                if write_paper and iteration == max_iterations - 1:
                    combined_goal = goal + "\n\nFINAL ITERATION: After analysis, call write_paper to generate the final research paper."

                try:
                    # Capture stdout during agent execution
                    import io
                    old_stdout = sys.stdout
                    sys.stdout = io.StringIO()

                    _db_log("Sending request to model...")
                    result = await agent.run_round(combined_goal, stop_event=_stop_evt)
                    final_report = result.get("report") if isinstance(result, dict) else None
                    usage = result.get("usage") if isinstance(result, dict) else None

                    # Flush captured output (skip [TOOL] lines — already logged by callback)
                    import re as _re
                    captured = sys.stdout.getvalue()
                    sys.stdout = old_stdout
                    for line in captured.strip().split('\n'):
                        line = line.strip()
                        if not line:
                            continue
                        # Tool calls are already written instantly by _on_tool_log callback
                        if _re.search(r'\[TOOL\]\s+\S+', line):
                            continue
                        _db_log(line)

                    if final_report:
                        rpt_str = json.dumps(final_report, ensure_ascii=False) if isinstance(final_report, dict) else str(final_report)
                        _db_log(f"✓ {rpt_str[:500]}")

                    if usage:
                        cumulative = agent.cumulative_usage
                        cost, _ = estimate_cost(model, cumulative["prompt_tokens"], cumulative["completion_tokens"])
                        _bcast_usage({
                            "prompt_tokens": cumulative["prompt_tokens"],
                            "completion_tokens": cumulative["completion_tokens"],
                            "total_tokens": cumulative["total_tokens"],
                            "estimated_cost": cost,
                        })
                except Exception as e:
                    _db_log(f"✗ Iteration {iteration + 1} error: {e}")

            _db_log("✓ Experiment complete")

            # Update conversation status in DB
            from server.database import async_session
            async with async_session() as db:
                result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
                conv = result.scalar_one_or_none()
                if conv:
                    conv.status = "completed" if not state["stopped_by_user"] else "draft"
                    conv.token_usage = agent.cumulative_usage if agent else {}
                    await db.commit()

        except Exception as e:
            _db_log(f"Fatal error: {e}")
            from server.database import async_session
            async with async_session() as db:
                result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
                conv = result.scalar_one_or_none()
                if conv:
                    conv.status = "failed"
                    await db.commit()
        finally:
            if agent:
                try:
                    await agent.close()
                except Exception:
                    pass
            state["running"] = False
            _bcast_status()

    try:
        agent_loop.run_until_complete(_run())
    finally:
        agent_loop.close()


@app.post("/api/agent/start")
async def start_agent(data: AgentStartRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Start a research agent for the current user."""
    # Get user's workspace
    result = await db.execute(select(Workspace).where(Workspace.user_id == user.id).limit(1))
    ws = result.scalar_one_or_none()
    if not ws:
        ws = Workspace(user_id=user.id, name="My Workspace")
        db.add(ws)
        await db.flush()

    state = _get_ws_state(ws.id)
    if state["running"]:
        raise HTTPException(400, "An experiment is already running. Stop it first.")
    # Fresh event for cross-thread stop signalling
    state["stop_event"] = threading.Event()

    # Get user config from DB, but allow request to override system_prompt
    config = {}
    cfg_result = await db.execute(
        select(Conversation).where(Conversation.workspace_id == ws.id)
        .order_by(Conversation.updated_at.desc()).limit(1)
    )
    last_conv = cfg_result.scalar_one_or_none()
    if last_conv and last_conv.config:
        config = last_conv.config
    # Always use the latest DEFAULT_SYSTEM_PROMPT. The stored config may
    # contain a stale copy from an older version; only use it if the user
    # explicitly provided a custom one (non-empty and different from default).
    if data.system_prompt and data.system_prompt.strip() != DEFAULT_SYSTEM_PROMPT.strip():
        config["system_prompt"] = data.system_prompt
    else:
        config["system_prompt"] = DEFAULT_SYSTEM_PROMPT

    # Create or reuse conversation record
    conv = None
    if data.conv_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == data.conv_id,
                Conversation.workspace_id == ws.id
            )
        )
        conv = result.scalar_one_or_none()
    if not conv:
        conv = Conversation(
            workspace_id=ws.id,
            title=data.goal[:100] if data.goal else "Untitled",
            goal=data.goal,
            status="running",
            config=config,
        )
        db.add(conv)
    else:
        conv.goal = data.goal
        conv.title = data.goal[:100] if data.goal else conv.title
        conv.status = "running"
        conv.config = config
    await db.commit()

    # Launch agent thread — capture main loop for cross-thread broadcasts
    global _main_loop
    try:
        _main_loop = asyncio.get_running_loop()
    except RuntimeError:
        pass

    thread = threading.Thread(
        target=run_agent_loop,
        args=(user.id, ws.id, conv.id, data.goal, config, data.write_paper,
              data.max_iterations, data.max_minutes),
        daemon=True,
    )
    thread.start()

    return {"conversation_id": conv.id, "status": "started"}


@app.post("/api/agent/stop")
async def stop_agent(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workspace).where(Workspace.user_id == user.id).limit(1))
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(404, "No workspace found")

    state = _get_ws_state(ws.id)
    if not state["running"]:
        return {"status": "already_stopped"}
    state["stop"] = True
    # Set the threading.Event so the agent's asyncio.Event bridge fires immediately
    evt = state.get("stop_event")
    if evt:
        evt.set()

    # Wait for the agent to naturally stop (responds to stop_event within 0.3s now)
    for _ in range(100):
        if not state["running"]:
            return {"status": "stopped"}
        time.sleep(0.1)

    # Still running after 10s — force reset
    state["running"] = False
    state["stopped_by_user"] = True
    await broadcast_status(ws.id)
    return {"status": "force_stopped"}


@app.get("/api/status")
async def get_status(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workspace).where(Workspace.user_id == user.id).limit(1))
    ws = result.scalar_one_or_none()
    if not ws:
        return {"running": False, "current_iteration": 0, "total_iterations": 0}
    state = _get_ws_state(ws.id)
    return {"running": state["running"], "current_iteration": state["current_iteration"], "total_iterations": state["total_iterations"]}


# ── Experiments (reads from workspace/experiments/iteration_log.jsonl) ──

@app.get("/api/experiments")
async def list_experiments(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Return experiment records from DB (authoritative) + JSONL fallback."""
    result = await db.execute(select(Workspace).where(Workspace.user_id == user.id).limit(1))
    ws = result.scalar_one_or_none()
    if not ws:
        return {"records": [], "summary": {"total": 0, "confirmed": 0, "rejected": 0}}

    # Try DB first
    from agent_core.experiments import get_records_from_db
    return await get_records_from_db(db, ws.id)


@app.post("/api/experiments/clear")
async def clear_experiments(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workspace).where(Workspace.user_id == user.id).limit(1))
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(404, "No workspace found")

    # Clear DB records
    from server.models.experiment import ExperimentRecord
    from sqlalchemy import delete as sql_delete
    await db.execute(sql_delete(ExperimentRecord).where(ExperimentRecord.workspace_id == ws.id))
    await db.commit()

    # Also clear JSONL file
    iteration_log = _workspace_dir(ws.id, "experiments") / "iteration_log.jsonl"
    if iteration_log.exists():
        iteration_log.write_text("", encoding="utf-8")
    return {"status": "cleared"}


@app.get("/api/experiments/export")
async def export_experiments(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workspace).where(Workspace.user_id == user.id).limit(1))
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(404, "No workspace found")
    from agent_core.experiments import export_summary_markdown
    iteration_log = _workspace_dir(ws.id, "experiments") / "iteration_log.jsonl"
    md = export_summary_markdown(iteration_log)
    return {"markdown": md}


# ── Charts ──

@app.get("/api/charts")
async def list_charts(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workspace).where(Workspace.user_id == user.id).limit(1))
    ws = result.scalar_one_or_none()
    if not ws:
        return []
    return get_charts_list(ws.id)


@app.get("/api/charts/{name}")
async def serve_chart(name: str, token: str | None = None,
                      user: User = Depends(get_optional_user), db: AsyncSession = Depends(get_db)):
    # Accept token via URL query param (for <img> tags that can't send headers)
    if token and not user:
        payload = decode_token(token)
        if payload and payload.get("type") == "access":
            user = await get_user_by_id(db, payload.get("sub"))
    if not user:
        raise HTTPException(401, "Not authenticated")
    result = await db.execute(select(Workspace).where(Workspace.user_id == user.id).limit(1))
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(404)
    path = _workspace_dir(ws.id, "charts") / name
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path)


# ── Files ──

@app.get("/api/files")
async def list_files(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workspace).where(Workspace.user_id == user.id).limit(1))
    ws = result.scalar_one_or_none()
    if not ws:
        return []
    return get_files_list(ws.id)


@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workspace).where(Workspace.user_id == user.id).limit(1))
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(404, "No workspace found")
    data_dir = _workspace_dir(ws.id, "data")
    path = data_dir / file.filename
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    return {"filename": file.filename, "size": len(content)}


@app.get("/api/files/{file_type}/{name}")
async def serve_file(file_type: str, name: str, token: str | None = None,
                     user: User = Depends(get_optional_user), db: AsyncSession = Depends(get_db)):
    # Accept token via URL query param (for <img>/<iframe> tags that can't send headers)
    if token and not user:
        payload = decode_token(token)
        if payload and payload.get("type") == "access":
            user = await get_user_by_id(db, payload.get("sub"))
    if not user:
        raise HTTPException(401, "Not authenticated")
    result = await db.execute(select(Workspace).where(Workspace.user_id == user.id).limit(1))
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(404)
    dir_map = {
        "data": _workspace_dir(ws.id, "data"),
        "scripts": _workspace_dir(ws.id, "scripts"),
        "papers": _workspace_dir(ws.id, "papers"),
        "charts": _workspace_dir(ws.id, "charts"),
    }
    d = dir_map.get(file_type)
    if not d:
        raise HTTPException(404)
    path = d / name
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path)


@app.get("/api/files/{file_type}/{name}/download")
async def download_file(file_type: str, name: str, token: str | None = None,
                        user: User = Depends(get_optional_user), db: AsyncSession = Depends(get_db)):
    """Serve file as download attachment (Content-Disposition)."""
    if token and not user:
        payload = decode_token(token)
        if payload and payload.get("type") == "access":
            user = await get_user_by_id(db, payload.get("sub"))
    if not user:
        raise HTTPException(401, "Not authenticated")
    result = await db.execute(select(Workspace).where(Workspace.user_id == user.id).limit(1))
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(404)
    dir_map = {
        "data": _workspace_dir(ws.id, "data"),
        "scripts": _workspace_dir(ws.id, "scripts"),
        "papers": _workspace_dir(ws.id, "papers"),
        "charts": _workspace_dir(ws.id, "charts"),
    }
    d = dir_map.get(file_type)
    if not d:
        raise HTTPException(404)
    path = d / name
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path, filename=name, media_type="application/octet-stream")


@app.delete("/api/files/{file_type}/{name}")
async def delete_file_api(file_type: str, name: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workspace).where(Workspace.user_id == user.id).limit(1))
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(404, "No workspace found")
    dir_map = {
        "data": _workspace_dir(ws.id, "data"),
        "scripts": _workspace_dir(ws.id, "scripts"),
        "papers": _workspace_dir(ws.id, "papers"),
        "charts": _workspace_dir(ws.id, "charts"),
    }
    d = dir_map.get(file_type)
    if not d:
        raise HTTPException(404)
    path = d / name
    if path.exists():
        path.unlink()
    return {"status": "deleted"}


# ── WebSocket ──

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()

    # Try to authenticate
    token = ws.query_params.get("token")
    user = None
    workspace_id = None

    if token:
        payload = decode_token(token)
        if payload and payload.get("type") == "access":
            from server.database import async_session as _as
            async with _as() as db:
                u = await get_user_by_id(db, payload.get("sub"))
                if u:
                    user = u
                    result = await db.execute(select(Workspace).where(Workspace.user_id == u.id).limit(1))
                    ws_obj = result.scalar_one_or_none()
                    if ws_obj:
                        workspace_id = ws_obj.id

    if workspace_id is None:
        workspace_id = "__anon__"

    state = _get_ws_state(workspace_id)
    state["ws_connections"].append(ws)

    try:
        while True:
            d = await ws.receive_text()
            if d == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
    except Exception:
        try:
            state["ws_connections"].remove(ws)
        except Exception:
            pass


# ── Startup ──

def run_server(host=None, port=None):
    host = host or os.getenv("HOST", "0.0.0.0")
    port = int(port or os.getenv("PORT", "8501"))
    print(f"Starting MolCraft at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_server()
