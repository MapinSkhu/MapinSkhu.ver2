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
