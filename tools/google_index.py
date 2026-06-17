#!/usr/bin/env python3
"""구글 Indexing API 색인 통보 (구글은 IndexNow 미참여).

구글 Indexing API 는 공식적으로 JobPosting·BroadcastEvent 용이지만 URL
업데이트 통보(URL_UPDATED)에 널리 쓰인다. 서비스 계정 인증이 필요하다.

준비(최초 1회):
  1) Google Cloud Console 에서 프로젝트 생성 → 'Indexing API' 사용 설정.
  2) 서비스 계정 생성 후 JSON 키를 내려받아 tools/service_account.json 로 저장
     (이 파일은 비밀이므로 .gitignore 에 추가되어 커밋되지 않음).
  3) Search Console 에서 해당 사이트(또는 도메인) 속성에 서비스 계정 이메일을
     '소유자'로 추가.
  4) 의존성 설치:
     pip install google-auth requests

사용법:
  python3 tools/google_index.py                 # sitemap.xml 의 모든 URL
  python3 tools/google_index.py URL1 URL2 ...    # 특정 URL만
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SA_PATH = os.path.join(ROOT, "tools", "service_account.json")
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SCOPES = ["https://www.googleapis.com/auth/indexing"]


def urls_from_sitemap():
    path = os.path.join(ROOT, "sitemap.xml")
    if not os.path.exists(path):
        sys.exit("sitemap.xml 이 없습니다. 먼저 python3 build.py 를 실행하세요.")
    with open(path, encoding="utf-8") as f:
        return re.findall(r"<loc>([^<]+)</loc>", f.read())


def main():
    if not os.path.exists(SA_PATH):
        sys.exit(f"서비스 계정 키가 없습니다: {SA_PATH}\n"
                 "파일 상단의 준비 절차를 먼저 진행하세요.")
    try:
        import requests
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        sys.exit("의존성이 필요합니다:  pip install google-auth requests")

    creds = service_account.Credentials.from_service_account_file(
        SA_PATH, scopes=SCOPES)
    session = AuthorizedSession(creds)

    urls = sys.argv[1:] or urls_from_sitemap()
    ok = err = 0
    # 구글 Indexing API 일일 기본 할당량은 200건. 초과분은 다음 날 재실행.
    for url in urls:
        r = session.post(ENDPOINT, json={"url": url, "type": "URL_UPDATED"})
        if r.status_code == 200:
            ok += 1
        else:
            err += 1
            print(f"  실패 {r.status_code}: {url}  {r.text[:160]}")
    print(f"구글 통보 완료 — 성공 {ok} / 실패 {err} (일일 할당량 약 200건)")


if __name__ == "__main__":
    main()
