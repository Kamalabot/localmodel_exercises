# Hermes Agent: End-to-End Gateway Request Trace (Telegram)

Tracing a request from start to finish is one of the most effective ways to understand a complex, distributed codebase. In this walkthrough, we will trace the exact lifecycle of a user sending a message to a Telegram bot powered by Hermes Agent.

This covers the entire pipeline: from webhook ingress, through the session orchestration and tool calling, down to output sanitization and Markdown formatting.

---

## Step 1: Ingress & Media Batching (`gateway/platforms/telegram.py`)

When a user sends a message on Telegram, the `python-telegram-bot` SDK triggers the `TelegramAdapter`.

1. **Message Reception**: The adapter processes the incoming `Update`. It parses the text and extracts any attached media.
2. **Burst Batching**: Users often send bursts of text or a barrage of photos in an album. To prevent Hermes from launching multiple concurrent, overlapping inference turns, the adapter enforces a delay.
    - **Adaptive Text Batching**: Based on length (`_TEXT_BATCH_FAST_LEN`), text waits briefly (e.g., 0.18s or 0.24s) to catch client-side splits.
    - **Media Batching**: Uses `_media_batch_delay_seconds` (default 0.8s) to group rapid album photos into a single `MessageEvent`.
3. **Normalization**: The adapter emits a standardized `MessageEvent` containing the normalized text, media paths, and routing metadata (like `message_thread_id` for Forum topics).

---

## Step 2: Session Caching & Orchestration (`gateway/run.py`)

The standardized event is handed off to the main `GatewayRunner` which daemonizes all messaging platforms.

1. **Session Resolution**: 
    - The runner constructs a `SessionSource` mapping the Telegram User ID, Chat ID, and Chat Type (e.g., `supergroup` or `dm`) to an internal Hermes `session_id`.
    - It queries the SQLite database (`SessionDB`) to pull the existing conversation history.
2. **AIAgent LRU Cache**: 
    - Instantiating an `AIAgent` is expensive (it loads tool schemas, sets up LLM clients, and loads memory providers).
    - To prevent OOM errors in long-running gateways, `gateway/run.py` maintains an LRU Cache of `AIAgent` instances capped at `_AGENT_CACHE_MAX_SIZE = 128`. 
    - Idle agents are evicted automatically after `_AGENT_CACHE_IDLE_TTL_SECS = 3600.0`.
3. **Execution**: The gateway triggers `agent.run_conversation()` synchronously.

---

## Step 3: The Inference & Tool Loop (`run_agent.py` & `model_tools.py`)

This is where the brain of the agent operates.

1. **LLM Invocation**: The `AIAgent` appends the new message to its history and calls the configured inference provider (OpenAI, OpenRouter, Anthropic, etc.) via the unified client interface.
2. **Tool Dispatch (`model_tools.py`)**: 
    - If the LLM decides to use a tool, it outputs a `function_call`.
    - `handle_function_call` intercepts this request. 
    - Because LLMs frequently hallucinate types (e.g. returning the string `"true"` instead of the boolean `true`, or `"42"` instead of `42`), the dispatcher first runs `coerce_tool_args` to match the LLM's raw output against the tool's JSON schema and dynamically repair mismatches.
    - The tool is executed via the `ToolRegistry` and its JSON result is appended to the message history.
3. **Looping**: If the model wants to call more tools, step 3 repeats. Otherwise, it generates a final text response.

---

## Step 4: Sanitization & Safety (`gateway/run.py`)

Before the final LLM text is returned to the user, the gateway runs it through rigorous safety filters, particularly designed for high-noise mobile platforms like Telegram.

1. **Secret Redaction**: 
    - `_redact_gateway_user_facing_secrets(text)` uses Regex patterns (`_GATEWAY_SECRET_PATTERNS`) to scrub leaked API keys, GitHub tokens, and bearer tokens. It replaces them with `[REDACTED]`.
2. **Provider Error Masking**: 
    - If the LLM provider crashes (e.g., HTTP 429 Rate Limit, or a 401 Auth Error), those raw tracebacks shouldn't leak to a Telegram chat.
    - `_looks_like_gateway_provider_error` inspects the text shape. If it's a provider crash, `_gateway_provider_error_reply` replaces the response with a clean user-safe string (e.g., *"⏱️ The model provider is rate-limiting requests. Please wait a moment."*).
3. **Status Suppression**: `_TELEGRAM_NOISY_STATUS_RE` filters out verbose internal telemetry (like "compression summary failed") that the user doesn't need to see.

---

## Step 5: Egress & Markdown Formatting (`gateway/platforms/telegram.py`)

Finally, the sanitized text is handed back to the `TelegramAdapter` for delivery.

1. **Table Conversion**: Telegram's `MarkdownV2` does not support standard GitHub Flavored Markdown (GFM) pipe tables (`| Col | Col |`). 
    - `_wrap_markdown_tables(text)` dynamically parses Markdown tables and rewrites them into bolded row headers and bullet-point groups so they render beautifully on mobile clients.
2. **Syntax Escaping**: 
    - `_escape_mdv2` ensures that structural characters (like `(` or `]`) occurring outside of codeblocks are backslash-escaped to prevent `python-telegram-bot` from throwing parsing exceptions.
3. **Clickable Slash Commands**: 
    - `_telegramize_command_mentions` regex-replaces inline commands to ensure they meet Telegram's strict `a-z0-9_` naming requirements, making sure commands like `/help` remain clickable buttons.
4. **Delivery**: The adapter calls Telegram's `sendMessage` or `editMessageText` (specifically requiring the `finalize=True` path for Markdown execution) to deliver the final product to the user's screen.
