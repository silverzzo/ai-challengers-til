"""
Notion TIL -> GitHub Markdown 동기화 스크립트

동작:
1. 어제(KST 기준) 작성된 Notion 데이터베이스 항목을 가져온다.
2. 각 페이지의 블록을 Markdown으로 변환한다.
3. TIL/{연도}/{월}/ 아래에 저장한다. (이미지도 함께 다운로드)
4. 저장소 전체를 스캔해 README.md를 다시 생성한다.
   - 이번 달 글: 펼쳐서 표시
   - 지난 달 글: <details> 로 접어서 표시
"""

import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
NOTION_VERSION = "2022-06-28"

# 노션 데이터베이스 속성 이름 (본인 DB 속성명과 다르면 GitHub 저장소 Variables 에서 지정)
DATE_PROPERTY = os.environ.get("NOTION_DATE_PROPERTY") or "Date"
TAGS_PROPERTY = os.environ.get("NOTION_TAGS_PROPERTY") or "Tags"  # multi_select 타입
SUBJECT_PROPERTY = os.environ.get("NOTION_SUBJECT_PROPERTY") or "과목"  # select(단일 선택) 타입

REPO_ROOT = Path(__file__).resolve().parent.parent
TIL_DIR = REPO_ROOT / "TIL"

KST = timezone(timedelta(hours=9))

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}


# ---------------------------------------------------------------------------
# Notion API
# ---------------------------------------------------------------------------

def get_target_date():
    """이 스크립트는 KST 00:05 에 실행되므로, '어제'는 방금 끝난 하루를 의미한다."""
    now_kst = datetime.now(KST)
    return (now_kst - timedelta(days=1)).date()


def query_database(target_date):
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    payload = {
        "filter": {
            "property": DATE_PROPERTY,
            "date": {"equals": target_date.isoformat()},
        }
    }
    pages = []
    while True:
        res = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        res.raise_for_status()
        data = res.json()
        pages.extend(data["results"])
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]
    return pages


def get_block_children(block_id):
    children = []
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    params = {"page_size": 100}
    while True:
        res = requests.get(url, headers=HEADERS, params=params, timeout=30)
        res.raise_for_status()
        data = res.json()
        children.extend(data["results"])
        if not data.get("has_more"):
            break
        params["start_cursor"] = data["next_cursor"]
    return children


# ---------------------------------------------------------------------------
# Notion 블록 -> Markdown 변환
# ---------------------------------------------------------------------------

def rich_text_to_md(rich_text_list):
    parts = []
    for rt in rich_text_list:
        text = rt.get("plain_text", "")
        if not text:
            continue
        ann = rt.get("annotations", {})
        href = rt.get("href")
        if ann.get("code"):
            text = f"`{text}`"
        else:
            if ann.get("bold"):
                text = f"**{text}**"
            if ann.get("italic"):
                text = f"*{text}*"
            if ann.get("strikethrough"):
                text = f"~~{text}~~"
        if href:
            text = f"[{text}]({href})"
        parts.append(text)
    return "".join(parts)


