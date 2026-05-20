# Hermes Agent: Code-Level Deep Dive & Technical Rundown

This document provides a highly technical look at the internals of Hermes Agent, featuring the actual Python classes, function signatures, imports, and object pipelines that make the system tick.

---

## 1. The Core Agent Loop (`run_agent.py` & `agent/agent_runtime_helpers.py`)

The `AIAgent` class is the central coordinator of the system. While the file `run_agent.py` is over 4,000 lines long, it makes extensive use of the `agent/` subdirectory to modularize the logic.

### AIAgent Initialization
The `AIAgent` is instantiated with configurations loaded from the CLI or Gateway. It forwards to `init_agent` inside `agent/agent_init.py`.

```python
# run_agent.py
class AIAgent:
    def __init__(self, base_url: str = None, api_key: str = None, provider: str = None, ...):
        from agent.agent_init import init_agent
        init_agent(self, base_url=base_url, api_key=api_key, provider=provider, ...)

    def _ensure_db_session(self) -> None:
        # Create session DB row on first use using SQLite FTS5 store
        try:
            from hermes_state import SessionDB
            self._session_db.create_session(
                session_id=self.session_id,
                source=self.platform or os.environ.get("HERMES_SESSION_SOURCE", "cli"),
                model=self.model, ...
            )
        except Exception as e: ...
```

### The `run_conversation` Interface
The main synchronous inference loop relies on `agent.conversation_loop.run_conversation`. It manages the conversation history, streaming callbacks, and task identifiers.

```python
# run_agent.py
def run_conversation(
    self,
    user_message: str,
    system_message: str = None,
    conversation_history: List[Dict[str, Any]] = None,
    task_id: str = None,
    stream_callback: Optional[callable] = None,
    persist_user_message: Optional[str] = None,
) -> Dict[str, Any]:
    """Forwarder — see ``agent.conversation_loop.run_conversation``."""
    from agent.conversation_loop import run_conversation
    return run_conversation(self, user_message, system_message, conversation_history, task_id, stream_callback, persist_user_message)
```

---

## 2. Tool Registration & Dispatch (`tools/registry.py`)

Rather than hardcoding tool references in `model_tools.py`, Hermes Agent uses a centralized dynamic registry. Tools register themselves upon import.

### The Tool Entry & Registry Class
Each tool uses a `ToolEntry` object to store its JSON schema and execution metadata.

```python
# tools/registry.py
class ToolEntry:
    __slots__ = ("name", "toolset", "schema", "handler", "check_fn", "requires_env", "is_async", ...)

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolEntry] = {}
        self._toolset_checks: Dict[str, Callable] = {}
        self._lock = threading.RLock()
        self._generation: int = 0
```

### Registration Logic
A tool file calls `registry.register()`, validating that it doesn't accidentally overwrite existing tools (unless explicitly requested via plugins/MCP).

```python
# tools/registry.py
def register(self, name: str, toolset: str, schema: dict, handler: Callable, check_fn: Callable = None, ...):
    with self._lock:
        existing = self._tools.get(name)
        if existing and existing.toolset != toolset:
            if not override:
                logger.error("Tool registration REJECTED: '%s' would shadow existing tool...", name)
                return
        self._tools[name] = ToolEntry(...)
```

---

## 3. Tool Execution & Argument Coercion (`model_tools.py`)

When the LLM decides to emit a tool call, `handle_function_call` bridges the LLM's raw output to the `ToolRegistry`. 

### The Dispatcher (`handle_function_call`)
```python
# model_tools.py
def handle_function_call(
    function_name: str,
    function_args: Dict[str, Any],
    task_id: Optional[str] = None,
    tool_call_id: Optional[str] = None,
    ...
) -> str:
    # 1. Coerce LLM string arguments to strict schema types (e.g. "42" -> 42)
    function_args = coerce_tool_args(function_name, function_args)

    try:
        # 2. Prevent the model from invoking internal loops
        if function_name in _AGENT_LOOP_TOOLS:
            return json.dumps({"error": f"{function_name} must be handled by the agent loop"})

        # 3. Check plugin hooks for interception
        from hermes_cli.plugins import invoke_hook
        # ... invoke pre_tool_call hooks ...

        # 4. Execute the tool via registry
        result = registry.dispatch(
            function_name, function_args,
            task_id=task_id, user_task=user_task
        )

        # 5. Apply transform hooks
        hook_results = invoke_hook("transform_tool_result", ...)
        for hook_result in hook_results:
            if isinstance(hook_result, str):
                result = hook_result
                break

        return result
    except Exception as e:
        error_msg = f"Error executing {function_name}: {str(e)}"
        return json.dumps({"error": _sanitize_tool_error(error_msg)}, ensure_ascii=False)
```

### Argument Coercion
LLMs often hallucinate types, such as passing arrays as JSON strings, or numbers as strings. `coerce_tool_args` repairs this dynamically.

