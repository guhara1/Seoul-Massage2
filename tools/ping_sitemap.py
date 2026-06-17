#!/usr/bin/env python3
"""사이트맵 통보 자동화 (현행 방식 중심).

중요: 구글과 빙의 옛 'sitemap ping' HTTP 엔드포인트
(google.com/ping?sitemap=, bing.com/ping?sitemap=)는 2023년에 폐지되었다.
따라서 이 스크립트는
  1) (참고) 레거시 ping 을 시도하되 실패해도 무시하고,
  2) 실제 효과가 있는 IndexNow 통보(빙·네이버·얀덱스)를 실행한다.
구글은 IndexNow 미참여이므로 tools/google_index.py 또는 Search Console
사이트맵 제출을 사용한다.

사용법:  python3 tools/ping_sitemap.py
"""
import subprocess
import sys
import urllib.parse
import urllib.request

SITEMAP = "https://seoul-massage2.pages.dev/sitemap.xml"
LEGACY = [
    "https://www.google.com/ping?sitemap=",
    "https://www.bing.com/ping?sitemap=",
]


def legacy_ping():
    enc = urllib.parse.quote(SITEMAP, safe="")
    for base in LEGACY:
        url = base + enc
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                print(f"[레거시] {base} → {r.status}")
        except Exception as e:  # noqa: BLE001
            print(f"[레거시] {base} → 폐지/무응답({e}) — 무시")


def main():
    print("1) 레거시 sitemap ping (폐지됨, 참고용)")
    legacy_ping()
    print("\n2) IndexNow 통보(빙·네이버·얀덱스) — 실제 색인 경로")
    rc = subprocess.call([sys.executable,
                          __file__.replace("ping_sitemap.py", "indexnow.py")])
    print("\n구글 색인은 'python3 tools/google_index.py' 또는 "
          "Search Console 사이트맵 제출을 사용하세요.")
    sys.exit(rc)


if __name__ == "__main__":
    main()
