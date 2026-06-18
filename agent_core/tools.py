"""通用科研工具定义 —— OpenAI function calling 格式的工具注册表。

12 个通用工具覆盖科研全流程:
    1. read_file               — 读取文件（数据、历史记录、代码）
    2. write_file              — 写出文件（结果 CSV、报告、脚本）
    3. execute_code            — 执行 Python 代码（核心实验能力）
    4. search_literature       — 搜索互联网文献/信息
    5. analyze_data            — 分析 CSV/JSON 数据，输出统计信息
    6. generate_chart          — 生成 matplotlib 可视化图表
    7. record_experiment       — 记录单次实验结果到日志
    8. report_iteration        — 报告一轮迭代完成
    9. write_paper             — 从实验记录生成学术论文
    10. delete_file             — 清理 workspace 中的临时文件
    11. fetch_url               — 抓取网页全文内容
    12. deep_research           — 一键深度研究（多源搜索+全文抓取）
"""
import asyncio
import csv
import io
import json
import os
import re
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

from agent_core.workspace_context import get_workspace_paths, get_db_writer


OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取文件内容（MarkItDown 驱动，支持 20+ 格式）。支持: PDF/DOCX/PPTX/XLSX/EPUB/CSV/IPYNB/HTML/XML/JSON/ZIP/图片/音频/纯文本等。用于读取用户上传的数据文件、历史实验记录、之前生成的代码等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "相对于项目根目录的文件路径，如 workspace/data/input.csv"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "读取的起始字符位置（从0开始），用于分页读取大文件",
                        "default": 0
                    },
                    "limit": {
                        "type": "integer",
                        "description": "最多读取的字符数，默认读取全部，超出50000自动截断",
                        "default": 0
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "将内容写入文件。用于保存实验结果 CSV、分析报告、可视化脚本等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "相对于项目根目录的文件路径，如 workspace/experiments/result.csv"
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入的完整文件内容"
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_code",
            "description": (
                "在独立进程中执行 Python 代码并返回输出。用于运行实验、数据分析、"
                "模型训练等任意计算任务。代码中可用 print() 输出结果。"
                "沙箱已安装以下库，均可直接 import 使用："
                "numpy, scipy, sympy (数值/符号); "
                "pandas, openpyxl (数据处理/Excel); "
                "matplotlib, seaborn, plotly (绑图/可视化，用 plt.savefig('charts/xxx.png') 保存); "
                "scikit-learn, xgboost, lightgbm, statsmodels (机器学习/数据挖掘/统计); "
                "torch, torchvision (神经网络/深度学习，CUDA GPU 可用); "
                "scikit-image, pillow (图像处理); "
                "networkx (图分析); "
                "requests (HTTP); Python 标准库全部。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的 Python 代码"
                    },
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "代码执行超时秒数，默认 120",
                        "default": 120
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_literature",
            "description": (
                "搜索互联网获取文献、方法、数据集等信息。"
                "用于了解研究背景、查找参考实现、获取公开数据集 URL 等。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词或问题"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "最多返回结果数，默认 5",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_data",
            "description": (
                "分析 CSV 或 JSON 数据文件，返回行数、列名、各列统计信息"
                "（均值/标准差/最小值/最大值/缺失值比例）。帮助 Agent 理解数据特征。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "数据文件路径，如 workspace/data/experiment.csv"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_chart",
            "description": (
                "根据数据文件和配置生成 matplotlib 图表并保存为 PNG。"
                "支持折线图(line)、柱状图(bar)、散点图(scatter)、直方图(hist)、箱线图(box)。"
                "适用于可视化实验结果、对比不同方法的效果等。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "data_file": {
                        "type": "string",
                        "description": "CSV 数据文件路径"
                    },
                    "chart_type": {
                        "type": "string",
                        "enum": ["line", "bar", "scatter", "hist", "box"],
                        "description": "图表类型"
                    },
                    "x_column": {
                        "type": "string",
                        "description": "X 轴对应的列名"
                    },
                    "y_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Y 轴对应的列名列表（支持多条曲线）"
                    },
                    "title": {
                        "type": "string",
                        "description": "图表标题"
                    },
                    "x_label": {
                        "type": "string",
                        "description": "X 轴标签",
                        "default": ""
                    },
                    "y_label": {
                        "type": "string",
                        "description": "Y 轴标签",
                        "default": ""
                    }
                },
                "required": ["data_file", "chart_type", "x_column", "y_columns", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "record_experiment",
            "description": (
                "记录一次实验的完整信息到 iteration_log.jsonl。"
                "每完成一次「假设→实验→数据分析→结论」闭环后调用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "round_num": {
                        "type": "integer",
                        "description": "当前迭代轮次，从 1 开始"
                    },
                    "hypothesis": {
                        "type": "string",
                        "description": "本轮验证的假设"
                    },
                    "method": {
                        "type": "string",
                        "description": "使用的实验方法/代码描述"
                    },
                    "metrics": {
                        "type": "object",
                        "description": "关键指标名→值的映射，如 {\"accuracy\": 0.92, \"f1\": 0.88}"
                    },
                    "conclusion": {
                        "type": "string",
                        "description": "实验结论：假设是否成立，发现了什么"
                    },
                    "chart_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "关联的图表文件路径列表"
                    }
                },
                "required": ["round_num", "hypothesis", "conclusion"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "report_iteration",
            "description": "报告当前迭代已完成，main.py 通过此调用统计迭代次数并控制终止。每轮闭环结束时必须调用一次。",
            "parameters": {
                "type": "object",
                "properties": {
                    "round_num": {
                        "type": "integer",
                        "description": "当前迭代轮次"
                    },
                    "hypothesis_id": {
                        "type": "string",
                        "description": "本轮假设 ID，如 H001"
                    },
                    "success": {
                        "type": "boolean",
                        "description": "假设是否被验证"
                    },
                    "summary": {
                        "type": "string",
                        "description": "本轮摘要，包括关键指标变化和下一步方向"
                    }
                },
                "required": ["round_num", "hypothesis_id", "success", "summary"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_paper",
            "description": (
                "根据所有实验记录撰写一篇学术论文。"
                "论文应包含：标题、摘要、引言、方法、实验结果、讨论、结论、参考文献。"
                "所有实验数据来自 iteration_log.jsonl 中的历史记录。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "论文标题"
                    },
                    "abstract": {
                        "type": "string",
                        "description": "论文摘要 (200-300字)"
                    },
                    "sections": {
                        "oneOf": [
                            {"type": "object", "description": "JSON object with section names as keys and markdown text as values"},
                            {"type": "string", "description": "JSON string encoding the sections object"}
                        ],
                        "description": (
                            "论文各章节内容，key为章节名(如introduction/methods/results/discussion/conclusion)，"
                            "value为该章节的完整 Markdown 文本。可以传 JSON 对象或 JSON 字符串。"
                        )
                    },
                    "references": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "参考文献列表"
                    }
                },
                "required": ["title", "abstract", "sections"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "删除 workspace 中的文件。用于清理不再需要的临时脚本、过时的输出文件等。只能删除 workspace/scripts/、workspace/data/ 和 workspace/charts/ 下的文件。",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要删除的文件路径，如 workspace/scripts/old_script.py"
                    },
                    "reason": {
                        "type": "string",
                        "description": "删除原因（用于日志记录）"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "抓取网页全文内容，提取纯文本正文。用于读取搜索到的网页、在线文档、论文摘要页面等。配合 search_literature 使用：先搜索，再抓取有潜力的 URL。",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要抓取的网页 URL"
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "返回文本的最大字符数，默认 10000",
                        "default": 10000
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "deep_research",
            "description": "一键深度文献调研：搜索网页（DuckDuckGo）并自动抓取搜索结果中的网页全文。用于对某个课题进行全面的文献调研，一次性获取多源研究素材。",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "研究课题或调研问题，越具体越好"
                    },
                    "num_sources": {
                        "type": "integer",
                        "description": "每个来源搜索和抓取的数量，默认 5",
                        "default": 5
                    }
                },
                "required": ["topic"]
            }
        }
    }
]


