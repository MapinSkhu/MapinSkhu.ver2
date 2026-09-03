from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator


class Classes(models.Model):
    kind = models.CharField(max_length=50) # 교필/전선/전필 등
    code = models.CharField(max_length=50) # 과목코드
    class_name = models.CharField(max_length=300, db_index=True) # 강의명
    prof = models.CharField(max_length=100, db_index=True) # 교수명

    room1 = models.CharField(max_length=100, blank=False, db_index=True) # 첫째강의실
    room2 = models.CharField(max_length=100, blank=True, db_index=True) # 둘째강의실

    date1 = models.CharField(max_length=5, blank=False, db_index=True) # 첫째요일
    date2 = models.CharField(max_length=5, blank=True, default=None, db_index=True) # 둘째요일

    start = models.TimeField(max_length=10, null=True, db_index=True) # 시작시간
    end = models.TimeField(max_length=10, null=True, db_index=True) # 끝시간

# --> 이후 개발 
    # start2 = models.TimeField(max_length=10, null=True) # 둘째시작시간
    # end2 = models.TimeField(max_length=10, null=True) # 둘째끝시간

    kwan_name = models.CharField(max_length=50, null=True, db_index=True) # 강의관명

    def __str__(self):
        return f'{self.kind, self.code, self.class_name, self.prof, self.room1, self.room2, self.date1, self.date2, self.start, self.end, self.kwan_name}'

class Kwan(models.Model):
    kwan_num = models.CharField(max_length=10)
    kwan_name = models.CharField(max_length=50, db_index=True)

    def __str__(self):
        return f'{self.kwan_name}'

class Room(models.Model):
    # url에 사용할 pk 만들기는 자동 생성되는 Id로 사용
    
    kwan_name = models.CharField(max_length=50, db_index=True)
    room = models.CharField(max_length=100, db_index=True)
    details = models.CharField(max_length=500, blank=True)
    floor = models.SmallIntegerField(
        validators=[
            MinValueValidator(1), MaxValueValidator(10)
            ]
    ) 
    room_image = models.ImageField(upload_to='images/room', null=True, blank=True)
    room_type = models.CharField(max_length=100, null = True, blank=True)

    @property
    def display_name(self):
        room_names = {
            '9101': '피츠버그홀',
            '9301': '성미가엘성당',
        }
        name = room_names.get(self.room)
        return f'{self.room}({name})' if name else self.room

    def __str__(self):
        return f'{self.room, self.room_type}'
