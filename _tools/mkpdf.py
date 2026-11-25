"""Convert the course notebooks (.ipynb) into printable HTML, then PDF via Chrome.

Usage: python3 _tools/mkpdf.py <notebook.ipynb>... --out <dir>
"""
import html, json, os, re, subprocess, sys, tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

HOW_TO = """**How to use this guide**
- Read each section top to bottom. Read the explanation **before** you run a command.
- Grey **Terminal** boxes are commands. Open Terminal, `cd ~/Documents/Learning-Certifications/Kubernetes-Course`, then copy and paste the box.
- Blue **Create file** boxes are also commands: pasting one creates that YAML/config file under `labs/`. Read the comments inside the file first.
- Compare your output with the **Expected output**.
- Quiz answers are in the green **Answer** box under each quiz. Try first, then read."""

CSS = """
@page { size: A4; margin: 16mm 14mm 18mm 14mm;
  @bottom-center { content: counter(page) " / " counter(pages); font: 9px -apple-system, Helvetica, sans-serif; color: #888; } }
* { box-sizing: border-box; }
body { font: 10.5pt/1.5 -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif; color: #1d2330; margin: 0; }
h1 { font-size: 22pt; color: #0b3d91; border-bottom: 3px solid #326ce5; padding-bottom: 6px; margin: 0 0 12px; }
h2 { font-size: 15pt; color: #0b3d91; border-bottom: 1px solid #c9d6f0; padding-bottom: 3px; margin: 22px 0 8px; break-after: avoid; }
h3 { font-size: 12.5pt; color: #1f4fa8; margin: 16px 0 6px; break-after: avoid; }
h4, h5 { font-size: 11pt; margin: 12px 0 4px; break-after: avoid; }
p { margin: 6px 0; }
a { color: #326ce5; text-decoration: none; }
code { font: 9pt "SF Mono", Menlo, Consolas, monospace; background: #eef1f6; padding: 1px 4px; border-radius: 3px; }
pre { font: 8.6pt/1.42 "SF Mono", Menlo, Consolas, monospace; background: #f5f7fa; border: 1px solid #dde3ec;
      border-radius: 5px; padding: 8px 10px; white-space: pre-wrap; word-break: break-word; margin: 6px 0 10px; }
pre code { background: none; padding: 0; font-size: inherit; }
.box { margin: 8px 0 12px; break-inside: avoid-page; }
.box .lbl { font: 600 8pt -apple-system, Helvetica, sans-serif; letter-spacing: .02em; padding: 3px 9px;
            border-radius: 5px 5px 0 0; display: inline-block; }
.box pre { margin: 0; border-radius: 0 5px 5px 5px; }
.term .lbl { background: #2b3445; color: #fff; }
.term pre { background: #1e2533; color: #e6edf3; border-color: #1e2533; }
.file .lbl { background: #326ce5; color: #fff; }
.file pre { background: #f2f6ff; border-color: #b9cdf5; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 9pt; break-inside: auto; }
th, td { border: 1px solid #d3dae6; padding: 4px 6px; vertical-align: top; text-align: left; }
th { background: #e8eefb; }
tr { break-inside: avoid; }
blockquote { border-left: 4px solid #f0a020; background: #fff8ea; margin: 8px 0; padding: 6px 12px; }
.answer { border: 1px solid #9fd3a8; background: #f1faf2; border-radius: 5px; padding: 4px 12px 6px; margin: 8px 0 12px; break-inside: avoid-page; }
.answer .alabel { font-weight: 700; color: #1d7a33; font-size: 9pt; }
hr { border: none; border-top: 1px solid #d3dae6; margin: 16px 0; }
ul, ol { margin: 4px 0 8px; padding-left: 22px; }
li { margin: 2px 0; }
.cover { background: #0b3d91; color: #fff; padding: 14px 18px; border-radius: 8px; margin-bottom: 16px; font-size: 9pt; }
.cover b { font-size: 11pt; }
"""