def _safe_path(relative_path: str) -> Path:
    """Resolve a user/LLM-provided path within the current workspace.

    Strips any 'workspace/' prefix (the LLM uses workspace/data/xxx.csv style paths)
    and resolves relative to the workspace-scoped directory.
    """
    paths = get_workspace_paths()
    clean = relative_path.replace("\\", "/")
    if clean.startswith("workspace/"):
        clean = clean[len("workspace/"):]
    # Also strip a leading workspace_id prefix if present (e.g. "abc123/data/file.csv")
    if clean.startswith(paths.workspace_id + "/"):
        clean = clean[len(paths.workspace_id) + 1:]

    ws_dir = paths.workspace_dir.resolve()
    p = (ws_dir / clean).resolve()
    if not str(p).startswith(str(ws_dir)):
        raise ValueError(f"路径越界: {relative_path}")

    # Auto-discover: if file doesn't exist at the given path, try data_dir
    if not p.exists() and "/" not in clean:
        alt = (paths.data_dir / clean).resolve()
        if alt.exists():
            return alt
    return p


async def handle_read_file(file_path: str, offset: int = 0, limit: int = 0, **kwargs) -> dict:
    p = _safe_path(file_path)
    if not p.exists():
        return {"error": f"文件不存在: {file_path}"}

    # ── MarkItDown-powered file reading ──
    # Uses Microsoft MarkItDown to convert 20+ file formats to Markdown:
    #   PDF, DOCX, PPTX, XLSX, XLS, EPUB, CSV, IPYNB (Jupyter),
    #   HTML/HTM, XML, JSON, ZIP, images (BMP/GIF/JPEG/PNG/TIFF/WEBP),
    #   audio (AAC/FLAC/M4A/MP3/OGG/WAV/WMA), Outlook MSG,
    #   plain text (.txt/.md/.py/.js/.json/.csv/etc.)
    #
    # Audio files get dedicated transcription with Chinese/English language support.
    # Falls back to direct text read for formats MarkItDown cannot handle.

    _converter_used = "plain_text"
    _title = None
    _size_bytes = p.stat().st_size
    _audio_exts = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".wma", ".aac", ".aiff"}

    # ── Audio: use speech_recognition directly (MarkItDown's AudioConverter
    #     doesn't pass language param and fails on non-English speech) ──
    if p.suffix.lower() in _audio_exts:
        try:
            import speech_recognition as sr
        except ImportError:
            return {
                "error": f"无法读取音频文件: speech_recognition 未安装",
                "file_path": file_path,
                "size_bytes": _size_bytes,
            }
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(str(p)) as source:
                audio = recognizer.record(source)
            # Try Chinese first, then English, then auto-detect
            transcript = ""
            for lang in ["zh-CN", "en-US", "ja-JP", "ko-KR", "fr-FR", "de-DE", "es-ES", "pt-BR", "ru-RU", None]:
                try:
                    if lang:
                        transcript = recognizer.recognize_google(audio, language=lang)
                    else:
                        transcript = recognizer.recognize_google(audio)
                    if transcript.strip():
                        break
                except sr.UnknownValueError:
                    continue
                except Exception:
                    continue
            if not transcript.strip():
                transcript = "[未检测到语音内容]"
            content = f"# Audio Transcript: {p.name}\n\n{transcript.strip()}\n"
            _converter_used = "speech_recognition"
        except sr.RequestError as e:
            return {
                "error": f"语音识别服务连接失败 (需代理): {e}",
                "file_path": file_path,
                "size_bytes": _size_bytes,
            }
        except Exception as e:
            return {
                "error": f"音频转录失败: {e}",
                "file_path": file_path,
                "size_bytes": _size_bytes,
            }
    else:
        # ── All other formats: use MarkItDown ──
        try:
            from markitdown import MarkItDown
            from markitdown import (
                FileConversionException, UnsupportedFormatException,
                MissingDependencyException,
            )

            md = MarkItDown()
            result = md.convert_local(str(p))
            content = result.markdown
            _converter_used = "markitdown"
            _title = result.title
        except UnsupportedFormatException:
            # Format genuinely not supported — fall back to plain text
            try:
                content = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                return {
                    "error": f"不支持此文件格式: {p.suffix}",
                    "file_path": file_path,
                    "size_bytes": _size_bytes,
                }
        except MissingDependencyException as e:
            # MarkItDown knows the format but dependencies are missing
            try:
                content = p.read_text(encoding="utf-8")
                _converter_used = "plain_text_fallback"
            except UnicodeDecodeError:
                return {
                    "error": f"无法读取 {p.suffix} 文件 — 缺少依赖: {e}",
                    "file_path": file_path,
                    "size_bytes": _size_bytes,
                }
        except FileConversionException as e:
            # MarkItDown tried but all converters failed — extract underlying cause
            detail = ""
            if hasattr(e, "attempts") and e.attempts:
                for att in e.attempts:
                    exc_info = getattr(att, "exc_info", None)
                    if exc_info and len(exc_info) >= 2 and exc_info[1] is not None:
                        inner_name = type(exc_info[1]).__name__
                        inner_msg = str(exc_info[1])[:300]
                        detail = f" {inner_name}: {inner_msg}"
                    else:
                        converter = getattr(att, "converter", None)
                        cn = type(converter).__name__ if converter is not None else "Unknown"
                        detail = f" converter={cn}"
                    break
            # Try plain text fallback
            try:
                content = p.read_text(encoding="utf-8")
                _converter_used = "plain_text_fallback"
            except UnicodeDecodeError:
                return {
                    "error": f"无法读取 {p.suffix} 文件 —{detail}",
                    "file_path": file_path,
                    "size_bytes": _size_bytes,
                }
        except ImportError:
            # markitdown not installed — fall back to plain text
            try:
                content = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                return {
                    "error": f"无法读取此文件格式: {p.suffix} (MarkItDown 未安装)",
                    "file_path": file_path,
                    "size_bytes": _size_bytes,
                }
        except Exception as e:
            # Catch-all: any other error from MarkItDown, try plain text
            try:
                content = p.read_text(encoding="utf-8")
                _converter_used = "plain_text_fallback"
            except UnicodeDecodeError:
                return {
                    "error": f"MarkItDown 转换失败: {e}",
                    "file_path": file_path,
                    "size_bytes": _size_bytes,
                }

    # ── Pagination (offset / limit) ──
    total_len = len(content)
    if offset > 0:
        content = content[offset:]

    max_chars = limit if limit > 0 else 50000
    if len(content) > max_chars:
        result = {
            "file_path": file_path,
            "size_bytes": _size_bytes,
            "content": content[:max_chars],
            "truncated": True,
            "offset": offset,
            "next_offset": offset + max_chars,
            "total_chars": total_len,
            "converter": _converter_used,
            "note": f"Read chars {offset}-{offset + max_chars} of {total_len}. Use offset={offset + max_chars} to continue.",
        }
    else:
        result = {
            "file_path": file_path,
            "size_bytes": _size_bytes,
            "content": content,
            "offset": offset,
            "total_chars": total_len,
            "converter": _converter_used,
        }

    if _title:
        result["title"] = _title

    return result


