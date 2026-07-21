import os
import json
import urllib.request
import urllib.error
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("File Search Server")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config() -> dict:
    defaults = {"max_results": 50, "case_sensitive": False}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            defaults.update(json.load(f))
    return defaults

@mcp.tool()
def search_keyword(file_path: str, keyword: str, case_sensitive: bool = False) -> dict:
    """Search a file for a keyword and return matching lines with line numbers."""
    config = load_config()
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    matches = []
    use_case = case_sensitive or config.get("case_sensitive")
    for line_num, line in enumerate(lines, start=1):
        haystack, needle = (line, keyword) if use_case else (line.lower(), keyword.lower())
        if needle in haystack:
            matches.append({"line": line_num, "text": line.strip()})
        if len(matches) >= config.get("max_results", 50):
            break

    return {"file": file_path, "keyword": keyword, "match_count": len(matches), "matches": matches}

@mcp.tool()
def list_files(directory: str = ".") -> list[str]:
    """List files in a directory that can be searched."""
    if not os.path.isdir(directory):
        return [f"Not a directory: {directory}"]
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

@mcp.tool()
def triage_finding(finding_text: str) -> dict:
    """Send a security/audit finding to a local, offline LLM (via llama-server) for a
    plain-English explanation, a severity rating, and a suggested fix. Requires
    llama-server to already be running locally — start it with something like:
    ./build/bin/llama-server -hf ggml-org/gemma-3-1b-it-GGUF
    """
    config = load_config()
    server_url = config.get("llama_server_url", "http://127.0.0.1:8080")

    prompt = (
        "You are a smart contract security auditor assistant. Given the finding "
        "below, respond with exactly three sections:\n"
        "1. Plain-English explanation\n"
        "2. Severity rating (Critical/High/Medium/Low) with one-line justification\n"
        "3. Suggested fix\n\n"
        f"Finding:\n{finding_text}"
    )

    payload = json.dumps({
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 512,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{server_url}/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            content = result["choices"][0]["message"]["content"]
            return {"finding": finding_text, "triage": content}
    except urllib.error.URLError as e:
        return {
            "error": (
                f"Could not reach llama-server at {server_url} ({e}). "
                "Is it running? Start it with: "
                "./build/bin/llama-server -hf ggml-org/gemma-3-1b-it-GGUF"
            )
        }
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        return {"error": f"Unexpected response format from llama-server: {e}"}

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