```python
# model_tools.py
def _coerce_value(value: str, expected_type, schema: dict | None = None):
    if expected_type in {"integer", "number"}:
        return _coerce_number(value, integer_only=(expected_type == "integer"))
    if expected_type == "boolean":
        return _coerce_boolean(value)
    if expected_type == "array":
        return _coerce_json(value, list)
    if expected_type == "object":
        return _coerce_json(value, dict)
    return value
```

---

## 4. The Command Line Interface (`cli.py`)

The Hermes CLI isn't just a simple loop; it heavily configures terminal properties, dynamically binds prompt-toolkit keys, and parses slash commands.

```python
# cli.py
class HermesCLI:
    def __init__(self, model: str = None, toolsets: List[str] = None, ...):
        self.config = CLI_CONFIG
        self.compact = compact if compact is not None else CLI_CONFIG["display"].get("compact", False)
        
        # Tool progress UI modes ("off", "new", "all", "verbose")
        self.tool_progress_mode = str(CLI_CONFIG["display"].get("tool_progress", "all"))
        
        # Configuration - priority: CLI args > env vars > config file
        self.model = model or _config_model or _DEFAULT_CONFIG_MODEL
        
        # SQLite DB Initialization
        try:
            from hermes_state import SessionDB
            self._session_db = SessionDB()
        except Exception as e:
            logger.warning("Failed to initialize SessionDB...")

        # Setup prompt toolkit queue & state
        self._pending_input = queue.Queue()
        self._interrupt_queue = queue.Queue()
```

### CLI Redraws & Resize
The CLI implements safe terminal resizing handlers without duplicating prompts:
```python
# cli.py
def _force_full_redraw(self) -> None:
    # Used to recover from terminal buffer drift (e.g. macOS tmux tab switches).
    app = getattr(self, "_app", None)
    if not app: return
    self._clear_prompt_toolkit_screen(app)
    _replay_output_history()
    try:
        app.invalidate()
    except Exception: pass
```

---

## 5. Gateway Initialization (`gateway/run.py`)

The `gateway` module makes the agent accessible remotely. It bootstraps the environment heavily before ever invoking an HTTP client.

```python
# gateway/run.py

# Bridge config.yaml values into the environment so os.getenv() picks them up.
# config.yaml is authoritative for terminal settings — overrides .env.
_config_path = _hermes_home / 'config.yaml'
if _config_path.exists():
    try:
        import yaml as _yaml
        with open(_config_path, encoding="utf-8") as _f:
            _cfg = _yaml.safe_load(_f) or {}
        from hermes_cli.config import _expand_env_vars
        _cfg = _expand_env_vars(_cfg)

        # Bridge configuration to env vars
        _terminal_cfg = _cfg.get("terminal", {})
        if _terminal_cfg and isinstance(_terminal_cfg, dict):
            _terminal_env_map = {
                "backend": "TERMINAL_ENV",
                "cwd": "TERMINAL_CWD",
                "docker_image": "TERMINAL_DOCKER_IMAGE",
                # ...
            }
            for _cfg_key, _env_var in _terminal_env_map.items():
                if _cfg_key in _terminal_cfg:
                    os.environ[_env_var] = str(_terminal_cfg[_cfg_key])
```

### Gateway Message Sanitization
The gateway protects external platforms (like Telegram) from noisy or adversarial outputs (like `[REDACTED]` keys or API HTTP 400 tracebacks).

```python
# gateway/run.py
def _sanitize_gateway_final_response(platform: Any, text: str) -> str:
    """Sanitize final gateway replies before sending them to high-noise chats."""
    if not text: return text
    if _gateway_platform_value(platform) != "telegram":
        return text

    redacted = _redact_gateway_user_facing_secrets(str(text))
    if _looks_like_gateway_provider_error(redacted):
        return _gateway_provider_error_reply(redacted)
    return redacted
```

---

## 6. Summary of Key Imports & Object Pipelines

1. **`AIAgent` Object Pipeline:**
   - CLI creates `HermesCLI` -> which instantiates `AIAgent` -> which initializes `SessionDB`.
   - On Prompt: `AIAgent.run_conversation()` -> Model generates `tool_call` -> `handle_function_call()` -> `registry.dispatch()` -> Executes target function -> Returns `tool_result()` -> Pushed to context window -> Model generates `final_response`.

2. **Key Module Relationships:**
   - **`run_agent.py`**: Defers heavy logic to `agent/*` (e.g. `agent_init.py`, `conversation_loop.py`).
   - **`model_tools.py`**: Interacts dynamically with `tools/registry.py`, ensuring no hard-coded function maps.
   - **`gateway/run.py`**: Orchestrates `Platform` objects from `gateway/platforms/` to push events into `GatewayRunner` which acts as a bridge to `AIAgent`.
   - **`hermes_cli/commands.py`**: Central definitions for slash commands that both the Gateway and the CLI ingest.

*End of Deep Dive.*
