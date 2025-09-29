import re
import os

def set_tuning_values_newfile(
    tex_path: str,
    base_font_pt=None,
    baseline_pt=None,
    default_fig_width=None,
    caption_size=None,
) -> str:
    with open(tex_path, "r", encoding="utf-8", errors="ignore") as f:
        tex = f.read()

    if "BEGIN AUTO FONT/FIG TUNING" not in tex:
        raise RuntimeError("Tuning block not found — run ensure_tuning_block first.")

    block_pattern = re.compile(
        r"(% === BEGIN AUTO FONT/FIG TUNING.*?% === END AUTO FONT/FIG TUNING[^\n]*\n?)",
        flags=re.DOTALL,
    )
    block_match = block_pattern.search(tex)
    if not block_match:
        raise RuntimeError("Could not locate tuning block boundaries.")

    block = block_match.group(1)

    def sub_one(pattern, repl, s):
        return re.sub(pattern, lambda m: m.group(1) + repl + m.group(2), s, count=1, flags=re.MULTILINE)

    if base_font_pt is not None:
        block = sub_one(r"(\\newcommand\{\\BaseFontSizePt\}\{)[^}]+(\})", str(base_font_pt), block)
    if baseline_pt is not None:
        block = sub_one(r"(\\newcommand\{\\BaseBaselineSkipPt\}\{)[^}]+(\})", str(baseline_pt), block)
    if default_fig_width is not None:
        block = sub_one(r"(\\newcommand\{\\DefaultFigureWidth\}\{)[^}]+(\})", default_fig_width, block)
    if caption_size is not None:
        block = sub_one(r"(\\newcommand\{\\CaptionSize\}\{)[^}]+(\})", caption_size, block)

    new_tex = tex[: block_match.start()] + block + tex[block_match.end():]

    root, ext = os.path.splitext(tex_path)

    # ✅ If filename already ends with _easy, overwrite it
    if root.endswith("_easy"):
        new_path = tex_path
    else:
        new_path = root + "_easy" + ext

    with open(new_path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(new_tex)

    print(f"🆕 Updated TeX file: {new_path}")
    return new_path


