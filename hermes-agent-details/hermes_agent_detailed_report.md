# Hermes Agent: Comprehensive System Architecture and Walkthrough Report

## 1. Executive Summary & Overview
**Hermes Agent** is a highly capable, self-improving AI agent built by Nous Research. It is designed to act as a robust autonomous assistant featuring a "closed learning loop," meaning it can create skills from experience, improve them during use, autonomously persist knowledge, and establish a profound model of user preferences across multiple sessions. 

The agent is decoupled from the host device—it can run on a $5 VPS, a GPU cluster, or on serverless infrastructure, allowing seamless control via messaging apps like Telegram, Slack, or a local terminal. Built to be model-agnostic, Hermes enables fast swapping between providers such as OpenRouter, Anthropic, OpenAI, or local instances (LM Studio, Ollama) without any codebase changes. 

## 2. Entry Points and Modes of Operation
The system is built around two primary entry points that eventually funnel down to the exact same AI inference loop. 

### 2.1 The Command-Line Interface (CLI)
The local entry point is invoked via the `hermes` command. This uses a sophisticated terminal orchestrator (`cli.py`).
- **Classic Prompt Toolkit:** For standard interaction, featuring robust multiline editing, rich syntax highlighting, and slash-command completions. 
- **Modern TUI (`--tui`):** A fully-fledged Terminal User Interface built with React/Ink running on a Node.js process (`ui-tui`), communicating via JSON-RPC over `stdio` to the Python backend (`tui_gateway`). This renders the chat transcript, tool execution states, interactive approval prompts, and system status natively in the terminal.

### 2.2 The Messaging Gateway
The secondary entry point is the gateway daemon (`hermes gateway`).
- Acts as a message broker between external platforms (Discord, Slack, WhatsApp, Telegram, etc.) and the agent core.
- Allows users to maintain persistent contextual conversations with the agent from anywhere. 
- Platform adapters map the unique data structures of external APIs (like Slack threads or Telegram chats) into a unified `Event` schema that the Hermes core understands.

### 2.3 Initialization Flow
Whether started via CLI or Gateway, the initialization executes the following sequence:
1. **Config Loading:** Resolves settings from `~/.hermes/config.yaml` and environment secrets from `~/.hermes/.env` (using `load_cli_config()` or raw gateway loaders).
2. **Session and State Resolution:** Hermes utilizes a SQLite database (FTS5 enabled) through `hermes_state.py` to manage chat states, preventing memory losses across restarts.
3. **Agent Instantiation:** An `AIAgent` object is instantiated with the loaded configuration, system prompts, API keys, and model parameters.

---

## 3. Core Architecture and Design Philosophy
The system is architected around the `run_agent.py` file, which houses the primary `AIAgent` class (~12k LOC). 

### 3.1 The Agent Loop (`run_conversation`)
The AI interaction is strictly deterministic, entirely synchronous within its loop, and relies on an iteration budget mechanism.
1. **Preparation:** Formats the system prompt by appending dynamic context like memory, platform-specific hints, identity blocks (e.g., from `SOUL.md`), and loaded context files. 
2. **Inference Loop:** Runs a bounded loop (governed by `max_iterations`).
3. **Yield / Complete:** A single inference turn may either yield a final markdown response or yield a sequence of tool requests. 

### 3.2 State Management and Context
`hermes_state.py` acts as the single source of truth for conversational histories.
- By using SQLite with Full-Text Search (FTS5), Hermes enables cross-session memory recall. 
- The `ContextCompressor` dynamically manages token budgets by compressing trailing dialogues when approaching the context window limits.

### 3.3 Extensibility through Plugins
Hermes uses a robust plugin architecture to cleanly separate auxiliary functionality from the core agent logic.
- Plugins are placed in `~/.hermes/plugins/`.
- Capabilities range from hooking into new LLM inference backends, embedding memory stores (like Mem0 or SuperMemory), to dynamic context injection.

---

## 4. Tool Interfacing, Registries, and Environments
Hermes doesn't just parse text; it takes action. Its tool system is heavily optimized and secure.

### 4.1 The Tool Registry (`tools/registry.py`)
All tools register themselves via a centralized decorator pattern. 
- Tool files (`tools/*.py`) define a function and immediately call `registry.register()`.
- Registration requires metadata: name, description, schema (JSON schema for arguments), the handler function, and environmental preconditions (`check_requirements`).

