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

# 2) 포괄적 커버리지 — 1~9호선 전 역과 대표 행정동(번호 동은 DONG_DATA 단계에서
#    이미 대표 동으로 통합됨)을 모두 개별 페이지로 제공한다. 도어웨이 위험은
#    기획서 16번대로 '권역 허브 구조 + 역마다 고유 콘텐츠 + 역당 1페이지(노선
#    미분할)'로 방어한다. 따라서 별도 통합(리다이렉트)은 두지 않는다.
REDIRECTS = {}
register_consolidated(REDIRECTS)

# 3) 나머지 페이지 모듈 import (등록된 레지스트리를 사용)
from . import main, areas, districts, dongs, stations, zones, info

PAGES = (
    [main.PAGE]
    + areas.PAGES
    + districts.PAGES
    + dongs.PAGES
    + dongs_gen.PAGES
    + stations.PAGES
    + stations_gen.PAGES
    + zones.PAGES
    + info.PAGES
)