def slugify(text):
    text = text.strip()
    # 한글, 영문, 숫자, 공백, 하이픈만 허용
    text = re.sub(r"[^\w\s가-힣-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = text.strip("-")
    return text[:50] if text else "til"


def download_image(url, save_path):
    res = requests.get(url, timeout=30)
    res.raise_for_status()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_bytes(res.content)


def blocks_to_markdown(blocks, asset_dir, asset_rel_prefix, image_counter):
    lines = []
    numbered_index = 0

    for block in blocks:
        btype = block["type"]
        content = block.get(btype, {})

        if btype != "numbered_list_item":
            numbered_index = 0

        if btype == "paragraph":
            lines.append(rich_text_to_md(content.get("rich_text", [])))
            lines.append("")

        elif btype in ("heading_1", "heading_2", "heading_3"):
            level = {"heading_1": "#", "heading_2": "##", "heading_3": "###"}[btype]
            lines.append(f"{level} {rich_text_to_md(content.get('rich_text', []))}")
            lines.append("")

        elif btype == "bulleted_list_item":
            lines.append(f"- {rich_text_to_md(content.get('rich_text', []))}")

        elif btype == "numbered_list_item":
            numbered_index += 1
            lines.append(f"{numbered_index}. {rich_text_to_md(content.get('rich_text', []))}")

        elif btype == "to_do":
            box = "[x]" if content.get("checked") else "[ ]"
            lines.append(f"- {box} {rich_text_to_md(content.get('rich_text', []))}")

        elif btype == "quote":
            lines.append(f"> {rich_text_to_md(content.get('rich_text', []))}")
            lines.append("")

        elif btype == "callout":
            emoji = content.get("icon", {}).get("emoji", "💡")
            lines.append(f"> {emoji} {rich_text_to_md(content.get('rich_text', []))}")
            lines.append("")

        elif btype == "code":
            lang = content.get("language", "") or ""
            lines.append(f"```{lang}")
            lines.append(rich_text_to_md(content.get("rich_text", [])))
            lines.append("```")
            lines.append("")

        elif btype == "divider":
            lines.append("---")
            lines.append("")

        elif btype == "image":
            image_counter[0] += 1
            src = content.get("external") or content.get("file") or {}
            url = src.get("url", "")
            ext = url.split("?")[0].split(".")[-1]
            if len(ext) > 4 or "/" in ext:
                ext = "png"
            filename = f"image-{image_counter[0]}.{ext}"
            try:
                download_image(url, asset_dir / filename)
                lines.append(f"![]({asset_rel_prefix}/{filename})")
            except Exception as exc:  # noqa: BLE001
                print(f"  이미지 다운로드 실패: {exc}")
            lines.append("")

        elif btype == "toggle":
            summary = rich_text_to_md(content.get("rich_text", []))
            lines.append(f"<details><summary>{summary}</summary>")
            lines.append("")
            if block.get("has_children"):
                sub_blocks = get_block_children(block["id"])
                lines.extend(
                    blocks_to_markdown(sub_blocks, asset_dir, asset_rel_prefix, image_counter)
                )
            lines.append("</details>")
            lines.append("")

        elif btype in ("bookmark", "embed"):
            url = content.get("url", "")
            if url:
                lines.append(f"<{url}>")
                lines.append("")

        else:
            # table, column_list 등 아직 지원하지 않는 블록은 건너뜀
            continue

        if block.get("has_children") and btype != "toggle":
            sub_blocks = get_block_children(block["id"])
            lines.extend(
                blocks_to_markdown(sub_blocks, asset_dir, asset_rel_prefix, image_counter)
            )

    return lines


# ---------------------------------------------------------------------------
# 페이지 속성 추출
# ---------------------------------------------------------------------------

def get_title(page):
    for prop in page["properties"].values():
        if prop["type"] == "title":
            rich = prop["title"]
            return rich_text_to_md(rich) if rich else "제목 없음"
    return "제목 없음"


def get_tags(page):
    prop = page["properties"].get(TAGS_PROPERTY)
    if not prop or prop.get("type") != "multi_select":
        return []
    return [t["name"] for t in prop["multi_select"]]


def get_subject(page):
    """단일 select 타입인 '과목' 속성을 읽는다."""
    prop = page["properties"].get(SUBJECT_PROPERTY)
    if not prop or prop.get("type") != "select":
        return None
    select = prop.get("select")
    return select["name"] if select else None


# ---------------------------------------------------------------------------
# 페이지 저장
# ---------------------------------------------------------------------------

def process_page(page, target_date):
    title = get_title(page)
    tags = get_tags(page)
    subject = get_subject(page)
    slug = slugify(title)
    date_str = target_date.isoformat()

    day_dir = TIL_DIR / f"{target_date.year:04d}" / f"{target_date.month:02d}"
    day_dir.mkdir(parents=True, exist_ok=True)

    filepath = day_dir / f"{date_str}-{slug}.md"
    asset_dir = day_dir / "assets" / f"{date_str}-{slug}"
    asset_rel_prefix = f"assets/{date_str}-{slug}"

    blocks = get_block_children(page["id"])
    image_counter = [0]
    body_lines = blocks_to_markdown(blocks, asset_dir, asset_rel_prefix, image_counter)

    frontmatter = ["---", f'title: "{title}"', f"date: {date_str}"]
    if subject:
        frontmatter.append(f'subject: "{subject}"')
    if tags:
        frontmatter.append("tags: [" + ", ".join(f'"{t}"' for t in tags) + "]")
    frontmatter.append("---")
    frontmatter.append("")

    content = "\n".join(frontmatter + [f"# {title}", ""] + body_lines)
    filepath.write_text(content, encoding="utf-8")
    print(f"  저장 완료: {filepath.relative_to(REPO_ROOT)}")


# ---------------------------------------------------------------------------
# README 재생성
# ---------------------------------------------------------------------------

def parse_frontmatter(filepath):
    text = filepath.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    meta = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip().strip('"')
    return meta


def collect_entries():
    entries = []
    if not TIL_DIR.exists():
        return entries
    for md_file in TIL_DIR.rglob("*.md"):
        if "assets" in md_file.parts:
            continue
        meta = parse_frontmatter(md_file)
        date_str = meta.get("date")
        if not date_str:
            continue
        entries.append(
            {
                "date": date_str,
                "title": meta.get("title", md_file.stem),
                "subject": meta.get("subject"),
                "path": md_file.relative_to(REPO_ROOT).as_posix(),
            }
        )
    entries.sort(key=lambda e: e["date"])  # 오름차순: 14일 -> 15일 -> 16일 순
    return entries


def generate_readme():
    entries = collect_entries()
    now_kst = datetime.now(KST)
    current_ym = f"{now_kst.year:04d}-{now_kst.month:02d}"

    by_month = {}
    for e in entries:
        by_month.setdefault(e["date"][:7], []).append(e)

    lines = [
        "# TIL (Today I Learned)",
        "",
        "> Notion에 작성한 TIL이 매일 자동으로 정리됩니다.",
        "",
    ]

    for ym in sorted(by_month.keys(), reverse=True):
        year, month = ym.split("-")
        month_entries = by_month[ym]
        heading = f"{year}년 {int(month)}월 ({len(month_entries)})"
        item_lines = []
        for e in month_entries:
            subject_tag = f"**[{e['subject']}]** " if e.get("subject") else ""
            item_lines.append(f"- `{e['date']}` {subject_tag}[{e['title']}]({e['path']})")

        if ym == current_ym:
            lines.append(f"## {heading}")
            lines.append("")
            lines.extend(item_lines)
            lines.append("")
        else:
            lines.append("<details>")
            lines.append(f"<summary>{heading}</summary>")
            lines.append("")
            lines.extend(item_lines)
            lines.append("")
            lines.append("</details>")
            lines.append("")

    (REPO_ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print("README.md 갱신 완료")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    target_date = get_target_date()
    print(f"대상 날짜(KST): {target_date.isoformat()}")

    pages = query_database(target_date)
    print(f"가져온 글 개수: {len(pages)}")

    if not pages:
        print("해당 날짜에 작성된 글이 없습니다. README만 갱신합니다.")

    for page in pages:
        process_page(page, target_date)

    generate_readme()


if __name__ == "__main__":
    main()
