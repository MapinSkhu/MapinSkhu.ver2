from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Classes, Room
from django.utils import timezone
from django.db.models import Q, Case, When

days = ['월', '화', '수', '목', '금', '토', '일']

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

    now = timezone.now() #형식: yyyy-mm-dd hh:mm:ss.ssssss
    now_weekday = now.weekday() #0~6
    now_weekday_str = days[now_weekday] #월~일

    class_dict = {} # 요일(key)별로 my_room에서 진행되는 수업리스트(value)를 저장

    for index, value in enumerate(days[:5]): #value:월~금
        extract_list = [] # my_room 수업 저장
        for c in week_classes[index]: #요일별 수업리스트 돌면서
            if ((c.room1 == my_room.room) or (c.room2 == my_room.room)): #사용자가 선택한 강의실과 일치하면
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
    classes = Classes.objects.all().filter(Q(kwan_name = my_kwan))
    classes = classes.filter((Q(date1 = now_weekday) | Q(date2 = now_weekday)))
    # kwan_img_url = get_object_or_404(Kwan, kwan_image = my_kwan)

    # print("rooms 길이: ", len(rooms))

    rooms_list = []

    rooms_access = []
    rooms_unaccess = []

    for r in rooms:
        r.room_type = "사용가능"

        for c in classes:
            if c.start <= now_time and now_time <= c.end:
                if (r.room == c.room1 or r.room == c.room2):
                    r.room_type = "사용불가"
                    rooms_unaccess.append(r)
        if r.room_type == "사용가능":
            rooms_access.append(r)
        rooms_list.append(r)

    # print("rooms_list 길이: ", len(rooms_list))
    return {
        'now_date' : now_date, 
        'now_time' : now_time, 
        'now_weekday' : now_weekday, 
        'rooms' : rooms, 
        'classes' : classes, 
        'rooms_list' : rooms_list, 
        'rooms_access': rooms_access,
        'rooms_unaccess': rooms_unaccess,
        # 'kwan_img_url' : kwan_img_url,
    }



# 1관 승연관
def sy_gwan(request):
    return render(request, 'class/sy_gwan.html', kwan_fn(my_kwan = "승연관"))

# 2관 일만관
def im_gwan(request):
    return render(request, 'class/im_gwan.html', kwan_fn(my_kwan = "일만관"))

# 3관 월당관
def wd_gwan(request):
    return render(request, 'class/wd_gwan.html', kwan_fn(my_kwan = "월당관"))

# 5관 나눔관
def nn_gwan(request):
    return render(request, 'class/nn_gwan.html', kwan_fn(my_kwan = "나눔관"))

# 6관 정보과학관
def jg_gwan(request):
    return render(request, 'class/jg_gwan.html', kwan_fn(my_kwan = "정보과학관"))

# 7관 새천년관
def scn_gwan(request):
    return render(request, 'class/scn_gwan.html', kwan_fn(my_kwan = "새천년관"))

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
    return render(request, 'class/mgell_gwan.html', kwan_fn(my_kwan = "미가엘관"))

# 12관 성베드로학교
def sbdr_school(request):
    return render(request, 'class/sbdr_school.html', kwan_fn(my_kwan = "성베드로학교"))

# 13관 행복기숙사
def dormitory(request):
    return render(request, 'class/dormitory.html', kwan_fn(my_kwan = "행복기숙사"))

# 강의실 디테일 페이지
def classroom(request, room):
    try:
        my_room = Room.objects.get(room = room) #디비에 room 존재하지 않으면 back(index로)
        return render(
            request, 
            'classroom.html',
            classroom_fn(my_room = my_room)
        )

    except:
        return render(request, 'index.html')
    


####### API VIEW  : DRF  사용할 경우 #######

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ClassroomListSerializer

@api_view(['GET'])
def classroom_list(request):
    # 1. 프론트가 보낸 쿼리 파라미터(필터링 조건) 읽기
    building = request.query_params.get('building_name')
    time = request.query_params.get('time')
    floor = request.query_params.get('floor')
    isEmpty = request.query_params.get('isEmptyRoom')
    
    # 2. DB에서 필터링해서 가져오기
    queryset = Classes.objects.all()
    if building:
        queryset = queryset.filter(kwan_name=building)
    if floor:
        queryset = queryset.filter(floor=floor)
        
    # 3. Serializer를 통해 JSON으로 변환 후 응답
    serializer = ClassroomListSerializer(queryset, many=True, context={'request': request})
    return Response({"classroom_list": serializer.data})