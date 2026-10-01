from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Classes, Room
from django.utils import timezone
from django.db.models import Q, Case, When
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from pathlib import Path
from types import SimpleNamespace
from .room_overrides import (
    BUILDING_PAGE_EXTRA_SOURCES,
    BUILDING_PAGE_DETAIL_OVERRIDES,
    BUILDING_PAGE_HIDDEN_ROOMS,
    BUILDING_PAGE_PROFESSOR_ROOM_FLOORS,
    CLASSROOM_CLASSIFICATION_OVERRIDES,
    MGELL_UPPER_FLOOR_DESCRIPTION,
    MGELL_UPPER_VISIBLE_ROOMS,
    NON_CLASSROOM_CLASSIFICATION_OVERRIDES,
    SHARED_IMAGE_ROOMS,
    VIRTUAL_BUILDING_ROOMS,
)

days = ['월', '화', '수', '목', '금', '토', '일']


def room_names_match(room_name, class_room_name):
    room_name = str(room_name).strip()
    class_room_name = str(class_room_name).strip()
    if room_name == class_room_name:
        return True

    if (
        len(room_name) > 1
        and room_name[0].isdigit()
        and room_name[1:].upper() == class_room_name.upper()
    ) or (
        len(class_room_name) > 1
        and class_room_name[0].isdigit()
        and class_room_name[1:].upper() == room_name.upper()
    ):
        return True

    if '~' not in room_name:
        return False

    range_start, range_end = (part.strip() for part in room_name.split('~', 1))
    if range_end.isdigit() and len(range_end) < len(range_start):
        range_end = f'{range_start[:-len(range_end)]}{range_end}'
    return class_room_name in {range_start, range_end}


def get_static_room_image(room_number):
    """호수 이름으로 추가된 정적 이미지를 찾아 URL을 반환한다."""
    normalized_room = room_number.strip().lower()
    normalized_room = SHARED_IMAGE_ROOMS.get(normalized_room, normalized_room)
    for extension in ('webp', 'jpg', 'jpeg', 'png'):
        image_path = f'images/classroom/{normalized_room}.{extension}'
        found_image = finders.find(image_path)
        if found_image:
            modified_time = Path(found_image).stat().st_mtime_ns
            return f'{static(image_path)}?v={modified_time}'
    return None

# 요일별 강의 쿼리셋으로 추출 후 리스트로 묶기
week_classes = [] # 인덱스 (월:0 ~ 금:4)
for w in range(len(days)-2): 
    week_classes.append(
        Classes.objects.filter(Q(date1 = days[w]) | Q(date2 = days[w])).order_by('end','start')
    )

def classroom_fn(my_room):#단순 room 문자열 아닌 room 객체 받기
    '''
    func : 사용자가 선택한 강의 보이기 
    0. 요일별로 강의 묶어서 리스트로 저장해두기-> week_classes
    1. 사용자가 선택한 강의실(my_room)의 강의만 week_classes에서 추출해서 템플릿에 전달
    -> 요일을 key로, 요일의 수업리스트를 value로 저장한 딕셔너리 전달
    2. 오늘 요일 템플릿에 전달
    -> 템플릿에서 오늘 요일 시간표 먼저 보이기    
    3. 해당 강의실에 강의 없는 경우 'empty' 전달
    '''

    my_room.detail_image_url = (
        get_static_room_image(my_room.room)
        or static('images/classroom/imagewait.webp')
    )

    now = timezone.now() #형식: yyyy-mm-dd hh:mm:ss.ssssss
    now_weekday = now.weekday() #0~6
    now_weekday_str = days[now_weekday] #월~일

    class_dict = {} # 요일(key)별로 my_room에서 진행되는 수업리스트(value)를 저장

    for index, value in enumerate(days[:5]): #value:월~금
        extract_list = [] # my_room 수업 저장
        for c in week_classes[index]: #요일별 수업리스트 돌면서
            if room_names_match(my_room.room, c.room1) or room_names_match(my_room.room, c.room2): #사용자가 선택한 강의실과 일치하면
                # if c.date2 == None:
                #     c.date2 = ""
                extract_list.append(c) #리스트로 저장
        if len(extract_list) == 0: #추출된 강의가 1도 없으면
            class_dict[value] = 'empty' #해당요일 dict value에는 empty 저장
        else:
            class_dict[value] = extract_list #추출된 강의 있으면 그 리스트를 dict value로 저장

    '''
    현재 요일의 수업리스트에서 현재 시간과 비교 -> start~end에 현재시간이 있다면 그 수업을 템플릿에 전달
    '''
    now_time = now.time() #형식: hh:mm:ss.ssssss
    now_class_name = 'empty' #현재 진행중인 수업 저장, 기본값은 empty

    if now_weekday != 5 and now_weekday != 6: #현재 요일이 토/일 아닌 경우
        now_class_list = class_dict.get(now_weekday_str) #dict.get(x) : key가 x인 value 추출, 여기선 현재 요일 수업리스트 추출
        if now_class_list != 'empty': #empty가 아니라면
            
            for c in now_class_list: #현재 요일 수업리스트 돌면서
                if c.start <= now_time: #수업 시작시간이 현재 시간보다 크거나 같고
                    if now_time < c.end: #수업 끝시간이 현재 시간보다 작으면 (등호는 곧 수업이 종료되기 때문에 뺌)
                        now_class_name = c.class_name #그것이 바로 현재 진행중인 수업이로다

    return {
        'my_room' : my_room,
        'now_class_name' : now_class_name,
        'now_weekday_str' : now_weekday_str, 
        'class_dict' : class_dict,
    }


