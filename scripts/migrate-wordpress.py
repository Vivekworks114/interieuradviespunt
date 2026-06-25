#!/usr/bin/env python3
"""Migrate WordPress WXR export into Astro content collections for interieuradviespunt.nl."""

from __future__ import annotations

import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XML_PATH = Path(
    os.environ.get(
        "WXR_PATH",
        "/Users/gauravkashyap/Downloads/interieuradviespunt.WordPress.2026-06-25.xml",
    )
)
SITE_URL = "https://interieuradviespunt.nl"

NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "wp": "http://wordpress.org/export/1.2/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
}

BLOG_DIR = ROOT / "src/content/blog"
PAGES_DIR = ROOT / "src/content/pages"
AUTHORS_DIR = ROOT / "src/content/authors"
CATEGORIES_DIR = ROOT / "src/content/categories"
TAGS_DIR = ROOT / "src/content/tags"
PUBLIC_UPLOADS = ROOT / "public/images"
DATA_DIR = ROOT / "src/data"

SKIP_PAGE_SLUGS = {"home", "blog", "contact", "sample-page-2", "zb_mp_title", "products-review"}
DEFAULT_FEATURED = "/images/2023/05/wanddecoratie.jpg"


def text(el) -> str:
    return el.text.strip() if el is not None and el.text else ""


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def yaml_list(items: list[str]) -> str:
    if not items:
        return "[]"
    return "\n" + "\n".join(f"  - {yaml_quote(i)}" for i in items)


def upload_to_local(url_or_path: str) -> str:
    if not url_or_path:
        return DEFAULT_FEATURED
    if url_or_path.startswith("/images/"):
        return url_or_path
    if "/wp-content/uploads/" in url_or_path:
        rel = url_or_path.split("/wp-content/uploads/", 1)[1].split("?")[0]
        return f"/images/{rel}"
    return url_or_path


def rewrite_urls(content: str, url_map: dict[str, str]) -> str:
    if not content:
        return ""

    def replace_upload_url(match: re.Match) -> str:
        url = match.group(0).split("?")[0]
        local = url_map.get(url)
        if local:
            return local
        if "/wp-content/uploads/" in url:
            local_path = upload_to_local(url)
            url_map[url] = local_path
            return local_path
        return url

    content = re.sub(
        rf"https?://(?:www\.)?interieuradviespunt\.nl/wp-content/uploads/[^\s\"'<>?]+",
        replace_upload_url,
        content,
    )
    content = re.sub(
        rf"{re.escape(SITE_URL)}/(?P<slug>[a-z0-9\-_/]+)/?",
        r"/\g<slug>/",
        content,
    )
    content = re.sub(
        r'(?:src|href)="/wp-content/uploads/([^"\']+)"',
        r'\1="/images/\1"',
        content,
    )
    return content


def extract_first_image(content: str) -> str | None:
    match = re.search(r'(?:src|href)="(/images/[^"]+)"', content or "")
    if match:
        return match.group(1)
    match = re.search(r'(?:src|href)="(/wp-content/uploads/[^"]+)"', content or "")
    return upload_to_local(match.group(1)) if match else None


def strip_html(html: str) -> str:
    text_value = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", text_value).strip()[:300]