def fix_wording(s):
    s = re.sub(r"\*\*How to use this notebook\*\*\n(?:[-*] .*\n?)+", HOW_TO + "\n", s)
    s = re.sub(r"\(([^()\s]+)\.ipynb\)", r"(\1.pdf)", s)
    s = re.sub(r"([^\s\[(]+)\.ipynb", r"\1.pdf", s)
    s = re.sub(r"\b[Tt]his notebook\b", lambda m: m.group(0)[0] + "his guide", s)
    s = re.sub(r"\b[Nn]ext notebook\b", lambda m: m.group(0)[0] + "ext guide", s)
    s = re.sub(r"\b[Nn]otebook (\d\d)\b", lambda m: ("P" if m.group(0)[0] == "N" else "p") + "art " + m.group(1), s)
    s = re.sub(r"[Nn]otebooks (\d\d)", r"Parts \1", s)
    s = s.replace("Click **Answer** to open them", "Answers are in the green box below")
    s = s.replace("then click **Answer**", "then read the answer box")
    s = re.sub(r"\s*(Click a cell and press|Press) \*\*Shift ?\+ ?Enter\*\*[^\n]*?(\.|(?=\n))", "", s)
    s = re.sub(r" with \*\*Shift ?\+ ?Enter\*\*", "", s)
    s = re.sub(r"`%%bash` cells?", "**Terminal** boxes", s)
    s = re.sub(r"`%%writefile` cells?", "**Create file** boxes", s)
    s = re.sub(r"[Cc]ells (that )?start(ing)? with `%%bash`", "**Terminal** boxes", s)
    s = re.sub(r"[Cc]ells (that )?start(ing)? with `%%writefile`", "**Create file** boxes", s)
    s = re.sub(r"(?<=\s)each `%%bash` cell", "each Terminal box", s)
    s = re.sub(r"\b([Cc])ell(s?)\b", lambda m: ("S" if m.group(1) == "C" else "s") + "tep" + m.group(2), s)
    return s

# ---------- inline markdown ----------
def inline(t):
    codes = []
    def keep(code):
        codes.append("<code>" + html.escape(code) + "</code>")
        return f"\x00{len(codes)-1}\x00"
    t = re.sub(r"`([^`]+)`", lambda m: keep(m.group(1)), t)
    t = re.sub(r"<code>(.*?)</code>", lambda m: keep(html.unescape(m.group(1))), t)
    t = html.escape(t, quote=False)
    t = re.sub(r"&lt;(/?)(b|br|i|em|strong)\s*/?&gt;", r"<\1\2>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)
    t = re.sub(r"(?<!\w)_(?!\s)([^_]+?)(?<!\s)_(?!\w)", r"<i>\1</i>", t)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], t)

# ---------- block markdown ----------
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")

def md(src):
    lines = src.split("\n")
    out, i = [], 0
    para = []
    def flush():
        if para:
            out.append("<p>" + inline(" ".join(x.strip() for x in para)) + "</p>")
            para.clear()
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if s.startswith("```"):
            flush(); j = i + 1; buf = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                buf.append(lines[j]); j += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
            i = j + 1; continue
        if re.match(r"^<details>", s):
            flush()
            m = re.search(r"<summary>(.*?)</summary>", s)
            label = re.sub(r"<[^>]+>", "", m.group(1)) if m else "Answer"
            out.append(f'<div class="answer"><div class="alabel">✓ {html.escape(label)}</div>')
            rest = re.sub(r"^<details>\s*(<summary>.*?</summary>)?", "", s)
            if rest: lines[i] = rest; continue
            i += 1; continue
        if s == "</details>" or s.endswith("</details>"):
            before = s[:-len("</details>")].strip()
            if before: para.append(before)
            flush(); out.append("</div>"); i += 1; continue
        if re.match(r"^<summary>", s):
            i += 1; continue
        m = re.match(r"^(#{1,5})\s+(.*)", s)
        if m and not ln.startswith(" "):
            flush(); n = len(m.group(1))
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>"); i += 1; continue
        if re.match(r"^(-{3,}|\*{3,})$", s):
            flush(); out.append("<hr>"); i += 1; continue
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?[\s:|-]+\|[\s:|-]*$", lines[i + 1]):
            flush()
            def cells(r):
                r = r.strip()
                r = r[1:] if r.startswith("|") else r
                r = r[:-1] if r.endswith("|") and not r.endswith("\\|") else r
                return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", r)]
            t = ["<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells(ln)) + "</tr></thead><tbody>"]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells(lines[i])) + "</tr>"); i += 1
            out.append("".join(t) + "</tbody></table>"); continue
        if s.startswith(">"):
            flush(); buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].lstrip()); i += 1
            out.append("<blockquote>" + md("\n".join(buf)) + "</blockquote>"); continue
        if LIST_RE.match(ln):
            flush()
            i = parse_list(lines, i, out); continue
        if not s:
            flush(); i += 1; continue
        para.append(ln); i += 1
    flush()
    return "\n".join(out)

