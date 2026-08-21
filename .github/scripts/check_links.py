#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检测 1.md 表格中资源链接是否可访问，并更新状态列与检测时间列。"""

import os
import re
import datetime
import urllib.request
import urllib.error

MD_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "1.md")
MD_PATH = os.path.abspath(MD_PATH)


def extract_url(cell: str) -> str | None:
    """从表格单元格中提取第一个 Markdown 链接地址。"""
    m = re.search(r"\[[^\]]*\]\((https?://[^)]+)\)", cell)
    return m.group(1) if m else None


def is_accessible(url: str) -> bool:
    """尝试访问 URL，判断是否可以访问。"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=headers, method="HEAD")
            with urllib.request.urlopen(req, timeout=15) as resp:
                if 200 <= resp.status < 400:
                    return True
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
            pass
        # HEAD 失败时退化为 GET
        try:
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=15) as resp:
                if 200 <= resp.status < 400:
                    return True
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
            pass
    return False


def main() -> None:
    today = datetime.datetime.now().strftime("%Y%m%d")

    with open(MD_PATH, encoding="utf-8") as f:
        lines = f.readlines()

    changed = False
    # 跳过表头（前两行）与分隔行
    for idx in range(2, len(lines)):
        line = lines[idx]
        if not line.strip().startswith("|"):
            continue

        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue

        url = extract_url(cells[0])
        if not url:
            continue

        reachable = is_accessible(url)
        status = "🟢 可访问" if reachable else "🔴 不可访问"

        if cells[3] != status or cells[4] != today:
            cells[3] = status
            cells[4] = today
            lines[idx] = "| " + " | ".join(cells) + " |\n"
            changed = True
            print(f"{'可访问' if reachable else '不可访问'}: {url}")
        else:
            print(f"无变化: {url}")

    if changed:
        with open(MD_PATH, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print("已更新 1.md")
    else:
        print("无需更新")


if __name__ == "__main__":
    main()
