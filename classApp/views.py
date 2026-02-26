from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from .models import Room, Classes
from django.db.models import Q
import logging
from django.shortcuts import get_object_or_404

# 터미널에서 데이터를 확인하기 위한 로거 설정 (선택사항)
logger = logging.getLogger(__name__)

@csrf_exempt
def get_classroom_list(request):
    # 1. 파라미터 가져오기 및 공백 제거 (.strip())
    # 한글 파라미터가 올 경우를 대비해 확실히 가져옵니다.
    building_name = request.GET.get('building_name', '').strip()
    floor_raw = request.GET.get('floor', '').strip()
    
    # "true"라는 문자열이 들어오면 True로 변환
    is_empty_only = request.GET.get('isEmptyRoom', '').lower() == 'true'

    # [디버깅] 터미널에서 어떤 값이 들어왔는지 확인해보세요.
    # print(f"DEBUG: building_name='{building_name}', floor='{floor_raw}'")

    now = timezone.now()
    now_time = now.time()
    # 요일 매핑 (장고 weekday는 월:0 ~ 일:6)
    days = ['월', '화', '수', '목', '금', '토', '일']
    now_weekday = days[now.weekday()]

    # 2. 기본 쿼리셋 (관 이름으로 필터링)
    # icontains를 사용하면 부분 일치도 검색되어 더 안전합니다 (예: "승연"만 쳐도 검색됨)
    rooms = Room.objects.filter(kwan_name__icontains=building_name)

    # 3. 층 필터링 (값이 있을 때만)
    if floor_raw:
        try:
            rooms = rooms.filter(floor=int(floor_raw))
        except ValueError:
            pass # 숫자가 아니면 무시

    # [디버깅] 쿼리 결과 개수 확인
    # print(f"DEBUG: 검색된 강의실 개수 = {rooms.count()}")

    # 4. 현재 진행 중인 수업 쿼리
    active_classes = Classes.objects.filter(
        Q(date1=now_weekday) | Q(date2=now_weekday),
        start__lte=now_time,
        end__gte=now_time
    )

    classroom_list = []
    for r in rooms:
        # 강의실 번호 매칭 시에도 공백 등을 고려해 필터링
        is_occupied = active_classes.filter(Q(room1=r.room) | Q(room2=r.room)).exists()
        is_available = not is_occupied

        if is_empty_only and not is_available:
            continue

        # 이미지 URL 처리 (절대 경로 권장)
        try:
            image_url = request.build_absolute_uri(r.room_image.url) if r.room_image else None
        except:
            image_url = None

        classroom_list.append({
            "id": str(r.id),
            "floor": r.floor,
            "classroom_number": r.room,
            "isAvaliable": is_available,
            "imageUrl": image_url
        })

    return JsonResponse({"classroom_list": classroom_list}, safe=False, json_dumps_params={'ensure_ascii': False})
# 2. 강의실 상세 정보 조회 (특정 강의실의 수업 리스트)
def get_classroom_detail(request, room_id):
    room_obj = get_object_or_404(Room, id=room_id)
    room_name = room_obj.room
    
    # 해당 강의실에서 열리는 모든 수업 조회
    classes = Classes.objects.filter(Q(room1=room_obj.room) | Q(room2=room_obj.room))
    
    course_list = []
    for c in classes:
        # 요일 배열 생성 (영문 Enum 대응)
        days_map = {'월': 'MON', '화': 'TUE', '수': 'WED', '목': 'THU', '금': 'FRI', '토': 'SAT', '일': 'SUN'}
        day_of_week = [days_map[c.date1]]
        if c.date2:
            day_of_week.append(days_map[c.date2])

        course_list.append({
            "id": c.code,
            "professor": c.prof,
            "course_name": c.class_name,
            "start_time": c.start.strftime('%H:%M') if c.start else None,
            "end_time": c.end.strftime('%H:%M') if c.end else None,
            "dayOfWeek": day_of_week,
            "room": room_name,
            # "degreeLevel": "UNDERGRATE" # 모델에 필드가 없으므로 기본값 설정
        })

    # 프론트 요구 양식에 맞춘 반환 (기자재 등은 모델에 없으므로 빈 값 또는 기본값)
    context = {
        "course_list": course_list,
        # "equipment": [
        #     {
        #         "pc": 0,
        #         "chair": 0,
        #         "projector": 1
        #     }
        # ],
        # "reservation_list": []
    }
    
    return JsonResponse(context, safe=False, json_dumps_params={'ensure_ascii': False})