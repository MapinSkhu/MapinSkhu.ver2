from collections import Counter
from hashlib import sha256
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage

from classApp.models import Room
from classApp.room_overrides import SHARED_IMAGE_ROOMS


# DB media와 원본 파일의 동일 여부를 비교하므로 서비스용 WebP보다 원본을 먼저 찾는다.
IMAGE_EXTENSIONS = ("jpg", "jpeg", "png", "webp", "avif")


def file_sha256(file_object):
    digest = sha256()
    for chunk in iter(lambda: file_object.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def is_placeholder_media(image_name):
    """실제 공간 사진이 아닌 기존 대기 이미지를 구분한다."""
    lowered_name = str(image_name or "").lower()
    return "imagewait" in lowered_name or "nonimage" in lowered_name


def find_static_image(room_number):
    """현재 화면 규칙과 같은 방식으로 호실의 정적 이미지를 찾는다."""
    normalized_room = str(room_number).strip().lower()
    image_key = SHARED_IMAGE_ROOMS.get(normalized_room, normalized_room)

    for extension in IMAGE_EXTENSIONS:
        relative_path = f"images/classroom/{image_key}.{extension}"
        found_path = finders.find(relative_path)
        if found_path:
            return relative_path, Path(found_path)
    return None, None


def inspect_room_image(room):
    static_relative_path, static_path = find_static_image(room.room)
    media_name = room.room_image.name if room.room_image else ""
    media_is_placeholder = is_placeholder_media(media_name)
    media_exists = bool(
        media_name
        and not media_is_placeholder
        and default_storage.exists(media_name)
    )
    static_hash = ""
    media_hash = ""
    media_bytes = 0
    if static_path:
        with static_path.open("rb") as static_file:
            static_hash = file_sha256(static_file)
    if media_exists:
        media_bytes = default_storage.size(media_name)
        with default_storage.open(media_name, "rb") as media_file:
            media_hash = file_sha256(media_file)

    has_static = static_path is not None
    if has_static and media_exists:
        category = "both"
    elif has_static:
        category = "static_only"
    elif media_exists:
        category = "media_only"
    else:
        category = "missing"

    comparison = "-"
    if category == "both":
        comparison = "identical" if static_hash == media_hash else "different"

    notes = []
    if media_name and media_is_placeholder:
        notes.append("media placeholder")
    elif media_name and not media_exists:
        notes.append("media file missing")

    if static_path:
        expected_name = f"{str(room.room).strip().lower()}{static_path.suffix.lower()}"
        if static_path.name != expected_name:
            notes.append(f"filename normalization: {static_path.name} -> {expected_name}")

    return {
        "building": room.kwan_name,
        "room": room.room,
        "category": category,
        "static": static_relative_path or "-",
        "media": media_name or "-",
        "static_bytes": static_path.stat().st_size if static_path else 0,
        "media_bytes": media_bytes,
        "comparison": comparison,
        "notes": "; ".join(notes) or "-",
    }


def render_markdown(rows):
    counts = Counter(row["category"] for row in rows)
    comparison_counts = Counter(
        row["comparison"] for row in rows if row["category"] == "both"
    )
    lines = [
        "# 호실 이미지 자동 점검 결과",
        "",
        "> 이 보고서는 읽기 전용 점검 결과다. 이미지 파일과 DB를 변경하지 않는다.",
        "",
        "## 요약",
        "",
        f"- 정적 이미지와 유효한 media 이미지가 모두 있음: {counts['both']}",
        f"  - 파일 내용이 완전히 동일함: {comparison_counts['identical']}",
        f"  - 파일 내용이 서로 다름: {comparison_counts['different']}",
        f"- 정적 이미지만 있음: {counts['static_only']}",
        f"- 유효한 media 이미지만 있음: {counts['media_only']}",
        f"- 둘 다 없음: {counts['missing']}",
        "",
        "## 정적 이미지 통합 전 우선 점검 대상",
        "",
        "`media_only`는 정적 폴더로 이전해야 할 후보이다. `both / identical`은 중복 파일이며, `both / different`는 어느 사진을 최종본으로 유지할지 육안으로 확인해야 한다.",
        "",
        "| 구분 | 해시 비교 | 관 | 호실 | 정적 이미지 | media 연결 | 용량 비교 | 비고 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    priority_rows = [
        row for row in rows if row["category"] in {"media_only", "both"}
    ]
    if priority_rows:
        for row in priority_rows:
            lines.append(
                f"| {row['category']} | {row['comparison']} | {row['building']} | {row['room']} | "
                f"`{row['static']}` | `{row['media']}` | "
                f"{row['static_bytes'] / 1_000_000:.2f} / {row['media_bytes'] / 1_000_000:.2f} MB | "
                f"{row['notes']} |"
            )
    else:
        lines.append("| - | - | - | - | - | - | - | 이전 또는 비교할 이미지 없음 |")

    lines.extend([
        "",
        "## 이미지가 없는 공간",
        "",
        "| 관 | 호실 | media 상태 | 비고 |",
        "| --- | --- | --- | --- |",
    ])
    missing_rows = [row for row in rows if row["category"] == "missing"]
    if missing_rows:
        for row in missing_rows:
            lines.append(
                "| {building} | {room} | `{media}` | {notes} |".format(**row)
            )
    else:
        lines.append("| - | - | - | 누락 이미지 없음 |")

    oversized_rows = [row for row in rows if row["static_bytes"] > 1_000_000]
    lines.extend([
        "",
        "## 로딩 최적화 후보",
        "",
        "정적 이미지가 1MB를 초과하는 공간이다. 해상도 조정 및 WebP/AVIF 변환을 우선 검토한다.",
        "",
        "| 관 | 호실 | 정적 이미지 | 크기 |",
        "| --- | --- | --- | ---: |",
    ])
    if oversized_rows:
        for row in sorted(oversized_rows, key=lambda item: item["static_bytes"], reverse=True):
            lines.append(
                f"| {row['building']} | {row['room']} | `{row['static']}` | "
                f"{row['static_bytes'] / 1_000_000:.2f} MB |"
            )
    else:
        lines.append("| - | - | - | 1MB 초과 이미지 없음 |")

    return "\n".join(lines) + "\n"


class Command(BaseCommand):
    help = "Room별 정적/media 이미지 연결 상태를 변경 없이 점검한다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            help="Markdown 보고서를 저장할 경로. 생략하면 표준 출력에 표시한다.",
        )

    def handle(self, *args, **options):
        rows = [
            inspect_room_image(room)
            for room in Room.objects.order_by("kwan_name", "floor", "room")
        ]
        report = render_markdown(rows)
        output_path = options.get("output")
        if output_path:
            path = Path(output_path)
            if not path.is_absolute():
                path = Path(settings.BASE_DIR) / path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(report, encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"점검 보고서 저장: {path}"))
        else:
            self.stdout.write(report)
