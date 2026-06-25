#!/usr/bin/env python3
"""Fetch WordPress content and images from interieuradviespunt.nl REST API."""

from __future__ import annotations

import json
import re
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://interieuradviespunt.nl"
DATA_DIR = ROOT / "src/data"
PUBLIC_DIR = ROOT / "public/images"
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

MEDIA_CACHE: dict[int, str] = {}


def api_get(path: str) -> list | dict:
    url = f"{SITE}/wp-json/wp/v2/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "AstroMigration/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def fetch_paginated(resource: str, per_page: int = 100) -> list:
    items: list = []
    page = 1
    while True:
        try:
            batch = api_get(f"{resource}?per_page={per_page}&page={page}")
        except Exception:
            break
        if not batch:
            break
        items.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
    return items


def strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", unescape(text)).strip()


def download_file(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["curl", "-sfL", url, "-o", str(dest)],
        capture_output=True,
    )
    return result.returncode == 0 and dest.exists() and dest.stat().st_size > 0


def local_image_path(url: str) -> str | None:
    if not url or "/wp-content/uploads/" not in url:
        return None
    rel = url.split("/wp-content/uploads/", 1)[1].split("?")[0]
    dest = PUBLIC_DIR / rel
    if download_file(url, dest):
        return f"/images/{rel}"
    return None


def get_media_url(media_id: int) -> str | None:
    if not media_id:
        return None
    if media_id in MEDIA_CACHE:
        return MEDIA_CACHE[media_id]
    try:
        media = api_get(f"media/{media_id}")
        url = media.get("source_url", "")
        local = local_image_path(url)
        if local:
            MEDIA_CACHE[media_id] = local
            return local
    except Exception:
        pass
    return None


FALLBACK_IMAGES = [
    "/images/2023/05/bloemen.jpg",
    "/images/2023/05/kussen-1024x1016.jpg",
    "/images/2023/05/meubels.jpg",
    "/images/2023/05/klokken.jpg",
    "/images/2023/05/spiegel.jpg",
    "/images/2023/05/verlichting.jpg",
    "/images/2023/05/wanddecoratie.jpg",
    "/images/2023/05/geur.jpg",
]


def fallback_image(index: int) -> str:
    return FALLBACK_IMAGES[index % len(FALLBACK_IMAGES)]


def extract_content_images(html: str) -> list[str]:
    urls = re.findall(
        rf"{re.escape(SITE)}/wp-content/uploads/[^\s\"'<>]+",
        html or "",
    )
    local = []
    for url in urls:
        path = local_image_path(url.split("?")[0])
        if path:
            local.append(path)
    return local


def process_posts(posts: list) -> list[dict]:
    result = []
    for i, post in enumerate(posts):
        featured = get_media_url(post.get("featured_media", 0))
        if not featured:
            content_imgs = extract_content_images(post.get("content", {}).get("rendered", ""))
            featured = content_imgs[0] if content_imgs else fallback_image(i)
        result.append(
            {
                "slug": post["slug"],
                "title": strip_html(post["title"]["rendered"]),
                "date": post["date"][:10],
                "excerpt": strip_html(post["excerpt"]["rendered"]),
                "content": post["content"]["rendered"],
                "featuredImage": featured,
            }
        )
    return result


def process_pages(pages: list) -> list[dict]:
    skip = {"home", "blog", "contact", "sample-page-2", "zb_mp_title", "products-review"}
    result = []
    for i, page in enumerate(pages):
        slug = page["slug"]
        if slug in skip or slug.startswith("zb_mp_"):
            continue
        featured = get_media_url(page.get("featured_media", 0))
        if not featured:
            content_imgs = extract_content_images(page.get("content", {}).get("rendered", ""))
            featured = content_imgs[0] if content_imgs else fallback_image(i)
        result.append(
            {
                "slug": slug,
                "title": strip_html(page["title"]["rendered"]),
                "excerpt": strip_html(page.get("excerpt", {}).get("rendered", "")),
                "content": page["content"]["rendered"],
                "featuredImage": featured,
            }
        )
    return result


ESSENTIAL_IMAGES = [
    f"{SITE}/wp-content/uploads/2022/08/Frame-191.svg",
    f"{SITE}/wp-content/uploads/2022/08/Group-82.jpg",
    f"{SITE}/wp-content/uploads/2022/08/Group-10.jpg",
    f"{SITE}/wp-content/uploads/2022/08/cropped-Group-5-32x32.png",
    f"{SITE}/wp-content/uploads/2022/08/cropped-Group-5-180x180.png",
    f"{SITE}/wp-content/uploads/2022/08/cropped-Group-5-192x192.png",
    f"{SITE}/wp-content/uploads/2023/05/bloemen.jpg",
    f"{SITE}/wp-content/uploads/2023/05/kussen-1024x1016.jpg",
    f"{SITE}/wp-content/uploads/2023/05/meubels.jpg",
    f"{SITE}/wp-content/uploads/2023/05/klokken.jpg",
    f"{SITE}/wp-content/uploads/2023/05/spiegel.jpg",
    f"{SITE}/wp-content/uploads/2023/05/verlichting.jpg",
    f"{SITE}/wp-content/uploads/2023/05/wanddecoratie.jpg",
    f"{SITE}/wp-content/uploads/2023/05/geur.jpg",
    f"{SITE}/wp-content/uploads/2023/05/550x550-1.jpeg",
    f"{SITE}/wp-content/uploads/2023/05/550x550.jpeg",
    f"{SITE}/wp-content/uploads/2023/05/550x733-225x300.jpeg",
    f"{SITE}/wp-content/uploads/2026/06/pexels-praylin-jerish-480842390-28888404.jpg",
    f"{SITE}/wp-content/uploads/2026/05/image-11.png",
    f"{SITE}/wp-content/uploads/2026/05/image-4.png",
    f"{SITE}/wp-content/uploads/2026/05/image-3.png",
]


def download_essential():
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = []
        for url in ESSENTIAL_IMAGES:
            rel = url.split("/wp-content/uploads/", 1)[1]
            dest = PUBLIC_DIR / rel
            futures.append(pool.submit(download_file, url, dest))
        for f in as_completed(futures):
            f.result()


def main():
    print("Downloading essential images...")
    download_essential()

    print("Fetching posts...")
    posts = fetch_paginated("posts")
    print(f"  Found {len(posts)} posts")

    print("Fetching pages...")
    pages = fetch_paginated("pages")
    print(f"  Found {len(pages)} pages")

    blog_posts = process_posts(posts)
    site_pages = process_pages(pages)

    posts_path = DATA_DIR / "blog-posts.json"
    pages_path = DATA_DIR / "pages.json"

    if blog_posts:
        posts_path.write_text(json.dumps(blog_posts, indent=2, ensure_ascii=False))
    else:
        print("  Warning: no posts from API, keeping existing blog-posts.json")

    if site_pages:
        pages_path.write_text(json.dumps(site_pages, indent=2, ensure_ascii=False))
    else:
        print("  Warning: no pages from API, keeping existing pages.json")

    summary = {
        "posts": len(blog_posts),
        "pages": len(site_pages),
        "imagesDownloaded": sum(1 for _ in PUBLIC_DIR.rglob("*") if _.is_file()),
    }
    (ROOT / "migration-summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
