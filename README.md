# mcp-server-development-for-Ressl
A JSON-RPC compliant MCP (Model Context Protocol) server exposing file-search and
local LLM-triage tools, built with FastMCP.

## Tools

### `search_keyword(file_path, keyword, case_sensitive=False)`
Searches a file for a keyword and returns matching lines with line numbers.
Behavior (max results, default case sensitivity) is configurable via `config.json`.

### `list_files(directory=".")`
Lists searchable files in a directory.

### `triage_finding(finding_text)`
Sends a security/audit finding to a **local, offline LLM** for a plain-English
explanation, severity rating, and suggested fix — no cloud API call, no data
leaves the machine. Requires a local `llama-server` instance running first
(see [llama.cpp](https://github.com/ggml-org/llama.cpp)):