async def handle_write_file(file_path: str, content: str) -> dict:
    p = _safe_path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return {"file_path": file_path, "size_bytes": len(content), "status": "written"}


async def handle_execute_code(code: str, timeout_seconds: int = 120) -> dict:
    paths = get_workspace_paths()
    script_path = paths.scripts_dir / f"agent_script_{int(time.time()*1000)}.py"
    script_path.write_text(code, encoding="utf-8")

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, str(script_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(paths.workspace_dir),  # run in workspace dir so user code can use relative paths
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout_seconds
        )
        stdout_text = stdout.decode("utf-8", errors="replace")
        stderr_text = stderr.decode("utf-8", errors="replace")[:2000]
        # If output is too long, save to file and return summary
        max_display = 30000
        if len(stdout_text) > max_display:
            out_file = paths.data_dir / f"output_{int(time.time()*1000)}.txt"
            out_file.write_text(stdout_text, encoding="utf-8")
            return {
                "exit_code": proc.returncode,
                "stdout": stdout_text[:max_display] + f"\n... [OUTPUT TRUNCATED: {len(stdout_text)-max_display} more chars. Full file: {out_file.relative_to(BASE_DIR)}. Use read_file to read it.]",
                "stderr": stderr_text,
                "script_path": str(script_path.relative_to(BASE_DIR)),
                "output_file": str(out_file.relative_to(BASE_DIR)),
                "total_chars": len(stdout_text),
            }
        return {
            "exit_code": proc.returncode,
            "stdout": stdout_text,
            "stderr": stderr_text,
            "script_path": str(script_path.relative_to(BASE_DIR)),
        }
    except asyncio.TimeoutError:
        proc.kill()
        return {"error": f"执行超时 ({timeout_seconds}s)", "exit_code": -1}
    except Exception as e:
        return {"error": str(e), "exit_code": -1}


