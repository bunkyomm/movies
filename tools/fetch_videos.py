#!/usr/bin/env python3
"""YouTubeチャンネル(@yourplacestory)の動画一覧を取得し、videos.jsonを生成する。

YouTube Data API(要APIキー)を使わず、公開ページのHTMLから情報を抽出する簡易スクリプト。
YouTube側のページ構造が変わると動かなくなる可能性があるため、新しい動画を追加した際に
動かない場合はこのスクリプトを見直すこと。

使い方:
    python3 tools/fetch_videos.py
"""

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "videos.json"
CHANNEL_HANDLE = "yourplacestory"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as res:
        return res.read().decode("utf-8", errors="replace")


def get_video_ids():
    html = fetch(f"https://www.youtube.com/@{CHANNEL_HANDLE}/videos")
    ids = list(dict.fromkeys(re.findall(r'"videoId":"([^"]+)"', html)))
    return ids


def extract_year(title):
    years = re.findall(r"20[12]\d", title)
    return int(years[0]) if years else None


def get_video_info(video_id):
    html = fetch(f"https://www.youtube.com/watch?v={video_id}")
    title_match = re.search(r'<meta name="title" content="([^"]*)">', html)
    title = title_match.group(1) if title_match else video_id
    date_match = re.search(r'"publishDate":"([^"]*)"', html)
    publish_date = date_match.group(1) if date_match else None
    return {
        "id": video_id,
        "title": title,
        "year": extract_year(title),
        "publishDate": publish_date,
        "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }


def main():
    try:
        video_ids = get_video_ids()
    except Exception as e:
        print(f"エラー: 動画一覧の取得に失敗しました: {e}", file=sys.stderr)
        sys.exit(1)

    if not video_ids:
        print("警告: 動画が1件も見つかりませんでした。", file=sys.stderr)

    videos = []
    for vid in video_ids:
        try:
            info = get_video_info(vid)
        except Exception as e:
            print(f"警告: {vid} の情報取得に失敗しました: {e}", file=sys.stderr)
            continue
        if info["year"] is None:
            print(f"警告: {vid} のタイトルから年度を抽出できませんでした: {info['title']!r}", file=sys.stderr)
        videos.append(info)
        time.sleep(0.3)

    # 年度の新しい順。同年度はタイトルの昇順で安定ソート。
    videos.sort(key=lambda v: (-(v["year"] or 0), v["title"]))

    OUTPUT_PATH.write_text(
        json.dumps(videos, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{len(videos)}件の動画情報を {OUTPUT_PATH.relative_to(ROOT)} に出力しました。")


if __name__ == "__main__":
    main()
