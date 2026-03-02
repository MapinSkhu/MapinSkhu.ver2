import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from classApp.models import Room, Classes  # 본인의 앱 이름으로 확인
from django.db.models import Q
from django.utils import timezone

class Command(BaseCommand):
    help = '전체 강의실 목록 및 개별 상세 데이터를 JSON 파일로 생성합니다.'

    def handle(self, *args, **options):
        # 1. 기초 설정
        days_map = {'월': 'MON', '화': 'TUE', '수': 'WED', '목': 'THU', '금': 'FRI', '토': 'SAT', '일': 'SUN'}
        output_dir = os.path.join(settings.MEDIA_ROOT, 'static_json')
        detail_dir = os.path.join(output_dir, 'details') # 상세 데이터용 하위 폴더
        os.makedirs(detail_dir, exist_ok=True)

        # 2. 모든 강의실(Room) 가져오기
        all_rooms = Room.objects.all()

        # --- 과정 A: 개별 강의실 상세 정보(detail) 생성 ---
        self.stdout.write('강의실 상세 정보 생성 중...')
        for r in all_rooms:
            # 해당 강의실에서 열리는 모든 수업 조회
            classes = Classes.objects.filter(Q(room1=r.room) | Q(room2=r.room))
            
            course_list = []
            for c in classes:
                day_of_week = [days_map.get(c.date1, 'UNKNOWN')]
                if c.date2:
                    day_of_week.append(days_map.get(c.date2, 'UNKNOWN'))

                course_list.append({
                    "id": c.code,
                    "professor": c.prof,
                    "course_name": c.class_name,
                    "start_time": c.start.strftime('%H:%M') if c.start else None,
                    "end_time": c.end.strftime('%H:%M') if c.end else None,
                    "dayOfWeek": day_of_week,
                    "degreeLevel": "UNDERGRATE" 
                })

            detail_data = {
                "course_list": course_list,
                "equipment": [{"pc": 0, "chair": 0, "projector": 1}],
                "reservation_list": []
            }

            # 파일명은 고유 ID로 저장 (예: details/1.json)
            detail_file_path = os.path.join(detail_dir, f"{r.id}.json")
            with open(detail_file_path, 'w', encoding='utf-8') as f:
                json.dump(detail_data, f, ensure_ascii=False, indent=4)

        # --- 과정 B: 관별/층별 목록(list) 생성 (기존 로직 확장) ---
        self.stdout.write('관별 목록 생성 중...')
        buildings = Room.objects.values_list('kwan_name', flat=True).distinct()
        for b_name in buildings:
            floors = Room.objects.filter(kwan_name=b_name).values_list('floor', flat=True).distinct()
            for fl in floors:
                rooms_in_floor = Room.objects.filter(kwan_name=b_name, floor=fl)
                classroom_list = []
                for r in rooms_in_floor:
                    classroom_list.append({
                        "id": str(r.id),
                        "floor": r.floor,
                        "classroom_number": r.room,
                        "isAvaliable": True, # 정적 파일이므로 기본값 설정 (혹은 계산 로직 추가)
                        "imageUrl": f"/media/{r.room_image}" if r.room_image else None
                    })

                list_data = {"classroom_list": classroom_list}
                list_file_name = f"{b_name}_{fl}.json".replace(" ", "_")
                list_file_path = os.path.join(output_dir, list_file_name)

                with open(list_file_path, 'w', encoding='utf-8') as f:
                    json.dump(list_data, f, ensure_ascii=False, indent=4)

        self.stdout.write(self.style.SUCCESS('모든 정적 JSON 데이터 생성이 완료되었습니다.'))