async def handle_search_literature(query: str, max_results: int = 5) -> dict:
    try:
        from ddgs import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")[:300],
                })
        return {"query": query, "results": results, "count": len(results)}
    except ImportError:
        return {"error": "duckduckgo_search 未安装，请运行 pip install duckduckgo-search"}
    except Exception as e:
        return {"query": query, "results": [], "error": str(e)}


async def handle_analyze_data(file_path: str) -> dict:
    p = _safe_path(file_path)
    if not p.exists():
        return {"error": f"文件不存在: {file_path}"}

    try:
        if file_path.endswith(".json"):
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return {"file_path": file_path, "format": "json_array", "record_count": len(data)}
            return {"file_path": file_path, "format": "json_object", "keys": list(data.keys()) if isinstance(data, dict) else []}

        if file_path.endswith(".jsonl"):
            records = []
            for line in p.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    records.append(json.loads(line))
            return {"file_path": file_path, "format": "jsonl", "record_count": len(records)}

        if file_path.endswith(".csv"):
            rows = list(csv.DictReader(p.read_text(encoding="utf-8").splitlines()))
            if not rows:
                return {"file_path": file_path, "format": "csv", "row_count": 0, "columns": []}

            columns = list(rows[0].keys())
            stats = {}
            for col in columns:
                values = []
                missing = 0
                for row in rows:
                    v = row.get(col, "")
                    if v == "" or v is None:
                        missing += 1
                        continue
                    try:
                        values.append(float(v))
                    except ValueError:
                        pass

                if values:
                    stats[col] = {
                        "count": len(values),
                        "missing": missing,
                        "missing_pct": round(missing / len(rows) * 100, 1),
                        "min": round(min(values), 4),
                        "max": round(max(values), 4),
                        "mean": round(sum(values) / len(values), 4),
                    }
                    sorted_vals = sorted(values)
                    stats[col]["median"] = round(sorted_vals[len(sorted_vals) // 2], 4)
                else:
                    stats[col] = {"count": 0, "missing": missing, "type": "non_numeric"}

            return {
                "file_path": file_path,
                "format": "csv",
                "row_count": len(rows),
                "columns": columns,
                "stats": stats,
            }

        return {"error": f"不支持的文件格式: {file_path}，仅支持 .csv/.json/.jsonl"}
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()[:1000]}


async def handle_generate_chart(
    data_file: str,
    chart_type: str,
    x_column: str,
    y_columns: list,
    title: str,
    x_label: str = "",
    y_label: str = "",
) -> dict:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm

        _font_ok = False
        for font_name in ["Microsoft YaHei", "SimHei", "WenQuanYi Micro Hei", "Noto Sans CJK SC"]:
            for f in fm.fontManager.ttflist:
                if font_name in f.name:
                    plt.rcParams["font.sans-serif"] = [f.name, "sans-serif"]
                    plt.rcParams["axes.unicode_minus"] = False
                    _font_ok = True
                    break
            if _font_ok:
                break

        p = _safe_path(data_file)
        if not p.exists():
            return {"error": f"数据文件不存在: {data_file}"}

        rows = list(csv.DictReader(p.read_text(encoding="utf-8").splitlines()))
        if not rows:
            return {"error": "CSV 文件为空"}

        x_data = []
        y_data_map = {col: [] for col in y_columns}
        for row in rows:
            try:
                x_data.append(float(row.get(x_column, 0)))
            except (ValueError, TypeError):
                x_data.append(row.get(x_column, ""))
            for col in y_columns:
                try:
                    y_data_map[col].append(float(row.get(col, 0)))
                except (ValueError, TypeError):
                    y_data_map[col].append(0)

        fig, ax = plt.subplots(figsize=(10, 6))

        colors = ["#2196F3", "#FF5722", "#4CAF50", "#FFC107", "#9C27B0"]

        if chart_type == "line":
            for i, col in enumerate(y_columns):
                ax.plot(x_data, y_data_map[col], marker="o", color=colors[i % len(colors)], label=col, linewidth=2)
        elif chart_type == "bar":
            import numpy as np
            n_groups = len(x_data)
            n_bars = len(y_columns)
            bar_width = 0.8 / n_bars
            indices = np.arange(n_groups)
            for i, col in enumerate(y_columns):
                ax.bar(indices + i * bar_width, y_data_map[col], bar_width, color=colors[i % len(colors)], label=col)
            ax.set_xticks(indices + bar_width * (n_bars - 1) / 2)
            ax.set_xticklabels(x_data, rotation=45, ha="right")
        elif chart_type == "scatter":
            for i, col in enumerate(y_columns):
                ax.scatter(x_data, y_data_map[col], color=colors[i % len(colors)], label=col, s=60, alpha=0.7)
        elif chart_type == "hist":
            for i, col in enumerate(y_columns):
                ax.hist(y_data_map[col], bins=20, alpha=0.6, color=colors[i % len(colors)], label=col)
        elif chart_type == "box":
            ax.boxplot([y_data_map[col] for col in y_columns], labels=y_columns)
        else:
            return {"error": f"不支持的图表类型: {chart_type}"}

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(x_label or x_column)
        ax.set_ylabel(y_label or "Value")
        if chart_type != "box":
            ax.legend(loc="best")
        ax.grid(True, alpha=0.3)

        paths = get_workspace_paths()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_filename = f"chart_{chart_type}_{timestamp}.png"
        chart_path = paths.charts_dir / chart_filename
        fig.tight_layout()
        fig.savefig(str(chart_path), dpi=150, bbox_inches="tight")
        plt.close(fig)

        return {
            "chart_path": str(chart_path.relative_to(BASE_DIR)),
            "chart_type": chart_type,
            "title": title,
            "status": "generated",
        }
    except ImportError:
        return {"error": "matplotlib 未安装"}
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()[:1000]}


