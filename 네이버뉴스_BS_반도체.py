import csv
import re
import sys
import time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


SEARCH_URL = "https://search.naver.com/search.naver"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9",
}


def fetch(url, params=None):
    response = requests.get(url, params=params, headers=HEADERS, timeout=15)
    response.raise_for_status()
    response.encoding = "utf-8"
    return BeautifulSoup(response.text, "html.parser")


def clean_text(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    return text.replace("새 창 열림", "").strip()


def get_news_results(query, count=10):
    soup = fetch(SEARCH_URL, {
        "where": "news",
        "sm": "tab_jum",
        "query": query,
    })
    results = []
    seen_links = set()

    for anchor in soup.select("a[href]"):
        link = anchor.get("href", "")
        title = clean_text(anchor.get_text(" ", strip=True))

        # 기사 제목처럼 보이는 링크만 선택한다.
        if len(title) < 15 or title in {"네이버 뉴스", "뉴스홈"}:
            continue
        parsed_link = urlparse(link)
        hostname = parsed_link.hostname or ""
        is_news_link = (
            "news.naver.com/mnews/article" in link
            or "n.news.naver.com/mnews/article" in link
            or "/News/Read" in link
            or "news" in hostname.lower()
            or "news" in parsed_link.path.lower()
        )
        if not is_news_link:
            continue
        if "channelPromotion" in link or "static/channel" in link:
            continue
        if link in seen_links:
            continue

        description = ""
        card = anchor.parent
        for _ in range(8):
            if card is None:
                break
            text = clean_text(card.get_text(" ", strip=True))
            text_without_title = text.replace(title, "", 1).strip()
            if len(text_without_title) >= 20:
                description = text_without_title
                break
            card = card.parent

        # 카드 전체에서 선택된 기사의 제목이 아닌 본문 후보를 찾음
        if not description and card is not None:
            description = clean_text(card.get_text(" ", strip=True))

        seen_links.add(link)
        results.append({
            "title": title,
            "description": description,
            "link": link,
            "body": "",
        })
        if len(results) >= count:
            break

    return results


def get_naver_article_body(link):
    """네이버 뉴스 기사 페이지에서 본문만 추출한다."""
    soup = fetch(link)
    body = soup.select_one("#dic_area") or soup.select_one("#articeBody")
    if body is None:
        return ""

    for unwanted in body.select("script, style, .end_photo_org"):
        unwanted.decompose()
    return clean_text(body.get_text("\n", strip=True))


def get_article_body(link):
    """네이버 또는 언론사 페이지에서 기사 본문을 추출한다."""
    soup = fetch(link)
    selectors = (
        "#dic_area",
        "#articeBody",
        "#newsct_article",
        ".news_body",
        "#article_body",
        ".article_body",
        "[itemprop='articleBody']",
    )
    for selector in selectors:
        body = soup.select_one(selector)
        if body:
            for unwanted in body.select("script, style, iframe, .view_ad02, .ad, .advertisement"):
                unwanted.decompose()
            text = clean_text(body.get_text("\n", strip=True))
            if len(text) >= 50:
                return text
    return ""


def save_csv(results, filename="반도체_뉴스.csv"):
    with open(filename, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=["title", "description", "link", "body"]
        )
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    query = "반도체"
    news = get_news_results(query, count=10)

    for index, item in enumerate(news, start=1):
        print(f"\n[{index}] {item['title']}")
        print(item["description"])
        print(item["link"])

        try:
            item["body"] = get_article_body(item["link"])
            print(item["body"][:300])
        except requests.RequestException as error:
            print(f"본문을 가져오지 못했습니다: {error}")
        time.sleep(0.5)

    save_csv(news)
    print(f"\n총 {len(news)}건을 반도체_뉴스.csv에 저장했습니다.")