def parse_list(lines, i, out):
    """Nested lists by indentation; continuation lines and fenced code inside items."""
    stack = []  # (indent, tag)
    item_open = []
    while i < len(lines):
        ln = lines[i]
        m = LIST_RE.match(ln)
        if m:
            ind = len(m.group(1).expandtabs(4)); tag = "ol" if m.group(2)[0].isdigit() else "ul"
            while stack and ind < stack[-1][0]:
                out.append("</li></%s>" % stack.pop()[1])
            if not stack or ind > stack[-1][0]:
                start = ""
                if tag == "ol" and int(re.match(r"\d+", m.group(2)).group()) != 1:
                    start = f' start="{re.match(r"[0-9]+", m.group(2)).group()}"'
                out.append(f"<{tag}{start}><li>"); stack.append((ind, tag))
            else:
                out.append("</li><li>")
            out.append(inline(m.group(3))); i += 1; continue
        s = ln.strip()
        if not stack: break
        if s.startswith("```") and ln.startswith(" "):
            j = i + 1; buf = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                buf.append(lines[j]); j += 1
            ind = len(ln) - len(ln.lstrip())
            out.append("<pre><code>" + html.escape("\n".join(x[ind:] if x[:ind].strip() == "" else x for x in buf)) + "</code></pre>")
            i = j + 1; continue
        if s and ln.startswith("  ") and not s.startswith("|"):
            out.append(" " + inline(s)); i += 1; continue
        if not s and i + 1 < len(lines) and (LIST_RE.match(lines[i + 1]) or lines[i + 1].startswith("   ")):
            i += 1; continue
        break
    while stack:
        out.append("</li></%s>" % stack.pop()[1])
    return i

# ---------- code cells ----------
def code_cell(src):
    first, _, body = src.partition("\n")
    if first.startswith("%%writefile"):
        path = first.split(None, 1)[1].strip()
        path = re.sub(r"^-a\s+", "", path)
        d = os.path.dirname(path)
        cmd = (f"mkdir -p {d} && " if d else "") + f"cat > {path} <<'EOF'\n{body.rstrip()}\nEOF"
        return f'<div class="box file"><span class="lbl">📄 Create file: {html.escape(path)}</span><pre><code>{html.escape(cmd)}</code></pre></div>'
    if first.startswith("%%bash"):
        src = body
    src = src.strip("\n")
    if not src.strip():
        return ""
    return f'<div class="box term"><span class="lbl">▶ Terminal</span><pre><code>{html.escape(src)}</code></pre></div>'

def convert(nb_path, base=""):
    nb = json.load(open(nb_path))
    parts = []
    for c in nb["cells"]:
        s = "".join(c["source"])
        parts.append(md(fix_wording(s)) if c["cell_type"] == "markdown" else code_cell(s))
    title = os.path.splitext(os.path.basename(nb_path))[0].replace("-", " ")
    return (f"<!doctype html><html><head><meta charset='utf-8'><base href='{base}'><title>{html.escape(title)}</title>"
            f"<style>{CSS}</style></head><body>{''.join(parts)}</body></html>")

if __name__ == "__main__":
    args = sys.argv[1:]
    out_dir = args[args.index("--out") + 1]; args = [a for a in args if a not in ("--out", out_dir)]
    os.makedirs(out_dir, exist_ok=True)
    tmp = tempfile.mkdtemp()
    for nb in args:
        name = os.path.splitext(os.path.basename(nb))[0]
        hp = os.path.join(tmp, name + ".html")
        open(hp, "w").write(convert(nb, "file://" + os.path.abspath(out_dir) + "/"))
        pdf = os.path.abspath(os.path.join(out_dir, name + ".pdf"))
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--user-data-dir={tmp}/chrome", f"--print-to-pdf={pdf}", "file://" + hp],
                       check=True, capture_output=True, timeout=180)
        print(f"{name}.pdf  {os.path.getsize(pdf)//1024} KB")