async def handle_record_experiment(
    round_num: int,
    hypothesis: str,
    conclusion: str,
    method: str = "",
    metrics: dict = None,
    chart_files: list = None,
    **kwargs,  # absorb extra fields from model (e.g. mean, std) → merge into metrics
) -> dict:
    paths = get_workspace_paths()
    metrics = dict(metrics or {})
    # Merge any extra keyword arguments into metrics (model sometimes flattens them)
    for k, v in kwargs.items():
        if k not in metrics:
            metrics[k] = v
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "round": round_num,
        "hypothesis": hypothesis,
        "method": method,
        "metrics": metrics,
        "conclusion": conclusion,
        "chart_files": chart_files or [],
        "record_type": "experiment",
    }
    # 1. Always persist to JSONL (durable audit trail)
    paths.iteration_log.parent.mkdir(parents=True, exist_ok=True)
    with open(paths.iteration_log, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    # 2. Attempt DB write via callback (best-effort, must not break agent)
    db_writer = get_db_writer()
    if db_writer:
        try:
            await db_writer(
                workspace_id=paths.workspace_id,
                round_num=round_num,
                hypothesis=hypothesis,
                method=method,
                conclusion=conclusion,
                success=None,
                metrics=metrics,
                chart_files=chart_files or [],
                record_type="experiment",
            )
        except Exception:
            pass  # DB failure must not interrupt the agent
    return {"status": "recorded", "round": round_num}


async def handle_report_iteration(
    round_num: int,
    hypothesis_id: str,
    success: bool,
    summary: str,
) -> dict:
    paths = get_workspace_paths()
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "round": round_num,
        "hypothesis_id": hypothesis_id,
        "success": success,
        "summary": summary,
        "record_type": "report",
    }
    paths.iteration_log.parent.mkdir(parents=True, exist_ok=True)
    with open(paths.iteration_log, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    # Attempt DB write via callback (best-effort)
    db_writer = get_db_writer()
    if db_writer:
        try:
            await db_writer(
                workspace_id=paths.workspace_id,
                round_num=round_num,
                hypothesis=hypothesis_id,
                method="",
                conclusion=summary,
                success=success,
                metrics=None,
                chart_files=[],
                record_type="report",
            )
        except Exception:
            pass
    return {"status": "recorded", "round": round_num, "message": f"第 {round_num} 轮迭代已记录"}

async def handle_write_paper(
    title: str,
    abstract: str,
    sections: dict = None,
    references: list = None,
    **kwargs,
) -> dict:
    # sections may come as a string (JSON-encoded) from some API providers
    if sections is None:
        # Try kwargs for alternative parameter names
        sections = kwargs.get("content") or kwargs.get("body") or {}
    
    if isinstance(sections, str):
        try:
            sections = json.loads(sections)
        except json.JSONDecodeError:
            return {"error": "sections 参数格式错误，期望 JSON 对象，收到无法解析的字符串"}
    if references and isinstance(references, str):
        try:
            references = json.loads(references)
        except json.JSONDecodeError:
            references = []
            
    paths = get_workspace_paths()
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    paper_filename = f"paper_{now}.md"
    paper_path = paths.papers_dir / paper_filename

    md_lines = [
        f"# {title}",
        "",
        f"## 摘要",
        "",
        abstract,
        "",
    ]

    section_order = ["introduction", "methods", "results", "discussion", "conclusion"]
    section_labels = {
        "introduction": "引言",
        "methods": "方法",
        "results": "实验结果",
        "discussion": "讨论",
        "conclusion": "结论",
    }

    for key in section_order:
        if key in sections:
            label = section_labels.get(key, key)
            md_lines.append(f"## {label}")
            md_lines.append("")
            md_lines.append(sections[key])
            md_lines.append("")

    for extra_key in sections:
        if extra_key not in section_order:
            md_lines.append(f"## {extra_key}")
            md_lines.append("")
            md_lines.append(sections[extra_key])
            md_lines.append("")

    if references:
        md_lines.append("## 参考文献")
        md_lines.append("")
        for i, ref in enumerate(references, 1):
            # Handle nested lists (some LLMs output [["ref1"], ["ref2"]])
            if isinstance(ref, list):
                ref = "; ".join(str(r) for r in ref)
            md_lines.append(f"[{i}] {ref}")
        md_lines.append("")

    md_content = "\n".join(md_lines)
    paper_path.write_text(md_content, encoding="utf-8")

    result = {
        "status": "written",
        "paper_path": str(paper_path.relative_to(BASE_DIR)),
        "title": title,
    }

    try:
        from agent_core.paper_exporter import md_to_docx
        docx_filename = f"paper_{now}.docx"
        docx_path = paths.papers_dir / docx_filename
        export_result = md_to_docx(md_content, docx_path, base_dir=paths.workspace_dir)
        result["docx_path"] = str(docx_path.relative_to(BASE_DIR))
        result["docx_status"] = export_result["status"]
        result["images_embedded"] = export_result.get("images_embedded", 0)
        result["images_missed"] = export_result.get("images_missed", 0)
    except ImportError:
        result["docx_path"] = None
        result["docx_note"] = "python-docx not installed"

    return result

async def handle_delete_file(file_path: str, reason: str = "") -> dict:
    paths = get_workspace_paths()
    p = _safe_path(file_path)
    if not p.exists():
        return {"error": f"文件不存在: {file_path}"}
    # Safety: only allow deleting from scripts/, charts/, data/ within current workspace
    allowed = [paths.scripts_dir, paths.charts_dir, paths.data_dir]
    p_resolved = p.resolve()
    if not any(str(p_resolved).startswith(str(d.resolve())) for d in allowed):
        return {"error": f"不允许删除该路径的文件: {file_path}"}
    try:
        size = p.stat().st_size
        p.unlink()
        return {"status": "deleted", "file_path": file_path, "size_bytes": size, "reason": reason}
    except Exception as e:
        return {"error": str(e)}

async def handle_fetch_url(url: str, max_chars: int = 10000) -> dict:
    """抓取网页全文内容，提取纯文本正文。"""
    try:
        import httpx
        from lxml import html as lxml_html
    except ImportError as e:
        return {"url": url, "error": f"依赖未安装: {e}"}

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            resp.raise_for_status()

        tree = lxml_html.fromstring(resp.text)
        # Remove unwanted elements
        for tag in tree.xpath('//script | //style | //nav | //footer | //header | //noscript | //iframe'):
            try:
                tag.getparent().remove(tag)
            except Exception:
                pass

        title = ''
        title_el = tree.xpath('//title')
        if title_el and title_el[0].text:
            title = title_el[0].text.strip()

        body = tree.xpath('//body')
        root = body[0] if body else tree
        text = root.text_content()

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned = '\n'.join(lines)

        content_length = len(cleaned)
        if len(cleaned) > max_chars:
            cleaned = cleaned[:max_chars] + f"\n...[截断，原文共 {content_length} 字符]"

        return {
            "url": url,
            "title": title,
            "text": cleaned,
            "content_length": content_length,
        }
    except httpx.TimeoutException:
        return {"url": url, "error": "请求超时 (15s)"}
    except httpx.HTTPStatusError as e:
        return {"url": url, "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"url": url, "error": str(e)}


async def handle_deep_research(topic: str, num_sources: int = 5) -> dict:
    """一键深度研究：搜索网页 → 全文抓取 → 汇总。"""
    material = []

    # Search web
    try:
        web_results = await handle_search_literature(topic, max_results=num_sources)
        material.append({
            "source_type": "web",
            "label": "网页搜索结果 (DuckDuckGo)",
            "results": web_results.get("results", [])[:num_sources],
        })
    except Exception as e:
        material.append({"source_type": "web", "label": "网页搜索", "error": str(e), "results": []})

    # Fetch full content from web URLs
    fetched = []
    urls_to_fetch = []
    for src in material:
        if src["source_type"] == "web":
            for r in src.get("results", []):
                if r.get("url") and not r["url"].endswith(".pdf"):
                    urls_to_fetch.append(r["url"])

    for url in urls_to_fetch[:num_sources]:
        try:
            content = await handle_fetch_url(url, max_chars=5000)
            if "error" not in content:
                fetched.append({
                    "url": url,
                    "title": content.get("title", ""),
                    "text": content.get("text", "")[:3000],
                })
        except Exception:
            pass

    total_sources = sum(len(src.get("results", [])) for src in material)

    return {
        "topic": topic,
        "sources_found": total_sources,
        "fetched_count": len(fetched),
        "research_material": material,
        "fetched_content": fetched,
    }


TOOL_HANDLERS = {
    "read_file": handle_read_file,
    "write_file": handle_write_file,
    "execute_code": handle_execute_code,
    "search_literature": handle_search_literature,
    "analyze_data": handle_analyze_data,
    "generate_chart": handle_generate_chart,
    "record_experiment": handle_record_experiment,
    "report_iteration": handle_report_iteration,
    "write_paper": handle_write_paper,
    "delete_file": handle_delete_file,
    "fetch_url": handle_fetch_url,
    "deep_research": handle_deep_research,
}