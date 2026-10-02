from django.shortcuts import render
from django.utils import timezone
from classApp.models import Room, Classes
from django.db.models import Q
from django.templatetags.static import static
from classApp.views import get_static_room_image, room_names_match
from classApp.room_overrides import (
    FLOOR_DESCRIPTION_SEARCH_ITEMS,
    is_room_hidden_on_building_page,
)

def base(request):
    return render(request, 'base.html')

def index(request):
    return render(request, 'index.html')

def introduce(request):
    return render(request, 'introduce.html')

def search(request):
    days = ['월', '화', '수', '목', '금', '토', '일',]
    now = timezone.now()
    now_time = now.time()
    weekday = now.weekday() #월:0 ~ 일:6
    now_weekday = days[weekday]

    q = request.GET.get('q', '')
    q = q.strip() # case1 : 입력 좌우에 공백 있는 경우 -> " 한국", "한국 "

    qs_list = q.split(' ') # case2 : 입력 중간에 공백 있는 경우 -> q='한국 사회' -> qs_list = ['한국','사회']
    
    # if ' ' not in q:
    #     qs2_list = list(q) #case3 : 입력에 공백 없는 경우 -> q='한국사회' -> qs2_list = ['한','국','사','회']

    roomsList = []
    classesList = []
    professorsList = []

    roomsAll = [
        room for room in Room.objects.all()
        if not is_room_hidden_on_building_page(room)
    ]
    classesAll = Classes.objects.all()
    class_room_names = set(classesAll.values_list('room1', flat=True)) | set(
        classesAll.values_list('room2', flat=True)
    )
    for room in roomsAll:
        room.is_search_classroom = (
            not room.details
            or (
                room.kwan_name == '일만관'
                and room.floor == 1
                and 'B105' in room.room
            )
            or (
                room.kwan_name == '새천년관'
                and room.floor == 7
                and room.room == '7706'
            )
            or (
                room.kwan_name == '성미가엘성당&피츠버그홀'
                and room.floor == 3
                and room.room == '9301'
            )
        )
        room.search_image_url = (
            get_static_room_image(room.room)
            or static(
                'images/classroom/nonimage.webp'
                if room.details
                else 'images/classroom/imagewait.webp'
            )
        )
        room.has_class = any(
            room_names_match(room.room, class_room)
            for class_room in class_room_names
        )
    professorsAll = classesAll

    rooms_result, classes_result, professors_result = "", "", ""
    floor_description_results = []

    if q:

        classes = []
        # spare1 = []
        # spare_count1 = {}
        for qs in qs_list: 
            classes += classesAll.filter(Q(class_name__icontains = qs)).distinct()
            #예시:한국사회 -> '한국' 들어간거 다 찾아서 리스트에 저장, '사회' 들어간거 다 저장 but 중복 제거 

        
        # for i in spare1: #뭘하고 잇는거지?
        #     try:
        #         spare_count1[i] +=1 
        #     except:
        #         spare_count1[i] = 1
        # output1 = []
        # for i, n in spare_count1.items():
        #     if n >= len(q)-1: #검색 단어의 길이정도만큼 겹치는 단어가 있는 경우 최종 결과에 담기 
        #         output1.append(i)
        # print("spare_count1는 도대체 뭔가?",spare_count1)
        # classes = output1
        
        
        query = q.casefold()
        floor_description_results = [
            item for item in FLOOR_DESCRIPTION_SEARCH_ITEMS
            if query in item['description'].casefold()
        ]
        rooms = [
            room for room in roomsAll
            if query in room.room.casefold() or query in room.details.casefold()
        ]
        professors = professorsAll.filter(Q(prof__icontains = q)).distinct()
        
        '''
        try: #공백 없는 입력이지만 데이터에는 공백이 있는 경우 데이터 찾기(예시:입력;한국사회, 데이터;한국 사회)
            if qs2_list:
                spare = []
                spare_count = {}
                for qs in qs2_list:
                    spare += classesAll.filter((Q(class_name__icontains = qs))).distinct()
                    # 예시:한국사회 -> '한' 들어간거 다 찾아서 리스트에 저장, '국'들어간거 다 저장, ....

                for i in spare:
                    try: #i가 딕셔너리에 있으면 1추가
                        spare_count[i] +=1
                    except: #없으면 1 세팅
                        spare_count[i] = 1

                output = []
                for i, n in spare_count.items():
                    if n >= len(q): #검색 단어의 길이정도만큼 겹치는 단어가 있는 경우 최종 결과에 담기 
                        output.append(i)

                classes = output
        except:
            pass
            
        '''

        # 중복 결과 제거
        rooms = set(rooms)
        rooms = list(rooms)
        classes = set(classes)
        classes = list(classes)
        professors = set(professors)
        professors = list(professors)


        for r in rooms:
            r.room_type = (
                "미개방"
                if r.is_search_classroom and not r.has_class
                else "사용가능"
            )

            #date1에 대해
            for c in classesAll.filter(Q(date1 = now_weekday)):
                if c.start <= now_time and now_time <= c.end:
                    if room_names_match(r.room, c.room1):
                        r.room_type = "수업중"
                        break
            #date2에 대해
            if r.room_type != "수업중":
                for c in classesAll.filter(Q(date2 = now_weekday)):
                    if c.start <= now_time and now_time <= c.end:
                        if room_names_match(r.room, c.room2):
                            r.room_type = "수업중"
                            break
            roomsList.append(r)

        '''
        for c in classes:
            classesList.append(c)
        
        for p in professors:
            professorsList.append(p)
        '''
           
        # 중복 결과 제거
        roomsList = set(roomsList)
        roomsList = list(roomsList)


        if len(rooms) == 0 and len(floor_description_results) == 0:
            rooms_result = "강의실 검색 결과가 없습니다."
        
        if len(classes) == 0:
            classes_result = "강의명 검색 결과가 없습니다."
        
        if len(professors) == 0:
            professors_result = "해당 교수님이 진행하는 강의 검색 결과가 없습니다."
    
    else:
        rooms, classes, professors = "", "", ""
        rooms_result = "강의실 검색 결과가 없습니다."
        classes_result = "강의명 검색 결과가 없습니다."
        professors_result = "해당 교수님이 진행하는 강의 검색 결과가 없습니다."
    

    return render(request, 'search.html',
    {'q': q,
    'now_time': now_time,
    'now_weekday': now_weekday,
    'roomsAll': roomsAll,
    'rooms': rooms, 'classes': classes, 'professors': professors,
    'floor_description_results': floor_description_results,
    'roomsList': roomsList, 'classesList': classesList, 'professorsList': professorsList,
    'rooms_result': rooms_result, 'classes_result': classes_result, 'professors_result': professors_result,
    })
