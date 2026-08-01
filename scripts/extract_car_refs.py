#!/usr/bin/env python3
"""從 Okiblues 實拍影片抽出每台車的參考幀，當成 OBcar 的 Vehicle Identity Pack 來源。

OBcar 的鐵則第 1 條是「車款靠上傳照片，不靠形容詞」，而每台車的實拍影片（100 秒左右、
1920×1080）本來就把前 3/4、正側、車尾、輪圈、頭燈全拍過一輪了。所以缺的不是拍攝，
是抽幀。

用法：
    python3 scripts/extract_car_refs.py              # 全車隊，每台一張聯絡表
    python3 scripts/extract_car_refs.py --car Voxy   # 只跑名字含 Voxy 的資料夾
    python3 scripts/extract_car_refs.py --every 4    # 每 4 秒抽一幀（預設 8）

產出（不進 git，媒體照 saidio 慣例留在本機）：
    <OUT>/<car>/f_01.jpg …      單幀，挑好的直接當參考照上傳
    <OUT>/<car>/contact.jpg     聯絡表，用來一眼挑出要哪幾張

挑幀原則：影片有燒死的字幕與 OKIBLUES 浮水印，優先挑沒有字幕那幾格；
車款身分只需要車體本身讀得出來，浮水印在角落不影響。
"""
import argparse
import subprocess
import sys
from pathlib import Path

FOOTAGE = Path(
    "/Users/sws/Library/CloudStorage/GoogleDrive-sssunjp@gmail.com/我的雲端硬碟"
    "/OkiMac/*Okiblues/final/小林影片"
)
OUT = Path.home() / "Sun/Claude/saidio/resource/obcar_refs"

# 這兩個資料夾是流程說明，不是車。
SKIP = {"出境指南", "取車還車"}


def landscape_video(folder):
    """優先用橫向影片：直式是同一批素材裁過的，車體邊緣容易被切掉。"""
    videos = sorted(p for p in folder.iterdir() if p.suffix.lower() in (".mp4", ".mov"))
    if not videos:
        return None
    return next((v for v in videos if "橫" in v.name), videos[0])


def extract(video, target, every):
    target.mkdir(parents=True, exist_ok=True)
    for old in target.glob("*.jpg"):
        old.unlink()
    subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video),
         "-vf", f"fps=1/{every},scale=960:-1", "-q:v", "3",
         str(target / "f_%02d.jpg")],
        check=True,
    )
    frames = sorted(target.glob("f_*.jpg"))
    if frames:
        columns = 4
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(target / "f_%02d.jpg"),
             "-vf", f"scale=480:-1,tile={columns}x{(len(frames) + columns - 1) // columns}",
             "-q:v", "3", str(target / "contact.jpg")],
            check=True,
        )
    return len(frames)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--car", default="", help="只跑名字含這個字串的資料夾")
    parser.add_argument("--every", type=int, default=8, help="每幾秒抽一幀")
    args = parser.parse_args()

    if not FOOTAGE.is_dir():
        sys.exit(f"找不到素材夾：{FOOTAGE}\n（Google Drive 沒掛載或路徑改了）")

    folders = [f for f in sorted(FOOTAGE.iterdir())
               if f.is_dir() and f.name not in SKIP and args.car.lower() in f.name.lower()]
    if not folders:
        sys.exit(f"沒有符合 --car {args.car!r} 的資料夾")

    for folder in folders:
        video = landscape_video(folder)
        if video is None:
            print(f"  跳過 {folder.name}：沒有影片")
            continue
        target = OUT / folder.name.strip()
        count = extract(video, target, args.every)
        print(f"  {folder.name.strip():<28} {count:>2} 幀  ← {video.name}")

    print(f"\n聯絡表看這裡：{OUT}")


if __name__ == "__main__":
    main()
