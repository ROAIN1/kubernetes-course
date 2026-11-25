"""Build a .ipynb from a plain-text source.

Source format: cells are separated by a line that is exactly
    ##MD      -> following lines form a markdown cell
    ##CODE    -> following lines form a code cell (use %%bash / %%writefile magics)
Usage: python3 mknb.py _src/03-workloads.txt 03-Workloads.ipynb
"""
import json, sys

def build(src, dst):
    cells, kind, buf = [], None, []
    def flush():
        if kind and "".join(buf).strip():
            text = "".join(buf).strip("\n") + "\n"
            lines = text.splitlines(keepends=True)
            lines[-1] = lines[-1].rstrip("\n")
            cell = {"cell_type": "markdown" if kind == "md" else "code", "metadata": {}, "source": lines}
            if kind == "code":
                cell.update(execution_count=None, outputs=[])
            cells.append(cell)
    for line in open(src, encoding="utf-8"):
        tag = line.strip()
        if tag in ("##MD", "##CODE"):
            flush(); kind, buf = tag[2:].lower(), []
        else:
            buf.append(line)
    flush()
    nb = {"cells": cells, "nbformat": 4, "nbformat_minor": 5,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python"}}}
    json.dump(nb, open(dst, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"{dst}: {len(cells)} cells")

if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
