from django.test import TestCase

from classApp.models import Room


class RoomSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.room = Room.objects.create(
            kwan_name="새천년관",
            room="B7999",
            details="식당",
            floor=1,
            room_image="images/room/imagewait.png",
        )

    def test_searches_room_number(self):
        response = self.client.get("/search/", {"q": self.room.room})

        self.assertContains(response, self.room.room)

    def test_searches_room_details(self):
        response = self.client.get("/search/", {"q": "식당"})

        self.assertContains(response, self.room.room)
        self.assertContains(response, self.room.details)
        self.assertContains(response, "lectureinfo-box--non-classroom")
        self.assertContains(response, "images/classroom/nonimage.webp")
        self.assertContains(response, f"새천년관 · {self.room.room}")
        self.assertContains(response, "search-room-location")
        self.assertNotContains(
            response,
            f'href="/classroom/{self.room.id}/"',
        )

    def test_classroom_without_any_scheduled_classes_is_unopened(self):
        unopened_room = Room.objects.create(
            kwan_name="나눔관",
            room="5C299",
            details="",
            floor=2,
        )

        response = self.client.get("/search/", {"q": unopened_room.room})

        self.assertContains(response, "미개방")
        self.assertContains(response, 'class="lecturecon unopened"')
        self.assertNotContains(response, 'class="lecturecon imposs"')
        self.assertNotContains(response, "사용가능")

    def test_room_hidden_on_building_page_is_not_searchable(self):
        hidden_room = Room.objects.create(
            kwan_name="월당관",
            room="3102",
            details="정보인프라팀 창고",
            floor=1,
        )

        response = self.client.get("/search/", {"q": hidden_room.room})

        self.assertNotContains(response, hidden_room.details)
        self.assertContains(response, "강의실 검색 결과가 없습니다.")

    def test_professor_rooms_are_replaced_by_floor_descriptions_in_search(self):
        Room.objects.create(
            kwan_name="승연관",
            room="1399",
            details="교수연구실",
            floor=3,
        )

        response = self.client.get("/search/", {"q": "교수연구실"})

        self.assertNotContains(response, "1399")
        self.assertContains(response, "승연관 F3")
        self.assertContains(response, "교수연구실이 있습니다.")

    def test_hidden_room_represented_by_floor_label_uses_label_in_search(self):
        Room.objects.create(
            kwan_name="나눔관",
            room="5C199",
            details="동아리연합회",
            floor=1,
        )

        response = self.client.get("/search/", {"q": "동아리연합회"})

        self.assertNotContains(response, "5C199")
        self.assertContains(response, "나눔관 F1")
        self.assertContains(response, "동아리연합회")

    def test_pittsburgh_hall_search_location_uses_wide_label(self):
        room = Room.objects.create(
            kwan_name="성미가엘성당&피츠버그홀",
            room="9299",
            details="교목사무실",
            floor=2,
        )

        response = self.client.get("/search/", {"q": room.room})

        self.assertContains(response, "search-room-location--wide")

    def test_search_does_not_fall_back_to_media_image(self):
        room = Room.objects.create(
            kwan_name="나눔관",
            room="5C298",
            details="",
            floor=2,
            room_image="images/room/media-only.jpg",
        )

        response = self.client.get("/search/", {"q": room.room})

        self.assertContains(response, "images/classroom/imagewait.webp")
        self.assertNotContains(response, "images/room/media-only.jpg")

    def test_index_does_not_copy_static_images_to_media(self):
        room = Room.objects.create(
            kwan_name="승연관",
            room="1201",
            details="",
            floor=2,
        )

        self.client.get("/")

        room.refresh_from_db()
        self.assertFalse(room.room_image.name)

    def test_search_prefers_webp_when_optimized_copy_exists(self):
        room = Room.objects.create(
            kwan_name="승연관",
            room="1201",
            details="",
            floor=2,
        )

        response = self.client.get("/search/", {"q": room.room})

        self.assertContains(response, "images/classroom/1201.webp")
        self.assertNotContains(response, "images/classroom/1201.jpg")
