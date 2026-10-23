"""Turn scraped drafts into press specs: download each photo, shrink it into assets/press/<sn>/, write content/press/<sn>.json.

Usage: python -I import_press.py <drafts_dir> <raw_dir> <assets_dir> <content_dir> [max_edge] [quality]
Run from the project folder. Specs that already exist are left alone (hand-edited ones keep their alt text).
"""
import json
import pathlib
import re
import sys
import urllib.request

from PIL import Image, ImageOps

drafts, raw, assets, content = (pathlib.Path(p) for p in sys.argv[1:5])
max_edge = int(sys.argv[5]) if len(sys.argv) > 5 else 800
quality = int(sys.argv[6]) if len(sys.argv) > 6 else 68
UA = {"User-Agent": "Mozilla/5.0"}
SCHOOL_TAG = re.compile(r"^\s*[\[(]\s*춘양초(?:등학교)?\s*[\])]\s*")

for draft_path in sorted(drafts.glob("*.json")):
    d = json.loads(draft_path.read_text(encoding="utf-8"))
    spec_path = content / f"{d['sn']}.json"
    if spec_path.exists():
        print(d["sn"], "spec exists, skipped")
        continue
    title = SCHOOL_TAG.sub("", d["title"])
    raw_dir, out_dir = raw / d["sn"], assets / d["sn"]
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    images = []
    for i, url in enumerate(d["photos"], 1):
        src = raw_dir / f"photo{i}.jpg"
        if not src.exists():
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                src.write_bytes(r.read())
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((max_edge, max_edge), Image.LANCZOS)
            dst = out_dir / f"photo{i}.jpg"
            im.save(dst, "JPEG", quality=quality, optimize=True, progressive=True)
        images.append({"file": dst.as_posix(), "alt": f"{title} 활동 사진 {i}"})
    spec = {
        "id": d["id"], "cat": "press", "title": title, "author": "봉화교육지원청", "date": d["date"],
        "body": d["body"], "images": images,
        "source": {"name": "경상북도봉화교육지원청 학교교육홍보", "short": "봉화교육지원청", "url": d["url"]},
    }
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    kb = sum((out_dir / f"photo{i}.jpg").stat().st_size for i in range(1, len(images) + 1)) // 1024
    print(d["sn"], d["date"], f"{len(images)} photos -> {kb} KB")

