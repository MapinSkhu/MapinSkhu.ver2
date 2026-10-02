import math
from pathlib import Path

from PIL import Image, ImageChops, ImageOps, ImageStat, UnidentifiedImageError
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


SOURCE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
PLACEHOLDER_NAMES = {"imagewait", "nonimage"}
QUALITY_STEPS = (82, 86, 90)
MIN_PSNR = 32.0
MAX_LONG_EDGE = 2400


def calculate_psnr(reference, candidate):
    difference = ImageChops.difference(reference, candidate)
    statistics = ImageStat.Stat(difference)
    squared_error = sum(value ** 2 for value in statistics.rms) / len(
        statistics.rms
    )
    if squared_error == 0:
        return math.inf
    return 20 * math.log10(255.0 / math.sqrt(squared_error))


def prepare_reference(image):
    image = ImageOps.exif_transpose(image)
    has_alpha = image.mode in {"RGBA", "LA"} or (
        image.mode == "P" and "transparency" in image.info
    )
    prepared = image.convert("RGBA" if has_alpha else "RGB")
    prepared.thumbnail(
        (MAX_LONG_EDGE, MAX_LONG_EDGE),
        Image.Resampling.LANCZOS,
    )
    return prepared, has_alpha


def comparison_image(image):
    if image.mode == "RGBA":
        background = Image.new("RGBA", image.size, "white")
        background.alpha_composite(image)
        return background.convert("RGB")
    return image.convert("RGB")


class BaseOptimizer:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def optimize(self, source_path, write):
        target_path = self.output_dir / f"{source_path.stem}.webp"
        with Image.open(source_path) as source_image:
            reference, has_alpha = prepare_reference(source_image)

        reference_for_comparison = comparison_image(reference)
        is_lossless = has_alpha or source_path.stem in PLACEHOLDER_NAMES
        attempts = (None,) if is_lossless else QUALITY_STEPS
        accepted = None

        for quality in attempts:
            temporary_path = target_path.with_suffix(".webp.tmp")
            save_options = {
                "format": "WEBP",
                "method": 6,
                "lossless": is_lossless,
            }
            if quality is not None:
                save_options["quality"] = quality
            reference.save(temporary_path, **save_options)

            try:
                with Image.open(temporary_path) as optimized:
                    optimized.load()
                    decoded = comparison_image(optimized)
                    dimensions_match = optimized.size == reference.size
                    psnr = calculate_psnr(reference_for_comparison, decoded)
            except (OSError, UnidentifiedImageError):
                temporary_path.unlink(missing_ok=True)
                continue

            accepted = {
                "temporary_path": temporary_path,
                "target_path": target_path,
                "quality": "lossless" if quality is None else quality,
                "psnr": psnr,
                "width": reference.width,
                "height": reference.height,
                "dimensions_match": dimensions_match,
                "output_bytes": temporary_path.stat().st_size,
            }
            if dimensions_match and psnr >= MIN_PSNR:
                break
            temporary_path.unlink(missing_ok=True)
            accepted = None

        if accepted is None:
            return {"status": "quality_failed", "source": source_path}

        accepted["source"] = source_path
        accepted["source_bytes"] = source_path.stat().st_size
        if accepted["output_bytes"] >= accepted["source_bytes"]:
            accepted["temporary_path"].unlink(missing_ok=True)
            accepted["status"] = "not_smaller"
            return accepted

        if write:
            accepted["temporary_path"].replace(target_path)
            accepted["status"] = "written"
        else:
            accepted["temporary_path"].unlink(missing_ok=True)
            accepted["status"] = "dry_run"
        return accepted


class Command(BaseCommand):
    help = "원본을 보존하면서 호실 JPG/PNG의 검증된 WebP 사본을 생성한다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--write",
            action="store_true",
            help="검증을 통과한 WebP를 실제로 저장한다. 생략하면 미리보기만 한다.",
        )
        parser.add_argument(
            "--report",
            help="검사 결과를 기록할 Markdown 경로",
        )

    def handle(self, *args, **options):
        image_dir = (
            Path(settings.BASE_DIR) / "classApp/static/images/classroom"
        )
        if not image_dir.exists():
            raise CommandError(f"이미지 디렉터리를 찾을 수 없습니다: {image_dir}")

        optimizer = BaseOptimizer(image_dir)
        sources = sorted(
            path
            for path in image_dir.iterdir()
            if path.is_file() and path.suffix.lower() in SOURCE_EXTENSIONS
        )
        results = [optimizer.optimize(path, options["write"]) for path in sources]
        successful = [
            result
            for result in results
            if result["status"] in {"written", "dry_run"}
        ]
        skipped = [result for result in results if result["status"] == "not_smaller"]
        failed = [result for result in results if result["status"] == "quality_failed"]
        source_total = sum(result["source_bytes"] for result in successful)
        output_total = sum(result["output_bytes"] for result in successful)

        lines = [
            "# 호실 WebP 최적화 보고서",
            "",
            f"- 실행 모드: {'실제 생성' if options['write'] else '미리보기'}",
            f"- 변환 기준: 긴 변 최대 {MAX_LONG_EDGE}px, PSNR {MIN_PSNR:.0f}dB 이상",
            f"- 원본 파일 수: {len(sources)}",
            f"- 검증 통과: {len(successful)}",
            f"- 원본보다 커서 제외: {len(skipped)}",
            f"- 품질 검사 실패: {len(failed)}",
            f"- 통과 원본 합계: {source_total / 1_000_000:.2f} MB",
            f"- WebP 합계: {output_total / 1_000_000:.2f} MB",
            f"- 절감률: {(1 - output_total / source_total) * 100:.1f}%" if source_total else "- 절감률: -",
            "",
            "## 화질이 낮은 순서",
            "",
            "| 파일 | 크기 | 품질 | PSNR | 용량 전→후 |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
        for result in sorted(successful, key=lambda item: item["psnr"])[:20]:
            psnr = "∞" if math.isinf(result["psnr"]) else f"{result['psnr']:.2f}"
            lines.append(
                f"| `{result['source'].name}` | {result['width']}×{result['height']} | "
                f"{result['quality']} | {psnr} dB | "
                f"{result['source_bytes'] / 1_000_000:.2f}→{result['output_bytes'] / 1_000_000:.2f} MB |"
            )

        if skipped:
            lines.extend(["", "## 원본보다 커서 제외", ""])
            lines.extend(f"- `{result['source'].name}`" for result in skipped)
        if failed:
            lines.extend(["", "## 품질 검사 실패", ""])
            lines.extend(f"- `{result['source'].name}`" for result in failed)
        report = "\n".join(lines) + "\n"

        if options.get("report"):
            report_path = Path(options["report"])
            if not report_path.is_absolute():
                report_path = Path(settings.BASE_DIR) / report_path
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report, encoding="utf-8")
            self.stdout.write(f"보고서: {report_path}")
        self.stdout.write(report)

        if failed:
            raise CommandError(f"품질 검사를 통과하지 못한 이미지가 {len(failed)}개 있습니다.")
