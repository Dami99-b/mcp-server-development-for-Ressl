import os
import json
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

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