### 4.2 Toolsets
Instead of exposing all tools simultaneously (which balloons the system prompt and confuses the model), tools are grouped into "toolsets" in `toolsets.py` (e.g., core, web-browsing, dev-tools). 
- Only enabled toolsets have their schemas serialized to the LLM. 
- Toolsets act as permission boundaries.

### 4.3 Tool Execution & Environments
When the model emits a `tool_call`:
1. `model_tools.py::handle_function_call()` is invoked.
2. The arguments are validated against the schema.
3. **Security:** If the tool modifies the filesystem or runs commands, it hooks into an environment sandbox (like Docker, Singularity, Daytona, or Modal). Some actions trigger a manual CLI approval prompt (or gateway message).
4. **Execution:** The handler executes, returns JSON data, and `run_agent.py` injects this as a `tool` role message into the transcript.

---

## 5. Backend: Gateway and Message Orchestration
The gateway (`gateway/run.py` and `gateway/platforms/`) is the central nervous system for decoupled execution.

### 5.1 Platform Adapters
Each platform adapter transforms platform-specific webhooks or polling events into standard formats. 
- Handles the uploading and formatting of multimodal payloads (images, voice memos).
- Manages message queuing to ensure that if a user sends 5 messages rapidly, the AI processes them coherently without duplicate thread creation.

### 5.2 Slash Commands in the Backend
Slash commands (e.g., `/memory`, `/model`) are uniformly defined in `hermes_cli/commands.py`. The gateway natively parses these and resolves aliases before invoking standard command handlers, keeping feature parity between Discord/Telegram and the local CLI.

---

## 6. Frontend: User Interfaces and Visual Identity
Hermes treats its aesthetic and user experience as a first-class priority, breaking away from standard raw terminal outputs.

### 6.1 The Ink React TUI
For advanced local rendering, `ui-tui/` builds an interactive terminal UI using Node.js and React Ink.
- **Process Model:** The TS/React code owns the UI, while a Python JSON-RPC subprocess handles the AI loop. 
- **Features:** Streaming chat responses, animated "thinking" states (`KawaiiSpinner`), multi-select approval prompts, and visual demarcation of reasoning blocks vs final text.

### 6.2 The Skin Engine
The aesthetic of the terminal is configurable purely via data.
- Found in `hermes_cli/skin_engine.py`, skins are YAML definitions specifying colors (border, text, accent), spinner types (verbs, faces, wings), tool prefixes, and agent names. 
- Users can switch aesthetics immediately with `/skin`.

### 6.3 PTY Bridge (Web Dashboard)
For browser-based interfaces, Hermes avoids duplicating logic. The web server uses a `ptyprocess` bridge to attach a native `hermes --tui` process to an xterm.js WebGL canvas on the frontend, guaranteeing 100% feature parity.

---

## 7. End-to-End Walkthrough: A Single Request
To summarize the system, here is what happens when a user types a command that requires action:

1. **Input Intake:** The user types "Find the highest CPU process and kill it" in the Ink TUI.
2. **Submission:** `ui-tui` sends a `prompt.submit` JSON-RPC event to the Python `tui_gateway`.
3. **Context Construction:** The Python gateway fetches session history from SQLite, packages the environment context, and initializes `AIAgent.run_conversation()`.
4. **Model Request #1:** The API receives the messages and the `tool_schemas` for system inspection.
5. **Tool Decision:** The model responds with a tool call `run_command(command="top -b -n 1")`.
6. **Execution & UI:** The `tui_gateway` relays `tool.start` to `ui-tui`, which renders a spinner ("Executing..."). The registry routes the call to the terminal sandbox. 
7. **Model Request #2:** The output of `top` is injected into the context, and the model is pinged again. 
8. **Approval Request:** The model decides to run `kill -9 <PID>`. Because this is destructive, a callback stops execution and surfaces an `approval.request` UI prompt.
9. **Finalization:** The user approves, the process is killed, and the model synthesizes a final markdown response which streams character-by-character back to the UI.

---

## 8. Advanced Mechanics
- **Subagents:** The system can spawn parallel isolated instances of `AIAgent` (`agent/agent_init.py`) for background work, coordinated by the main agent. 
- **Trajectory Compression:** Raw event loops are saved as trajectories and can be compressed for distillation (training specialized smaller models).
- **Scheduled Automations (Cron):** A daemon (`cron/jobs.py`) operates alongside the gateway to trigger agent actions asynchronously without human input.
- **MCP Integration:** Allows binding to external Model Context Protocol servers to instantaneously map third-party ecosystems as tools.

*End of Report.*
