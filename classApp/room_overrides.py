"""DB/CSV를 변경하지 않는 화면 표시 전용 공간 예외 규칙."""

ROOM_DISPLAY_NAMES = {
    '9101': '피츠버그홀',
    '9301': '성미가엘성당',
}

SHARED_IMAGE_ROOMS = {
    '9202': '9201',
    '9203': '9201',
    '9204': '9201',
    '8b102': '8b101',
}

# 새천년관 화면에서만 중앙도서관 데이터를 함께 보여준다.
BUILDING_PAGE_EXTRA_SOURCES = {
    '새천년관': ('중앙도서관',),
}

# 원본 데이터에는 남겨 두되 지정된 건물 화면에서만 숨긴다.
BUILDING_PAGE_HIDDEN_ROOMS = {
    '새천년관': frozenset({'8102', '8103', '8203', '8303'}),
    '월당관': frozenset({'3102'}),
    '나눔관': frozenset({'5C202', '5C203', '5C206'}),
}

# 원본 details는 유지하고 지정된 건물 화면에서만 다른 이름으로 표시한다.
BUILDING_PAGE_DETAIL_OVERRIDES = {
    '일만관': {
        '2A501A': '강사실',
    },
    '새천년관': {
        '8202': '라운지',
    },
    '월당관': {
        '3103': '음악 실습실 - 1',
        '3104': '음악 실습실 - 2',
        '3201': '도서관 자유열람실 - 1',
        '3202': '도서관 자유열람실 - 2',
    },
}

# details가 있어도 강의실 카드와 시간표를 사용해야 하는 데이터 예외.
CLASSROOM_CLASSIFICATION_OVERRIDES = {
    '월당관': {
        'rules': (
            {'floor': 1, 'room_name_contains': '3103'},
            {'floor': 1, 'room_name_contains': '3104'},
        ),
    },
    '일만관': {
        'rules': (
            {'floor': 5, 'room_name_contains': '(강의실)'},
            {'floor': 1, 'room_name_contains': 'B105'},
        ),
    },
    '새천년관': {
        'rules': (
            {'floor': 7, 'room_name_contains': '7706'},
        ),
    },
    '성미가엘성당&피츠버그홀': {
        'rules': (
            {'floor': 3, 'room_name_contains': '9301'},
        ),
    },
}

# 원본 details가 비어 있어도 특수목적실로 표시해야 하는 호실.
NON_CLASSROOM_CLASSIFICATION_OVERRIDES = {
    '일만관': frozenset({'2A501A'}),
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

# 지정 층에서는 개별 교수연구실 카드를 숨기고 층 제목 옆 안내로 대체한다.
BUILDING_PAGE_PROFESSOR_ROOM_FLOORS = {
    '승연관': frozenset({3, 4}),
    '일만관': frozenset({2, 3, 4}),
    '정보과학관': frozenset({6}),
    '새천년관': frozenset({4, 5, 6, 7}),
}

FLOOR_DESCRIPTION_SEARCH_ITEMS = tuple(
    {
        'kwan_name': building_name,
        'floor_label': f'F{floor}',
        'description': '교수연구실이 있습니다.',
    }
    for building_name, floors in BUILDING_PAGE_PROFESSOR_ROOM_FLOORS.items()
    for floor in sorted(floors)
) + (
    {
        'kwan_name': '정보과학관',
        'floor_label': 'F3',
        'description': '교수연구실이 있습니다.',
    },
    {
        'kwan_name': '나눔관',
        'floor_label': 'B1',
        'description': '동아리실이 있습니다.',
    },
    {
        'kwan_name': '나눔관',
        'floor_label': 'F1',
        'description': '동아리실 · 동아리연합회 · 인권위원회 · 총학생회가 있습니다.',
    },
    {
        'kwan_name': '나눔관',
        'floor_label': 'F2',
        'description': '학부공동학생회실 · 동아리실이 있습니다.',
    },
    {
        'kwan_name': '미가엘관',
        'floor_label': 'F5 ~ F8',
        'description': MGELL_UPPER_FLOOR_DESCRIPTION,
    },
)


def is_room_hidden_on_building_page(room):
    """관별 화면 예외로 카드가 숨겨지는 실제 DB 공간인지 반환한다."""
    if room.room in BUILDING_PAGE_HIDDEN_ROOMS.get(room.kwan_name, ()):
        return True

    professor_floors = BUILDING_PAGE_PROFESSOR_ROOM_FLOORS.get(
        room.kwan_name, ()
    )
    if (
        room.floor in professor_floors
        and '교수연구실' in (room.details or '')
    ):
        return True

    if room.kwan_name == '나눔관':
        if room.floor == 1 and room.details in {
            '동아리실', '동아리연합회', '인권위원회', '총학생회'
        }:
            return True

    if room.kwan_name == '정보과학관' and room.floor == 3:
        return True
        if room.floor == 2 and (
            room.details == '동아리실'
            or room.details.startswith('학부공동학생회실')
        ):
            return True

    if (
        room.kwan_name == '미가엘관'
        and 5 <= room.floor <= 8
        and room.room not in MGELL_UPPER_VISIBLE_ROOMS
    ):
        return True

    return False
