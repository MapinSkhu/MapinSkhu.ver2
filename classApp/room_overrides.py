"""DB/CSV를 변경하지 않는 화면 표시 전용 공간 예외 규칙."""

ROOM_DISPLAY_NAMES = {
    '9101': '피츠버그홀',
    '9301': '성미가엘성당',
}

SHARED_IMAGE_ROOMS = {
    '9202': '9201',
    '9203': '9201',
    '9204': '9201',
    '8b101': '8B101',
    '8b102': '8B101',
}

# 새천년관 화면에서만 중앙도서관 데이터를 함께 보여준다.
BUILDING_PAGE_EXTRA_SOURCES = {
    '새천년관': ('중앙도서관',),
}

# 원본 데이터에는 남겨 두되 지정된 건물 화면에서만 숨긴다.
BUILDING_PAGE_HIDDEN_ROOMS = {
    '새천년관': frozenset({'8102', '8103', '8202', '8203', '8303'}),
}

# details가 있어도 강의실 카드와 시간표를 사용해야 하는 데이터 예외.
CLASSROOM_CLASSIFICATION_OVERRIDES = {
    '일만관': {
        'floor': 5,
        'room_name_contains': '(강의실)',
    },
}

# 원본 데이터에 없는 화면 전용 공간. 실제 호실 데이터가 추가되면 이 항목을 제거한다.
VIRTUAL_BUILDING_ROOMS = {
    '새천년관': (
        {'room': 'VIRTUAL-B2-PARKING', 'details': '지하주차장', 'basement_level': 2},
        {'room': 'VIRTUAL-B2-MACHINE', 'details': '기계실', 'basement_level': 2},
        {'room': 'VIRTUAL-B2-ELECTRIC', 'details': '전기실', 'basement_level': 2},
    ),
}

MGELL_UPPER_VISIBLE_ROOMS = frozenset({'M809', 'M814'})
MGELL_UPPER_FLOOR_DESCRIPTION = '성공회대학교 미가엘기숙사가 존재합니다.'
