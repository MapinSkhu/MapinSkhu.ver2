from django.test import TestCase

from classApp.models import Room


class RoomSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.room = Room.objects.create(
            kwan_name="새천년관",
            room="B7101",
            details="식당",
            floor=1,
            room_image="images/room/imagewait.png",
        )

    def test_searches_room_number(self):
        response = self.client.get("/search/", {"q": "B7101"})

        self.assertContains(response, self.room.room)

    def test_searches_room_details(self):
        response = self.client.get("/search/", {"q": "식당"})

        self.assertContains(response, self.room.room)
        self.assertContains(response, self.room.details)
        self.assertContains(response, "lectureinfo-box--non-classroom")
        self.assertContains(response, "images/classroom/nonImage.png")
        self.assertContains(response, "새천년관 · B7101")
        self.assertContains(response, "search-room-location")
        self.assertNotContains(
            response,
            f'href="/classroom/{self.room.id}/"',
        )
