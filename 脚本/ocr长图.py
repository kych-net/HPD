#!/usr/bin/env python3
"""长图 OCR:高重叠率切分 → mac-ocr 逐块识别 → 丢弃切分边界附近的文本 → 按全局坐标拼接。

为什么这么切:Apple Vision 对超高图会内部降采样,整张丢进去会把小字识别成乱码;
切成 ~3000px 的块能保住原分辨率。高重叠(默认 50%)保证每行文字至少在一块里完整出现;
切分边界附近的文本可能被裁断,一律丢弃,由相邻块里的完整副本补回;最后按全局纵坐标
去重、按行距(截图里的空行)切分段落。

用法:
    python3 脚本/ocr长图.py 长图.jpg
    python3 脚本/ocr长图.py 图片/*.jpg -o 内容/新章.txt
    python3 脚本/ocr长图.py 长图.jpg --drop-pattern '默认笔记本'
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

MAC_OCR = shutil.which("mac-ocr") or "/opt/homebrew/bin/mac-ocr"

# 阅读器截图顶端的外框文字(状态栏时间、标题栏日期/字数/笔记名),默认丢弃。
DEFAULT_DROP = (
    r"^\s*\d{1,2}:\d{2}\b",
    r"^\s*\d{4}[/-]\d{1,2}[/-]\d{1,2}",
    r"\d+\s*字\s*[|｜]",
    r"默认笔记本",
)


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}\n{proc.stderr.strip()}")
    return proc.stdout


def make_slices(src: Path, out_dir: Path, slice_h: int, step: int):
    """按固定步长切图,返回 [(顶端绝对坐标, 本片高度, 切片路径), …]。"""
    with Image.open(src) as im:
        w, h = im.size
        slice_h = min(slice_h, h)
        top, idx = 0, 0
        while True:
            cur_h = min(slice_h, h - top)
            out = out_dir / f"{src.stem}__{idx:03d}.png"
            im.crop((0, top, w, top + cur_h)).save(out)
            yield top, cur_h, out
            if top + cur_h >= h:
                break
            top += step
            idx += 1


def ocr(path: Path, lang: str) -> list[dict]:
    out = run([MAC_OCR, str(path), "-l", lang, "--format", "json"])
    data = json.loads(out)
    if isinstance(data, dict):
        data = [data]
    return data[0].get("observations", []) if data else []


def collect_lines(src: Path, workdir: Path, args, drop_res: list[re.Pattern]) -> list[dict]:
    with Image.open(src) as im:
        w_img, h = im.size
    slice_h = min(args.slice_height, h)
    step = max(1, round(slice_h * (1 - args.overlap)))
    margin = round(slice_h * args.margin)
    status_margin = round(slice_h * args.status_margin)

    lines: list[dict] = []
    for top, cur_h, path in make_slices(src, workdir, slice_h, step):
        # 只丢"内部"边界附近的文本;图片真正的上下边缘不算切分处。
        drop_top = margin if top > 0 else status_margin
        drop_bottom = margin if (top + cur_h) < h else 0
        for ob in ocr(path, args.lang):
            bb = ob["boundingBox"]
            local_y = bb["y"] * cur_h
            if local_y < drop_top or local_y > cur_h - drop_bottom:
                continue
            text = ob["text"].strip()
            if not text:
                continue
            if top == 0 and any(p.search(text) for p in drop_res):
                continue
            lines.append(
                {
                    "y": top + local_y,
                    "x": bb["x"] * w_img,
                    "w": bb["width"] * w_img,
                    "h": bb["height"] * cur_h,
                    "text": text,
                    "conf": ob.get("confidence", 1.0),
                }
            )
        print(f"  {src.name} 切片 {path.name} → 累计 {len(lines)} 行", file=sys.stderr)
    return lines


def stitch(lines: list[dict]) -> list[dict]:
    """把各块结果拼成按纵坐标排好的行序列。

    同一物理行会在多块里出现:位置几乎重合、横向区间重叠,取最长(未被裁断)的一份;
    若同一行被 OCR 拆成横向不重叠的两段,则按 x 顺序接回去。
    """
    if not lines:
        return []
    lines.sort(key=lambda l: (l["y"], l["x"]))
    heights = sorted(l["h"] for l in lines)
    tol = max(8.0, heights[len(heights) // 2] * 0.5)

    rows: list[dict] = []
    for ln in lines:
        if rows and abs(ln["y"] - rows[-1]["y"]) <= tol:
            row = rows[-1]
            if ln["x"] > row["x"] + row["w"] - tol:
                row["text"] += ln["text"]
                row["w"] = ln["x"] + ln["w"] - row["x"]
            elif (len(ln["text"]), ln["conf"]) > (len(row["text"]), row["conf"]):
                ln["w"] = max(row["w"], ln["w"])
                rows[-1] = ln
        else:
            rows.append(ln)
    return rows


def split_paragraphs(rows: list[dict], ratio: float, short_line: bool = False) -> list[str]:
    """按行距切分段落。

    源文多是硬换行的(行尾常是断词处),所以默认只把"行距明显偏大"当换段信号,
    即截图里的空行。个别排版用短行收尾分段的,可开 --break-on-short-line 补充判断。
    """
    if not rows:
        return []

    gaps = sorted(rows[i]["y"] - rows[i - 1]["y"] for i in range(1, len(rows)))
    normal = gaps[len(gaps) // 2] if gaps else 0
    gap_threshold = normal * ratio

    short_right = -1.0
    if short_line:
        right = [r["x"] + r["w"] for r in rows]
        col_right = sorted(right)[int(len(right) * 0.95)]
        char_w = sorted(r["w"] / max(len(r["text"]), 1) for r in rows)[len(rows) // 2]
        short_right = col_right - 2.5 * char_w

    paras = [rows[0]["text"]]
    for prev, cur in zip(rows, rows[1:]):
        if cur["y"] - prev["y"] > gap_threshold or prev["x"] + prev["w"] < short_right:
            paras.append(cur["text"])
        else:
            paras[-1] += cur["text"]
    return paras


def expand(patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for pat in patterns:
        hits = sorted(glob.glob(pat)) if any(c in pat for c in "*?[") else [pat]
        if not hits:
            raise SystemExit(f"找不到文件:{pat}")
        files.extend(Path(h) for h in hits)
    return files


def main() -> None:
    ap = argparse.ArgumentParser(description="高重叠切分长图并 OCR 后拼接")
    ap.add_argument("images", nargs="+", help="长图路径,支持通配符")
    ap.add_argument("-o", "--output", help="输出文本文件;缺省写 stdout")
    ap.add_argument("--slice-height", type=int, default=3000, help="单块高度(像素,默认 3000)")
    ap.add_argument("--overlap", type=float, default=0.5, help="相邻块重叠比例(默认 0.5)")
    ap.add_argument("--margin", type=float, default=0.06, help="丢弃切分处附近文本的边距,占块高比例")
    ap.add_argument("--status-margin", type=float, default=0.05, help="图片顶端外框高度,占块高比例")
    ap.add_argument("--paragraph-ratio", type=float, default=1.7, help="行距超过常规行距多少倍算换段")
    ap.add_argument("--break-on-short-line", action="store_true", help="短行也当作换段(默认只认空行)")
    ap.add_argument("--join", choices=["paragraphs", "lines"], default="paragraphs")
    ap.add_argument("--lang", default="zh-Hans", help="识别语言,BCP-47")
    ap.add_argument("--separator", default="\n\n", help="多张图之间的分隔符")
    ap.add_argument("--drop-pattern", action="append", help="额外丢弃的外框行正则,可重复")
    ap.add_argument("--no-default-drop", action="store_true", help="不用内置的阅读器外框过滤")
    args = ap.parse_args()

    if not Path(MAC_OCR).exists():
        raise SystemExit("找不到 mac-ocr,请先安装")

    patterns = [] if args.no_default_drop else list(DEFAULT_DROP)
    patterns += args.drop_pattern or []
    drop_res = [re.compile(p) for p in patterns]

    blocks: list[str] = []
    with tempfile.TemporaryDirectory(prefix="ocr-long-") as tmp:
        workdir = Path(tmp)
        for src in expand(args.images):
            print(f"处理 {src}", file=sys.stderr)
            rows = stitch(collect_lines(src, workdir, args, drop_res))
            if args.join == "lines":
                blocks.append("\n".join(r["text"] for r in rows))
            else:
                blocks.append(
                    "\n\n".join(split_paragraphs(rows, args.paragraph_ratio, args.break_on_short_line))
                )

    text = args.separator.join(blocks).strip() + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"已写入 {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
