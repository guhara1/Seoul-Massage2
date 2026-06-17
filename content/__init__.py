# 전체 페이지 목록 집계
# 1) 자동 생성 모듈을 먼저 불러와 링크/역 그룹 레지스트리에 등록한다.
#    (districts/stations/main 이 import 시점에 헬퍼를 호출하므로 그 전에 등록)
from . import dongs_gen, stations_gen
from .site import (register_dong_pages, register_stations,
                   register_consolidated)

register_dong_pages(dongs_gen.ALL_DONG_SLUGS)
register_stations(stations_gen.FULL_STATION_GROUPS)

# 레지스트리가 모두 채워진 뒤 자동 생성 페이지를 만든다(내부링크 sibling 해석).
dongs_gen.PAGES = dongs_gen.build()
stations_gen.PAGES = stations_gen.build()

# 2) 통합(consolidation) — 얇은 자동생성 동·역 페이지는 개별 페이지를 만들지 않고
#    소속 자치구 페이지로 301 통합한다. 수기 작성 상세 페이지(dongs.py·stations.py)와
#    자치구·생활권·메인은 그대로 유지한다.
#    이 등록은 반드시 main/districts/zones/stations/dongs import(=본문 생성) 전에
#    이뤄져야 내부 링크가 자치구 페이지를 가리킨다.
def _consolidation_map(pages):
    m = {}
    for p in pages:
        crumbs = p.get("breadcrumb") or []
        target = None
        for _, href in crumbs:
            if href and href.startswith("/seoul/"):  # 자치구 URL
                target = href
                break
        if target:
            m[p["path"]] = target
    return m


# 권역(area) 허브가 직접 연결하는 핵심 역세권은 개별 페이지로 되살린다(통합 제외).
REVIVE_STATIONS = {
    "gangdong-station-chuljangmassage", "myeongdong-station-chuljangmassage",
    "gwanghwamun-station-chuljangmassage", "hoegi-station-chuljangmassage",
    "changdong-station-chuljangmassage", "miasageori-station-chuljangmassage",
    "ssangmun-station-chuljangmassage", "magongnaru-station-chuljangmassage",
    "kkachisan-station-chuljangmassage", "omokgyo-station-chuljangmassage",
}


def _is_revived(path):
    return path.rstrip("/").split("/")[-1] in REVIVE_STATIONS


REDIRECTS = {}
REDIRECTS.update(_consolidation_map(dongs_gen.PAGES))
REDIRECTS.update({k: v for k, v in _consolidation_map(stations_gen.PAGES).items()
                  if not _is_revived(k)})
register_consolidated(REDIRECTS)

# 되살린 역 페이지는 통합 등록 '후' 다시 빌드해야 본문 내부 링크가 통합을
# 인식한다(첫 build() 는 통합 전이라 통합된 역으로 죽은 링크가 생긴다).
_revived_station_pages = [p for p in stations_gen.build() if _is_revived(p["path"])]

# 3) 나머지 페이지 모듈 import (등록된 레지스트리·통합 정보를 사용)
from . import main, areas, districts, dongs, stations, zones, info

# 통합된 얇은 페이지는 PAGES 에서 제외 → 빌드/사이트맵 미포함.
PAGES = (
    [main.PAGE]
    + areas.PAGES
    + districts.PAGES
    + dongs.PAGES
    + stations.PAGES
    + _revived_station_pages
    + zones.PAGES
    + info.PAGES
)