def kwan_fn(my_kwan):
    days = ['월', '화', '수', '목', '금', '토', '일']
    now = timezone.now()
    now_date = now.date()
    now_time = now.time()
    weekday = now.weekday() #월:0 ~ 일:6
    now_weekday = days[weekday]

    rooms = Room.objects.all().filter(Q(kwan_name = my_kwan)).order_by('room')
    
    classes = Classes.objects.filter((Q(date1 = now_weekday) | Q(date2 = now_weekday)))
    class_room_names = set(Classes.objects.values_list('room1', flat=True)) | set(
        Classes.objects.values_list('room2', flat=True)
    )
    rooms_list = []
    rooms_access = []
    rooms_unaccess = []

    for r in rooms:
        r.has_class = any(
            room_names_match(r.room, class_room)
            for class_room in class_room_names
        )
        is_numbered_classroom = (
            bool(r.room.strip())
            and not r.details.strip()
            and '(' not in r.room
        )
        classification_override = CLASSROOM_CLASSIFICATION_OVERRIDES.get(r.kwan_name)
        is_classroom_override = any(
            r.floor == rule['floor']
            and rule['room_name_contains'] in r.room
            for rule in classification_override.get('rules', ())
        ) if classification_override else False
        r.is_classroom = (
            is_numbered_classroom or is_classroom_override
        )
        if r.room in NON_CLASSROOM_CLASSIFICATION_OVERRIDES.get(r.kwan_name, ()):
            r.is_classroom = False
        normalized_room = r.room.strip().upper()
        r.is_basement = (
            normalized_room.startswith('B')
            or (len(normalized_room) > 1 and normalized_room[1] == 'B')
        )
        r.basement_level = 1 if r.is_basement else None
        static_room_image = get_static_room_image(r.room)
        r.is_image_missing = not static_room_image
        if static_room_image:
            r.card_image_url = static_room_image
        elif r.is_classroom:
            r.card_image_url = static('images/classroom/imagewait.webp')
        else:
            r.card_image_url = static('images/classroom/nonimage.webp')
        r.room_type = "미개방" if r.is_classroom and not r.has_class else "사용가능"

        for c in classes:
            # 3. 시간 비교
            if c.start <= now_time and now_time <= c.end:
                # 4. 방 번호 비교 (여기서 일치하면 어차피 이 건물 수업임)
                if room_names_match(r.room, c.room1) or room_names_match(r.room, c.room2):
                    r.room_type = "수업중"
                    rooms_unaccess.append(r)
                    break # 수업이 1개라도 있으면 사용불가 처리하고 검사 중지
                    
        if r.is_classroom and r.room_type == "사용가능":
            rooms_access.append(r)
            
        rooms_list.append(r)

        rooms_list.sort(key=lambda room: (room.floor, not room.is_classroom, room.room))

    return {
        'now_date' : now_date, 
        'now_time' : now_time, 
        'now_weekday' : now_weekday, 
        'rooms' : rooms, 
        'classes' : classes, 
        'rooms_list' : rooms_list, 
        'rooms_access': rooms_access,
        'rooms_unaccess': rooms_unaccess,
    }


def hide_professor_room_cards(context, building_name):
    hidden_floors = BUILDING_PAGE_PROFESSOR_ROOM_FLOORS.get(
        building_name, frozenset()
    )
    for key in ('rooms_list', 'rooms_access', 'rooms_unaccess'):
        context[key] = [
            room for room in context[key]
            if not (
                room.floor in hidden_floors
                and '교수연구실' in (room.details or '')
            )
        ]
    return context

# 1관 승연관
def sy_gwan(request):
    context = hide_professor_room_cards(kwan_fn(my_kwan="승연관"), "승연관")
    return render(request, 'class/sy_gwan.html', context)

# 2관 일만관
def im_gwan(request):
    context = kwan_fn(my_kwan="일만관")
    detail_overrides = BUILDING_PAGE_DETAIL_OVERRIDES.get('일만관', {})
    for room in context['rooms_list']:
        room.details = detail_overrides.get(room.room, room.details)
    hide_professor_room_cards(context, "일만관")
    return render(request, 'class/im_gwan.html', context)

