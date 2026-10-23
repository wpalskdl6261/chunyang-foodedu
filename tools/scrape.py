"""Read gbe.kr board posts (text only) and write one draft spec per post.

Usage: python -I scrape.py <pages_dir> <drafts_dir> <nttSn> [<nttSn> ...]
Each page's HTML is cached in pages_dir; drafts get title/author/date/body, photo URLs and their sizes (HEAD only).
"""
import html
import json
import pathlib
import re
import sys
import urllib.request

BASE = "https://www.gbe.kr"
VIEW = BASE + "/bh/na/ntt/selectNttInfo.do?mi=19559&bbsId=1806&nttSn={}"
UA = {"User-Agent": "Mozilla/5.0"}

pages, drafts = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
pages.mkdir(parents=True, exist_ok=True)
drafts.mkdir(parents=True, exist_ok=True)


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def head_size(url):
    req = urllib.request.Request(url, headers=UA, method="HEAD")
    with urllib.request.urlopen(req, timeout=30) as r:
        return int(r.headers.get("Content-Length") or 0)


def strip(fragment):
    fragment = re.sub(r"<!--.*?-->", "", fragment, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).replace("\xa0", " ").strip()


def body_text(fragment):
    fragment = re.sub(r"<!--.*?-->", "", fragment, flags=re.S)
    fragment = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.I)
    paras = re.split(r"</?(?:p|div|td|tr|table|tbody)\b[^>]*>", fragment, flags=re.I)
    out = []
    for p in paras:
        lines = [re.sub(r"[ \t]+", " ", l).strip() for l in strip(p).split("\n")]
        text = "\n".join(l for l in lines if l)
        if text:
            out.append(text)
    return "\n\n".join(out)


for sn in sys.argv[3:]:
    cache = pages / f"{sn}.html"
    src = cache.read_text(encoding="utf-8") if cache.exists() else fetch(VIEW.format(sn))
    cache.write_text(src, encoding="utf-8")
    title = strip(re.search(r'<th scope="col" colspan="4" class="title">(.*?)</th>', src, re.S).group(1))
    author = strip(re.search(r'<th scope="row">작성자</th>\s*<td>(.*?)</td>', src, re.S).group(1))
    date = strip(re.search(r'<th scope="row">등록일</th>\s*<td>(.*?)</td>', src, re.S).group(1)).replace(".", "-")
    # 본문 칸: 사진 칸(class="ac nttView") 다음의 <td colspan="4">. 안에 표가 들어 있을 수 있어서
    # <td>/</td> 짝을 세어 이 칸이 닫히는 곳까지를 본문으로 본다
    start = src.index('<td colspan="4">', src.index('<th scope="row">등록일</th>')) + len('<td colspan="4">')
    depth, end = 1, len(src)
    for m in re.compile(r"<(/?)td\b", re.I).finditer(src, start):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            end = m.start()
            break
    body = body_text(src[start:end])
    photos = [BASE + p for p in re.findall(r"photoView\(\d+,\d+,'([^']+)'\)", src)]
    sizes = [head_size(u) for u in photos]
    draft = {"id": f"press-{sn}", "sn": sn, "title": title, "author": author, "date": date,
             "body": body, "photos": photos, "photo_bytes": sizes, "url": VIEW.format(sn)}
    (drafts / f"{sn}.json").write_text(json.dumps(draft, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{sn}\t{date}\t{len(photos)} photos\t{sum(sizes) // 1024} KB\t{len(body)} chars\t{title}")
