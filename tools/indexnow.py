#!/usr/bin/env python3
"""IndexNow 즉시 색인 통보 — 빙·네이버·얀덱스에 한 번에 전달.

IndexNow 는 한 곳(api.indexnow.org)에 통보하면 참여 검색엔진(Bing, Naver,
Yandex, Seznam)에 함께 전파된다. 구글은 IndexNow 미참여이므로 별도
(tools/google_index.py 또는 Search Console)로 처리한다.

준비물(이미 저장소에 셋업됨):
  - 루트의 키 파일:  https://<도메인>/35ef6a8d6cc69568452f8e3b898d69c7.txt
    (내용은 키 문자열 한 줄)

사용법:
  python3 tools/indexnow.py                 # sitemap.xml 의 모든 URL 통보
  python3 tools/indexnow.py URL1 URL2 ...    # 특정 URL만 통보(글 올릴 때)
"""
import json
import os
import re
import sys
import urllib.request

KEY = "35ef6a8d6cc69568452f8e3b898d69c7"
BASE_URL = "https://seoul-massage2.pages.dev"
ENDPOINT = "https://api.indexnow.org/indexnow"   # 대표 엔드포인트(전 엔진 전파)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def host_of(url):
    return re.sub(r"^https?://([^/]+).*$", r"\1", url)


def urls_from_sitemap():
    path = os.path.join(ROOT, "sitemap.xml")
    if not os.path.exists(path):
        sys.exit("sitemap.xml 이 없습니다. 먼저 python3 build.py 를 실행하세요.")
    with open(path, encoding="utf-8") as f:
        return re.findall(r"<loc>([^<]+)</loc>", f.read())


def submit(urls):
    host = host_of(BASE_URL)
    payload = {
        "host": host,
        "key": KEY,
        "keyLocation": f"{BASE_URL.rstrip('/')}/{KEY}.txt",
        "urlList": urls,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"IndexNow 응답 {resp.status} — {len(urls)}개 URL 통보 완료")
            print("  (200/202 면 정상. 빙·네이버·얀덱스로 전파됩니다.)")
    except urllib.error.HTTPError as e:
        print(f"HTTP 오류 {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}")
        sys.exit(1)
    except Exception as e:  # noqa: BLE001
        print(f"통보 실패: {e}")
        sys.exit(1)


def main():
    urls = sys.argv[1:] or urls_from_sitemap()
    if not urls:
        sys.exit("통보할 URL이 없습니다.")
    # IndexNow 는 1회 최대 10,000개. 안전하게 1,000개씩 나눠 보낸다.
    for i in range(0, len(urls), 1000):
        submit(urls[i:i + 1000])


if __name__ == "__main__":
    main()
