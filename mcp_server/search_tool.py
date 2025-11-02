import sys
import os
	
def search_keyword(file_path, keyword):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    found = False
    for line_num, line in enumerate(lines, start=1):
        if keyword.lower() in line.lower():
            print(f"[Line {line_num}] {line.strip()}")
            found = True

    if not found:
        print("No matches found.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python search_tool.py <file_path> <keyword>")
    else:
        search_keyword(sys.argv[1], sys.argv[2])