def download_image(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["curl", "-sfL", url, "-o", str(dest)],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and dest.exists() and dest.stat().st_size > 0


def strip_shortcodes(value: str) -> str:
    return re.sub(r"\[[^\]]*\]", "", value)


def clean_html(html: str) -> str:
    html = re.sub(r"<!--[\s\S]*?-->", "", html or "")
    html = strip_shortcodes(html)
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["script", "style", "iframe"]):
            tag.decompose()
        for p in soup.find_all("p"):
            if p.find(["h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "table", "div"]):
                p.unwrap()
        return str(soup)
    except ImportError:
        return html


def prepare_mdx_body(html: str) -> str:
    html = clean_html(html)
    try:
        from markdownify import markdownify as md

        text = md(html, heading_style="ATX", bullets="-", strip=["script", "style"])
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        return text.replace("{", "\\{").replace("}", "\\}")
    except ImportError:
        text = re.sub(r"\n{3,}", "\n\n", html).strip()
        return text.replace("{", "\\{").replace("}", "\\}")


def sanitize_frontmatter_text(value: str) -> str:
    value = strip_shortcodes(value or "")
    value = re.sub(r"\s+", " ", value).strip()
    return value[:500]


def parse_wxr() -> dict:
    authors: dict[str, dict] = {}
    categories: dict[str, dict] = {}
    tags: dict[str, dict] = {}
    attachments: dict[str, str] = {}
    items: list[dict] = []
    nav_items: list[dict] = []

    for event, elem in ET.iterparse(XML_PATH, events=("end",)):
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

        if tag == "author":
            login = text(elem.find("wp:author_login", NS))
            authors[login] = {
                "id": text(elem.find("wp:author_id", NS)),
                "login": login,
                "email": text(elem.find("wp:author_email", NS)),
                "displayName": text(elem.find("wp:author_display_name", NS)),
            }
            elem.clear()
            continue

        if tag == "category":
            slug = text(elem.find("wp:category_nicename", NS))
            categories[slug] = {
                "slug": slug,
                "name": text(elem.find("wp:cat_name", NS)),
                "parent": text(elem.find("wp:category_parent", NS)),
            }
            elem.clear()
            continue

        if tag != "item":
            continue

        post_type = text(elem.find("wp:post_type", NS))
        status = text(elem.find("wp:status", NS))
        post_id = text(elem.find("wp:post_id", NS))
        slug = text(elem.find("wp:post_name", NS))
        title = text(elem.find("title"))
        link = text(elem.find("link"))
        creator = text(elem.find("dc:creator", NS))
        content = text(elem.find("content:encoded", NS))
        excerpt = text(elem.find("excerpt:encoded", NS))
        pub_date = text(elem.find("wp:post_date", NS))
        modified = text(elem.find("wp:post_modified", NS))

        postmeta = {}
        for pm in elem.findall("wp:postmeta", NS):
            key = text(pm.find("wp:meta_key", NS))
            val = text(pm.find("wp:meta_value", NS))
            if key:
                postmeta[key] = val

        cats = []
        post_tags = []
        for cat in elem.findall("category"):
            domain = cat.get("domain", "")
            nicename = cat.get("nicename", "")
            label = cat.text or ""
            if domain == "category" and label:
                cats.append(label)
                if nicename and nicename not in categories:
                    categories[nicename] = {"slug": nicename, "name": label, "parent": ""}
            elif domain == "post_tag" and label:
                post_tags.append(label)
                if nicename and nicename not in tags:
                    tags[nicename] = {"slug": nicename, "name": label}

        attachment_url = text(elem.find("wp:attachment_url", NS))
        if post_type == "attachment" and attachment_url:
            attachments[post_id] = attachment_url

        if post_type == "nav_menu_item" and status == "publish":
            nav_items.append(
                {
                    "post_id": post_id,
                    "title": title,
                    "slug": slug,
                    "menu_order": int(text(elem.find("wp:menu_order", NS)) or 0),
                    "meta": postmeta,
                }
            )
        elif post_type in {"post", "page"} and status == "publish":
            items.append(
                {
                    "post_type": post_type,
                    "post_id": post_id,
                    "slug": slug,
                    "title": title,
                    "link": link,
                    "author": creator,
                    "content": content,
                    "excerpt": excerpt,
                    "pubDate": pub_date,
                    "updatedDate": modified,
                    "categories": cats,
                    "tags": post_tags,
                    "meta": postmeta,
                }
            )

        elem.clear()

    return {
        "authors": authors,
        "categories": categories,
        "tags": tags,
        "attachments": attachments,
        "items": items,
        "nav_items": nav_items,
    }


def resolve_thumbnail(item: dict, attachments: dict[str, str]) -> str | None:
    thumb_id = item["meta"].get("_thumbnail_id")
    if thumb_id and thumb_id in attachments:
        return upload_to_local(attachments[thumb_id])
    return None


def write_mdx(path: Path, frontmatter: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    for key, value in frontmatter.items():
        if value is None:
            continue
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:{yaml_list(value)}")
        elif isinstance(value, str):
            lines.append(f"{key}: {yaml_quote(value)}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")
    lines.append(body.strip())
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_blog_posts_json(posts: list[dict]) -> None:
    latest = sorted(posts, key=lambda p: p["pubDate"], reverse=True)
    out = []
    for item in latest:
        featured = item.get("featuredImage") or DEFAULT_FEATURED
        out.append(
            {
                "slug": item["slug"],
                "title": item["title"],
                "excerpt": item["description"],
                "featuredImage": featured,
                "date": item["pubDate"][:10],
            }
        )
    (DATA_DIR / "blog-posts.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_pages_json(pages: list[dict]) -> None:
    out = []
    for item in pages:
        out.append(
            {
                "slug": item["slug"],
                "title": item["title"],
                "excerpt": item["description"],
                "featuredImage": item.get("featuredImage") or DEFAULT_FEATURED,
            }
        )
    (DATA_DIR / "pages.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def migrate() -> None:
    print(f"Parsing {XML_PATH}...")
    data = parse_wxr()
    url_map: dict[str, str] = {}
    image_urls: set[str] = set()

    for url in data["attachments"].values():
        image_urls.add(url)

    posts_raw = [i for i in data["items"] if i["post_type"] == "post"]
    pages_raw = [
        i
        for i in data["items"]
        if i["post_type"] == "page"
        and i["slug"] not in SKIP_PAGE_SLUGS
        and not i["slug"].startswith("zb_mp_")
    ]

    print(f"Migrating {len(posts_raw)} posts, {len(pages_raw)} pages...")

    if BLOG_DIR.exists():
        for f in BLOG_DIR.glob("*.mdx"):
            f.unlink()
    if PAGES_DIR.exists():
        for f in PAGES_DIR.glob("*.mdx"):
            f.unlink()

    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    migrated_posts: list[dict] = []
    migrated_pages: list[dict] = []

    for item in posts_raw:
        body = rewrite_urls(item["content"], url_map)
        featured = resolve_thumbnail(item, data["attachments"]) or extract_first_image(body)
        if featured:
            full_url = featured if featured.startswith("http") else f"{SITE_URL}{featured.replace('/images/', '/wp-content/uploads/')}"
            if "/wp-content/uploads/" in full_url or featured.startswith("/images/"):
                if featured.startswith("/images/"):
                    image_urls.add(f"{SITE_URL}/wp-content/uploads/{featured.split('/images/', 1)[1]}")
                else:
                    image_urls.add(full_url)

        description = sanitize_frontmatter_text(
            strip_html(item["excerpt"]) or strip_html(body) or item["title"]
        )
        pub_iso = item["pubDate"].replace(" ", "T")
        updated_iso = item["updatedDate"].replace(" ", "T")
        featured_local = featured or DEFAULT_FEATURED

        frontmatter = {
            "title": sanitize_frontmatter_text(item["title"]),
            "description": description,
            "pubDate": pub_iso,
            "updatedDate": updated_iso,
            "author": item["author"],
            "categories": item["categories"] or ["Blog"],
            "tags": item["tags"],
            "featuredImage": featured_local,
            "imageAlt": sanitize_frontmatter_text(item["title"]),
        }

        write_mdx(BLOG_DIR / f"{item['slug']}.mdx", frontmatter, prepare_mdx_body(body))

        migrated_posts.append(
            {
                "slug": item["slug"],
                "title": frontmatter["title"],
                "description": description,
                "featuredImage": featured_local,
                "pubDate": item["pubDate"],
            }
        )

        for match in re.findall(r"/images/[^\s\"'<>?]+", body):
            image_urls.add(f"{SITE_URL}/wp-content/uploads/{match.split('/images/', 1)[1]}")

    for item in pages_raw:
        body = rewrite_urls(item["content"], url_map)
        featured = resolve_thumbnail(item, data["attachments"]) or extract_first_image(body)
        description = sanitize_frontmatter_text(
            strip_html(item["excerpt"]) or strip_html(body) or item["title"]
        )
        pub_iso = item["pubDate"].replace(" ", "T")
        updated_iso = item["updatedDate"].replace(" ", "T")
        featured_local = featured or DEFAULT_FEATURED
        is_product = item["slug"].startswith("beste-")

        frontmatter = {
            "title": sanitize_frontmatter_text(item["title"]),
            "description": description,
            "pubDate": pub_iso,
            "updatedDate": updated_iso,
            "featuredImage": featured_local,
        }
        if is_product:
            frontmatter["pageType"] = "product"

        write_mdx(PAGES_DIR / f"{item['slug']}.mdx", frontmatter, prepare_mdx_body(body))

        migrated_pages.append(
            {
                "slug": item["slug"],
                "title": frontmatter["title"],
                "description": description,
                "featuredImage": featured_local,
            }
        )

        for match in re.findall(r"/images/[^\s\"'<>?]+", body):
            image_urls.add(f"{SITE_URL}/wp-content/uploads/{match.split('/images/', 1)[1]}")

    AUTHORS_DIR.mkdir(parents=True, exist_ok=True)
    for login, author in data["authors"].items():
        safe = re.sub(r"[^\w\-]", "-", login)
        (AUTHORS_DIR / f"{safe}.json").write_text(
            json.dumps(author, indent=2), encoding="utf-8"
        )

    CATEGORIES_DIR.mkdir(parents=True, exist_ok=True)
    (CATEGORIES_DIR / "categories.json").write_text(
        json.dumps(list(data["categories"].values()), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    TAGS_DIR.mkdir(parents=True, exist_ok=True)
    (TAGS_DIR / "tags.json").write_text(
        json.dumps(list(data["tags"].values()), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    write_blog_posts_json(migrated_posts)
    write_pages_json(migrated_pages)

    print(f"Downloading {len(image_urls)} images...")
    download_jobs = []
    for url in sorted(image_urls):
        if "/wp-content/uploads/" not in url:
            continue
        rel = url.split("/wp-content/uploads/", 1)[1].split("?")[0]
        dest = PUBLIC_UPLOADS / rel
        download_jobs.append((url.split("?")[0], dest))

    success = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {
            pool.submit(download_image, url, dest): (url, dest)
            for url, dest in download_jobs
        }
        for future in as_completed(futures):
            if future.result():
                success += 1

    print(f"Downloaded {success}/{len(download_jobs)} images")

    summary = {
        "posts": len(posts_raw),
        "pages": len(pages_raw),
        "authors": len(data["authors"]),
        "categories": len(data["categories"]),
        "tags": len(data["tags"]),
        "images": success,
    }
    (ROOT / "migration-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    migrate()
