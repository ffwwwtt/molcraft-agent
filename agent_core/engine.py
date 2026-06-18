"""???? Agent ????

??:
    User Goal -> Engine -> LLM (tool calling) -> Tool Handlers -> Results
                        |_____ iteration loop _____|

??:
    - context_compress: Each round auto-generates summary to replace verbose tool history
    - tool_cache: read_file/execute_code/analyze_data cache by arg hash
"""
import asyncio
import hashlib
import json
import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, Any

import httpx
from openai import AsyncOpenAI

BASE_DIR = Path(__file__).resolve().parent.parent

MAX_CACHE_ENTRIES = 200

def _cache_key(tool_name: str, arguments: dict) -> str:
    raw = json.dumps({"tool": tool_name, "args": arguments}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


class ResearchAgent:
    def __init__(self, api_key: str, base_url: str, model: str,
                 tools: list[dict], tool_handlers: dict[str, Callable[..., Any]],
                 system_prompt: str = "", temperature: float = 0.3,
                 max_tool_calls_per_round: int = 200,
                 trace_log_path: Optional[Path] = None):
        # ── Custom httpx client with connection pooling and granular timeouts ──
        self._http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=10.0,    # TLS handshake + TCP connect
                read=120.0,      # Time between data chunks (streaming) or total read
                write=30.0,      # Time to send request body
                pool=10.0,       # Time to acquire a connection from the pool
            ),
            limits=httpx.Limits(
                max_keepalive_connections=10,
                max_connections=20,
                keepalive_expiry=30.0,
            ),
        )
        self.client = AsyncOpenAI(
            api_key=api_key, base_url=base_url,
            http_client=self._http_client,
            max_retries=0,  # We handle retries ourselves with exponential backoff
        )
        self.model = model
        self.tools = tools
        self.tool_handlers = tool_handlers
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tool_calls_per_round = max_tool_calls_per_round
        self.trace_log_path = trace_log_path
        self.write_paper = False
        self.tool_cache: dict[str, dict] = {}
        self.cache_hits = 0
        self.cache_misses = 0

        self.checkpoint_path = None  # type: Optional[Path]
        self._current_messages = []  # type: list[dict]
        self.on_tool_call = None  # Optional async callback(tool_name, args, result) — after execution
        self.on_tool_start = None  # Optional async callback(tool_name, args) — before execution
        self.on_thinking_chunk = None  # Optional callback(chunk_text: str) — called per-streaming-delta
        self.on_tool_call_chunk = None  # Optional callback(tool_name: str, chunk: str) — per-delta for tool args
        self._last_usage = None  # Usage from most recent API call
        self.cumulative_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        self._last_api_latency = None  # dict: {ttfb_s, total_s, token_count, status, timestamp}
        self.on_api_latency = None  # Optional async callback(latency_data: dict)

    async def close(self):
        """Clean up the httpx client and its connection pool."""
        if self._http_client is not None:
            await self._http_client.aclose()

    def log(self, msg: str):
        timestamp = datetime.now().isoformat()
        line = f"[{timestamp}] {msg}"
        print(line)
        if self.trace_log_path:
            with open(self.trace_log_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

    @staticmethod
    def _truncate_tool_result(tool_name: str, result_content: str, max_chars: int = 8000) -> str:
        if len(result_content) <= max_chars:
            return result_content
        try:
            result_obj = json.loads(result_content)
        except json.JSONDecodeError:
            return result_content[:max_chars] + "\n...[truncated]"
        if isinstance(result_obj, dict):
            kept = {}
            keep_keys = ["exit_code", "error", "stderr", "file_path", "size_bytes",
                         "total_chars", "row_count", "columns", "format", "status",
                         "truncated", "note", "script_path", "output_file",
                         "chart_path", "chart_type", "title", "message",
                         "record_count", "count", "docx_path", "paper_path",
                         "images_embedded", "images_missed", "query", "results"]
            for key in keep_keys:
                if key in result_obj:
                    val = result_obj[key]
                    if isinstance(val, str) and len(val) > 500:
                        val = val[:500] + "..."
                    kept[key] = val
            for text_key in ["stdout", "content"]:
                if text_key in result_obj:
                    raw = result_obj[text_key]
                    if isinstance(raw, str) and len(raw) > 1000:
                        kept[text_key] = raw[:1000] + f"\n...[truncated, total {len(raw)} chars]"
                    else:
                        kept[text_key] = raw
            kept["_truncated_from"] = len(result_content)
            return json.dumps(kept, ensure_ascii=False)
        return result_content[:max_chars] + "\n...[truncated]"

    async def _compress_tool_history(self, messages: list[dict], research_goal: str) -> str:
        summary_input = []
        for msg in messages:
            if msg["role"] == "assistant" and msg.get("tool_calls"):
                for tc in msg["tool_calls"]:
                    fn = tc.get("function", {})
                    name = fn.get("name", "")
                    try:
                        args = json.loads(fn.get("arguments", "{}"))
                    except json.JSONDecodeError:
                        args = fn.get("arguments", "")
                    args_str = json.dumps(args, ensure_ascii=False)
                    if len(args_str) > 300:
                        args_str = args_str[:300] + "..."
                    summary_input.append(f"Call: {name}({args_str})")
            elif msg["role"] == "tool":
                content = msg.get("content", "")
                try:
                    obj = json.loads(content)
                    if isinstance(obj, dict):
                        brief = {}
                        for k in ["exit_code", "error", "row_count", "status", "count",
                                  "chart_type", "title", "summary"]:
                            if k in obj:
                                brief[k] = obj[k]
                        content = json.dumps(brief, ensure_ascii=False)
                except json.JSONDecodeError:
                    pass
                if len(content) > 500:
                    content = content[:500] + "..."
                summary_input.append(f"Result: {content}")
        if not summary_input:
            return ""
        input_text = "\n".join(summary_input)
        if len(input_text) > 15000:
            input_text = input_text[:15000] + "\n...[truncated]"
        prompt = f"????: {research_goal}\n\n??? Agent ??????????? 200-400 ??????????????:\n{input_text}\n\n??:"
        _compress_start = time.perf_counter()
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2, max_tokens=600, stream=False)
            _compress_elapsed = time.perf_counter() - _compress_start
            summary = resp.choices[0].message.content.strip()
            # Capture usage from compress call (non-streaming, so resp.usage is available)
            if resp.usage:
                compress_usage = {
                    "prompt_tokens": resp.usage.prompt_tokens,
                    "completion_tokens": resp.usage.completion_tokens,
                    "total_tokens": resp.usage.total_tokens,
                }
                for k in self.cumulative_usage:
                    self.cumulative_usage[k] += compress_usage.get(k, 0)
            self.log(f"[compress] {_compress_elapsed:.1f}s | summary: {summary[:200]}...")
            return summary
        except Exception as e:
            _compress_elapsed = time.perf_counter() - _compress_start
            self.log(f"[compress] failed after {_compress_elapsed:.1f}s: {e}")
            return ""

    # --- Checkpoint / Resume ---

    def save_checkpoint(self, iteration, step):
        """Save current progress to checkpoint file."""
        if not self.checkpoint_path:
            return
        try:
            import json as _json
            data = {
                "iteration": iteration,
                "step": step,
                "messages": self._current_messages,
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
            }
            self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            self.checkpoint_path.write_text(_json.dumps(data, ensure_ascii=False, default=str), encoding="utf-8")
        except Exception as e:
            self.log(f"[checkpoint] save failed: {e}")

    def load_checkpoint(self):
        """Load checkpoint. Returns (iteration, step, messages)."""
        if not self.checkpoint_path or not self.checkpoint_path.exists():
            return 0, 0, []
        try:
            import json as _json
            data = _json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
            it = data.get("iteration", 0)
            st = data.get("step", 0)
            msgs = data.get("messages", [])
            self.log(f"[checkpoint] loaded: iteration={it}, step={st}, messages={len(msgs)}")
            return it, st, msgs
        except Exception as e:
            self.log(f"[checkpoint] load failed: {e}")
            return 0, 0, []

    def clear_checkpoint(self):
        """Remove checkpoint file."""
        if self.checkpoint_path and self.checkpoint_path.exists():
            try:
                self.checkpoint_path.unlink()
            except Exception:
                pass

    async def run_round(self, research_goal: str,
                         stop_event: Optional[asyncio.Event] = None,
                         previous_summary: str = "") -> dict:
        system_content = self.system_prompt
        if self.write_paper:
            system_content += (
                "\n\n[Important] This experiment requires a research paper."
                " Call write_paper tool after all iterations to generate a full paper"
                " including title, abstract, introduction, methods, results, discussion, and conclusion."
            )
        user_content = research_goal
        if previous_summary:
            user_content = (
                f"{research_goal}\n\n"
                f"[Previous Round Summary]\n{previous_summary}\n\n"
                f"Continue based on the summary above. Do not repeat completed work."
            )
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]
        self._current_messages = messages
        step = 0
        last_report = {}
        retry_count = 0
        max_retries = 5

        while step < self.max_tool_calls_per_round:
            if stop_event and stop_event.is_set():
                break
            step += 1

            # ── Inactivity watchdog: abort if no response for 120s ──
            _last_active = [time.time()]  # mutable container for closure updates
            stream_task = None  # will hold the cancellable streaming task

            async def _inactivity_guard():
                while not (stop_event and stop_event.is_set()):
                    await asyncio.sleep(5)
                    if time.time() - _last_active[0] > 120:
                        self.log("[TIMEOUT] ⏰ 超过 120 秒无响应，强制停止")
                        if stream_task and not stream_task.done():
                            stream_task.cancel()  # truly abort the blocked I/O
                        if stop_event:
                            stop_event.set()
                        break

            guard_task = asyncio.create_task(_inactivity_guard())

            # ── Per-API-call timing ──
            _api_start = time.perf_counter()
            _first_token_time = None
            _token_count = 0

            try:
                response = await self.client.chat.completions.create(
                    model=self.model, messages=messages, tools=self.tools,
                    tool_choice="auto", temperature=self.temperature,
                    stream=True, stream_options={"include_usage": True})
            except Exception as exc:
                _api_elapsed = time.perf_counter() - _api_start
                guard_task.cancel()
                retry_count += 1
                if retry_count >= max_retries:
                    self.log(f"[API] call failed after {_api_elapsed:.1f}s, max retries ({max_retries}) reached: {exc}")
                    if stop_event: stop_event.set()
                    break
                # Exponential backoff: 2s → 4s → 8s → 16s → 32s (base 2s, cap 60s, ±50% jitter)
                base_delay = 2.0
                backoff = min(base_delay * (2 ** (retry_count - 1)), 60.0)
                jitter = random.uniform(0, backoff * 0.5)
                delay = backoff + jitter
                self.log(
                    f"[API] call failed after {_api_elapsed:.1f}s: {exc}, "
                    f"retrying {retry_count}/{max_retries} in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
                continue
            retry_count = 0

            content_parts = []
            tool_calls_dict = {}
            _stream_tool_names = {}  # idx -> tool name, cached for streaming callbacks

            async def _stream_loop():
                nonlocal content_parts, tool_calls_dict, _first_token_time, _token_count, _stream_tool_names
                async for chunk in response:
                    if _first_token_time is None:
                        _first_token_time = time.perf_counter() - _api_start
                    _token_count += 1
                    _last_active[0] = time.time()  # reset inactivity clock
                    if stop_event and stop_event.is_set():
                        break
                    # Capture usage from final chunk (arrives with empty choices but has chunk.usage)
                    if hasattr(chunk, 'usage') and chunk.usage:
                        self._last_usage = {
                            "prompt_tokens": chunk.usage.prompt_tokens,
                            "completion_tokens": chunk.usage.completion_tokens,
                            "total_tokens": chunk.usage.total_tokens,
                        }

                    delta = chunk.choices[0].delta if chunk.choices else None
                    if not delta:
                        continue
                    if delta.content:
                        content_parts.append(delta.content)
                        if not tool_calls_dict:
                            if self.on_thinking_chunk:
                                self.on_thinking_chunk(delta.content)
                    if delta.tool_calls:
                        for tc_raw in delta.tool_calls:
                            try:
                                if isinstance(tc_raw, dict):
                                    idx = tc_raw.get("index", 0)
                                    fn_raw = tc_raw.get("function", {})
                                    fn_name = fn_raw.get("name", "") if isinstance(fn_raw, dict) else ""
                                    fn_args = fn_raw.get("arguments", "") if isinstance(fn_raw, dict) else ""
                                    fn_id = tc_raw.get("id", "")
                                else:
                                    idx = tc_raw.index
                                    fn_raw = tc_raw.function if hasattr(tc_raw, "function") else {}
                                    fn_name = fn_raw.name if hasattr(fn_raw, "name") else (fn_raw.get("name", "") if isinstance(fn_raw, dict) else "")
                                    fn_args = fn_raw.arguments if hasattr(fn_raw, "arguments") else (fn_raw.get("arguments", "") if isinstance(fn_raw, dict) else "")
                                    fn_id = tc_raw.id or ""
                            except Exception:
                                continue
                            # Cache tool name from first chunk (subsequent chunks only carry arguments)
                            if fn_name:
                                _stream_tool_names[idx] = fn_name
                            # Fire streaming callback for EVERY argument chunk (not just the first)
                            stream_name = fn_name or _stream_tool_names.get(idx, '')
                            if stream_name and self.on_tool_call_chunk and fn_args:
                                try:
                                    self.on_tool_call_chunk(stream_name, fn_args)
                                except Exception:
                                    pass
                            if idx not in tool_calls_dict:
                                tool_calls_dict[idx] = {"id": fn_id, "function": {"name": fn_name, "arguments": fn_args}}
                            else:
                                if fn_args:
                                    tool_calls_dict[idx]["function"]["arguments"] += fn_args

            stream_task = asyncio.create_task(_stream_loop())
            try:
                await stream_task
            except asyncio.CancelledError:
                self.log("Streaming cancelled by timeout watchdog")
            except Exception as _stream_exc:
                self.log(f"Stream error: {_stream_exc}")
            finally:
                # Always cancel the inactivity watchdog and signal end-of-thinking,
                # even if the stream crashed.  Prevents zombie guard tasks and
                # hung thinking bubbles on the frontend.
                guard_task.cancel()
                if content_parts and self.on_thinking_chunk:
                    self.on_thinking_chunk("__END__")

            # Accumulate usage from this API call
            if self._last_usage:
                for k in self.cumulative_usage:
                    self.cumulative_usage[k] += self._last_usage.get(k, 0)

            # ── Log per-API-call timing ──
            _api_total = time.perf_counter() - _api_start
            _ttfb = _first_token_time if _first_token_time is not None else _api_total
            self._last_api_latency = {
                "ttfb_s": round(_ttfb, 2),
                "total_s": round(_api_total, 2),
                "chunk_count": _token_count,
                "status": "ok" if not (stop_event and stop_event.is_set()) else "cancelled",
                "timestamp": datetime.now().isoformat(),
            }
            if self.on_api_latency:
                try:
                    await self.on_api_latency(self._last_api_latency)
                except Exception:
                    pass

            content = "".join(content_parts)
            message = {"role": "assistant", "content": content or None}
            if tool_calls_dict:
                message["tool_calls"] = []
                for idx in sorted(tool_calls_dict.keys()):
                    tc = tool_calls_dict[idx]
                    if tc["id"] and tc["function"]["name"]:
                        import json as _json
                        try:
                            args_parsed = _json.loads(tc["function"]["arguments"])
                        except _json.JSONDecodeError:
                            args_parsed = tc["function"]["arguments"]
                        message["tool_calls"].append({
                            "id": tc["id"], "type": "function",
                            "function": {"name": tc["function"]["name"], "arguments": _json.dumps(args_parsed, ensure_ascii=False)}
                        })
            messages.append(message)
            if content:
                print()

            has_tc = len(message.get("tool_calls", [])) > 0 if isinstance(message, dict) else False
            if not has_tc:
                self.log("No more tool calls, round done.")
                break

            tool_calls = message.get("tool_calls", [])
            for tool_call in tool_calls:
                if stop_event and stop_event.is_set():
                    break
                if isinstance(tool_call, dict):
                    func = tool_call.get("function", {})
                    tool_name = func.get("name", "") if isinstance(func, dict) else ""
                    args_str = func.get("arguments", "{}") if isinstance(func, dict) else "{}"
                else:
                    func = tool_call.function
                    tool_name = func.name
                    args_str = func.arguments
                arguments = self._safe_parse_args(args_str)

                args_preview = json.dumps(arguments, ensure_ascii=False)[:250]
                self.log(f"[TOOL] {tool_name} | {args_preview}")

                use_cache = tool_name in ("read_file", "execute_code", "analyze_data")
                cache_hit = False
                if use_cache:
                    ck = _cache_key(tool_name, arguments)
                    if ck in self.tool_cache:
                        result = self.tool_cache[ck]
                        self.cache_hits += 1
                        self.log(f"[CACHE] hit #{self.cache_hits} for {tool_name}")
                        cache_hit = True

                if not cache_hit:
                    # Notify BEFORE execution (shows "executing..." in frontend)
                    if self.on_tool_start:
                        try:
                            await self.on_tool_start(tool_name, arguments)
                        except Exception:
                            pass

                    handler = self.tool_handlers.get(tool_name)
                    if handler:
                        try:
                            result = await handler(**arguments)
                        except Exception as exc:
                            result = {"error": str(exc)}
                            self.log(f"[ERROR] {tool_name}: {exc}")
                    else:
                        result = {"error": f"Unknown tool: {tool_name}"}

                    # Notify AFTER execution (shows result in frontend)
                    if self.on_tool_call:
                        try:
                            await self.on_tool_call(tool_name, arguments, result)
                        except Exception:
                            pass


                    if use_cache and "error" not in str(result):
                        if len(self.tool_cache) >= MAX_CACHE_ENTRIES:
                            oldest_key = next(iter(self.tool_cache))
                            del self.tool_cache[oldest_key]
                        self.tool_cache[ck] = result
                        self.cache_misses += 1

                if tool_name == "report_iteration" and isinstance(result, dict):
                    last_report = result

                result_str = json.dumps(result, ensure_ascii=False, default=str)
                result_str = self._truncate_tool_result(tool_name, result_str)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", "") if isinstance(tool_call, dict) else tool_call.id,
                    "content": result_str,
                })
                # Checkpoint after tool call
                self.save_checkpoint(0, step)

        return {"report": last_report, "usage": self._last_usage}

    async def run_iterations(self, research_goal: str,
                              max_iterations: int = 3, max_seconds: int = 5400):
        stop_event = asyncio.Event()
        start_time = time.time()

        async def time_monitor():
            await asyncio.sleep(max_seconds)
            stop_event.set()
            self.log(f"Max time {max_seconds}s reached, stopping.")

        monitor_task = asyncio.create_task(time_monitor())
        results = []
        previous_summary = ""

        try:
            for i in range(max_iterations):
                if stop_event.is_set():
                    break
                self.log(f"{chr(61)*60}")
                self.log(f"Iteration {i+1}/{max_iterations} start")
                self.log(f"{chr(61)*60}")

                report = await self.run_round(research_goal, stop_event, previous_summary)
                results.append(report)

                elapsed = time.time() - start_time
                self.log(f"Iteration {i+1} done ({elapsed:.0f}s)")

                if i < max_iterations - 1:
                    self.log("[compress] Generating round summary...")
                    summary = await self._compress_tool_history([], research_goal)
                    if summary:
                        previous_summary = summary

            return results
        finally:
            monitor_task.cancel()

    @staticmethod
    def _safe_parse_args(args_str: str) -> dict:
        try:
            parsed = json.loads(args_str or "{}")
            # Some API providers double-encode JSON arguments:
            # the raw string is a JSON string like '"{\"key\":...}"'
            # which json.loads returns as a plain string — not a dict.
            # Attempt a second parse if the result is still a string.
            if isinstance(parsed, str):
                try:
                    parsed = json.loads(parsed)
                except (json.JSONDecodeError, TypeError):
                    pass
            if not isinstance(parsed, dict):
                return {"_raw_arguments": args_str, "_parse_error": "result is not a dict"}
            return parsed
        except json.JSONDecodeError:
            return {"_raw_arguments": args_str, "_parse_error": "JSONDecodeError"}
