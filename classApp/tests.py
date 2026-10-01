from django.test import TestCase

from .models import Room


class RoomDisplayNameTests(TestCase):
    def test_named_halls_include_name_after_room_number(self):
        room_9101 = Room(room='9101')
        room_9301 = Room(room='9301')

        self.assertEqual(room_9101.display_name, '9101(피츠버그홀)')
        self.assertEqual(room_9301.display_name, '9301(성미가엘성당)')

    def test_other_rooms_keep_room_number_only(self):
        room = Room(room='7207')

        self.assertEqual(room.display_name, '7207')


class ProfessorRoomDisplayTests(TestCase):
    def test_seungyeon_professor_room_is_replaced_by_floor_description(self):
        Room.objects.create(
            kwan_name='승연관', room='1399', details='교수연구실', floor=3
        )

        response = self.client.get('/sy_gwan/')

        self.assertContains(response, '교수연구실이 있습니다.')
        self.assertNotContains(response, 'data-room="1399"')

    def test_ilman_professor_room_is_replaced_by_floor_description(self):
        Room.objects.create(
            kwan_name='일만관', room='2A299', details='교수연구실', floor=2
        )

        response = self.client.get('/im_gwan/')

        self.assertContains(response, '교수연구실이 있습니다.')
        self.assertNotContains(response, 'data-room="2A299"')


class StaticRoomImageTests(TestCase):
    def test_detail_does_not_fall_back_to_media_image(self):
        room = Room.objects.create(
            kwan_name='나눔관',
            room='5C298',
            details='',
            floor=2,
            room_image='images/room/media-only.jpg',
        )

        response = self.client.get(f'/classroom/{room.id}/')

        self.assertContains(response, 'images/classroom/imagewait.webp')
        self.assertNotContains(response, 'images/room/media-only.jpg')

    def test_static_image_lookup_prefers_webp(self):
        room = Room.objects.create(
            kwan_name='승연관', room='1201', details='', floor=2
        )

        response = self.client.get(f'/classroom/{room.id}/')

        self.assertContains(response, 'images/classroom/1201.webp')
        self.assertNotContains(response, 'images/classroom/1201.jpg')