# 3관 월당관
def wd_gwan(request):
    context = kwan_fn(my_kwan="월당관")
    hidden_rooms = BUILDING_PAGE_HIDDEN_ROOMS.get('월당관', frozenset())
    detail_overrides = BUILDING_PAGE_DETAIL_OVERRIDES.get('월당관', {})

    for room in context['rooms_list']:
        room.details = detail_overrides.get(room.room, room.details)

    for key in ('rooms_list', 'rooms_access', 'rooms_unaccess'):
        context[key] = [room for room in context[key] if room.room not in hidden_rooms]

    return render(request, 'class/wd_gwan.html', context)

# 5관 나눔관
def nn_gwan(request):
    context = kwan_fn(my_kwan="나눔관")
    hidden_rooms = BUILDING_PAGE_HIDDEN_ROOMS.get('나눔관', frozenset())
    hidden_details = {'동아리실', '동아리연합회', '인권위원회', '총학생회'}
    for key in ('rooms_list', 'rooms_access', 'rooms_unaccess'):
        context[key] = [
            room for room in context[key]
            if room.room not in hidden_rooms
            and not (
                room.floor == 1 and room.details in hidden_details
            ) and not (
                room.floor == 2
                and (
                    room.details == '동아리실'
                    or room.details.startswith('학부공동학생회실')
                )
            )
        ]
    return render(request, 'class/nn_gwan.html', context)

# 6관 정보과학관
def jg_gwan(request):
    context = kwan_fn(my_kwan="정보과학관")
    hide_professor_room_cards(context, "정보과학관")
    return render(request, 'class/jg_gwan.html', context)

# 7관 새천년관
def scn_gwan(request):
    context = kwan_fn(my_kwan="새천년관")
    hidden_rooms = BUILDING_PAGE_HIDDEN_ROOMS.get('새천년관', frozenset())
    detail_overrides = BUILDING_PAGE_DETAIL_OVERRIDES.get('새천년관', {})

    for source_name in BUILDING_PAGE_EXTRA_SOURCES.get('새천년관', ()):
        source_context = kwan_fn(my_kwan=source_name)
        for key in ('rooms_list', 'rooms_access', 'rooms_unaccess'):
            context[key].extend(source_context[key])

    for room in context['rooms_list']:
        room.details = detail_overrides.get(room.room, room.details)

    for key in ('rooms_list', 'rooms_access', 'rooms_unaccess'):
        context[key] = [
            room for room in context[key]
            if room.room not in hidden_rooms
        ]

    hide_professor_room_cards(context, "새천년관")

    for virtual_room in VIRTUAL_BUILDING_ROOMS.get('새천년관', ()):
        virtual_image = get_static_room_image(virtual_room['room'])
        context['rooms_list'].append(SimpleNamespace(
            id=None,
            kwan_name='새천년관',
            floor=-virtual_room['basement_level'],
            is_basement=True,
            is_classroom=False,
            has_class=False,
            room_type=None,
            is_image_missing=not virtual_image,
            card_image_url=(
                virtual_image or static('images/classroom/nonimage.webp')
            ),
            **virtual_room,
        ))

    context['rooms_list'].sort(
        key=lambda room: (room.floor, not room.is_classroom, room.room)
    )

    return render(request, 'class/scn_gwan.html', context)

# 8관 중앙도서관
def library(request):
    return render(request, 'class/library.html', kwan_fn(my_kwan = "중앙도서관"))

# 9관 피츠버그홀
def pb_hall(request):
    return render(request, 'class/pb_hall.html', kwan_fn(my_kwan = "성미가엘성당&피츠버그홀"))

# 10관 구두인관
def gdin_gwan(request):
    return render(request, 'class/gdin_gwan.html', kwan_fn(my_kwan = "구두인관"))

# 11관 미가엘관
def mgell_gwan(request):
    context = kwan_fn(my_kwan="미가엘관")
    for room in context['rooms_list']:
        room.show_in_upper_floor = room.room in MGELL_UPPER_VISIBLE_ROOMS
    context['upper_floor_description'] = MGELL_UPPER_FLOOR_DESCRIPTION
    return render(request, 'class/mgell_gwan.html', context)

# 12관 성베드로학교
def sbdr_school(request):
    return render(request, 'class/sbdr_school.html', kwan_fn(my_kwan = "성베드로학교"))

# 13관 행복기숙사
def dormitory(request):
    return render(request, 'class/dormitory.html', kwan_fn(my_kwan = "행복기숙사"))

# 강의실 디테일 페이지
def classroom(request, id):
    try:
        my_room = Room.objects.get(id = id) #디비에 room 존재하지 않으면 back(index로)
        return render(
            request, 
            'classroom.html',
            classroom_fn(my_room = my_room)
        )

    except:
        return render(request, 'index.html')
