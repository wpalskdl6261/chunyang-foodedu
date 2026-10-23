"""춘양초 식생활교육 페이지를 만든다.

    python tools/build.py            -> index.html  (GitHub Pages용: 글꼴은 CDN, 사진은 assets/ 파일을 불러옴)
    python tools/build.py --single   -> dist/chunyang-food-edu.html  (한 파일: 글꼴·교표·사진을 모두 안에 넣은 Claude Artifact용)

원본은 src/index.src.html, 보도자료는 content/press/*.json, 갈래·짧은 이름은 content/press-themes.json.
"""
import argparse
import base64
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT_CDN = ('<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9'
            '/dist/web/static/pretendard-dynamic-subset.min.css">')
FONT_WEIGHTS = {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700}
SCHOOL_TAG = re.compile(r"^\s*[\[(]\s*춘양초(?:등학교)?\s*[\])]\s*")
DATA_BLOCK = re.compile(r'(<script type="application/json" id="press-data">)(.*?)(</script>)', re.S)
DESCRIPTION = "학교급식 선도학교를 운영하는 춘양초등학교의 식생활교육 이야기"


def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def embedded_fonts():
    faces = [
        '@font-face{font-family:"Pretendard";font-style:normal;font-weight:%d;font-display:swap;src:url(%s) format("woff2")}'
        % (weight, data_uri(ROOT / "tools" / "fonts" / f"Pretendard-{name}.subset.woff2", "font/woff2"))
        for name, weight in FONT_WEIGHTS.items()
    ]
    return ('<style id="pretendard-face">\n/* Pretendard 1.3.9 (KS X 1001 subset) by Kil Hyung-jin, SIL Open Font License 1.1 */\n'
            + "\n".join(faces) + "\n</style>")


def press_posts(single):
    themes = json.loads((ROOT / "content" / "press-themes.json").read_text(encoding="utf-8"))
    posts = []
    for spec_path in sorted((ROOT / "content" / "press").glob("*.json")):
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        images = [{"src": data_uri(ROOT / im["file"], "image/jpeg") if single else im["file"], "alt": im.get("alt", "")}
                  for im in spec.get("images", [])]
        post = {
            "id": spec["id"], "cat": "press",
            "title": SCHOOL_TAG.sub("", spec["title"]),
            "date": spec["date"],
            "body": spec.get("body", ""),
            "images": images,
            "source": spec.get("source", {}),
        }
        post.update(themes.get(spec["id"].removeprefix("press-"), {}))
        posts.append(post)
    return posts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--single", action="store_true", help="글꼴·사진을 모두 넣은 한 파일(dist/)로 만든다")
    single = ap.parse_args().single

    src = (ROOT / "src" / "index.src.html").read_text(encoding="utf-8")
    src = src.replace("<!--@font-->", embedded_fonts() if single else FONT_CDN, 1)
    src = src.replace("__EMBLEM__", data_uri(ROOT / "assets" / "emblem.png", "image/png") if single else "assets/emblem.png")
    posts = press_posts(single)
    payload = json.dumps(posts, ensure_ascii=False, indent=1).replace("<", "\\u003c")
    src = DATA_BLOCK.sub(lambda m: m.group(1) + payload + m.group(3), src, count=1)

    if single:
        out = ROOT / "dist" / "chunyang-food-edu.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(src, encoding="utf-8")
    else:
        # src는 <title>·<style> 다음에 본문이 이어지는 형태라, 본문 시작(<header) 앞까지를 <head>에 넣는다
        cut = src.index('<header class="topbar">')
        out = ROOT / "index.html"
        out.write_text(
            '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            f'<meta name="description" content="{DESCRIPTION}">\n'
            '<meta property="og:title" content="춘양초 식생활교육">\n'
            f'<meta property="og:description" content="{DESCRIPTION}">\n'
            '<link rel="icon" href="assets/emblem.png">\n'
            + src[:cut] + '</head>\n<body>\n' + src[cut:] + '\n</body>\n</html>\n',
            encoding="utf-8")
    print(f"{out.relative_to(ROOT)}: 보도자료 {len(posts)}건, 사진 {sum(len(p['images']) for p in posts)}장, "
          f"{out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
