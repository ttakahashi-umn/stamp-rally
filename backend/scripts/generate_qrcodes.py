from __future__ import annotations

import argparse
import csv
import hmac
import os
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path

import qrcode  # type: ignore[import-untyped]
from PIL import Image, ImageDraw, ImageFont  # type: ignore[import-untyped]


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV_PATH = REPO_ROOT / "data" / "facilities.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "qrcodes"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate signed venue QR code PNG files."
    )
    parser.add_argument(
        "--csv-path",
        type=Path,
        default=DEFAULT_CSV_PATH,
        help=f"Facilities CSV path (default: {DEFAULT_CSV_PATH})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for QR PNG files (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--days-valid",
        type=int,
        default=180,
        help="Validity period in days from now if --expires-at is omitted (default: 180)",
    )
    parser.add_argument(
        "--expires-at",
        type=str,
        default=None,
        help="Absolute expiration timestamp in ISO-8601 (example: 2026-12-31T23:59:59+09:00)",
    )
    return parser.parse_args()


def resolve_expiration(expires_at: str | None, days_valid: int) -> datetime:
    if expires_at:
        normalized = expires_at.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    return datetime.now(timezone.utc) + timedelta(days=days_valid)


def build_payload(secret: str, venue_code: str, expires_unix: int) -> str:
    body = f"{venue_code}:{expires_unix}"
    signature = hmac.new(secret.encode(), body.encode(), digestmod=sha256).hexdigest()
    return f"{body}:{signature}"


def build_qr_image(payload: str, venue_code: str) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    footer_height = 40
    canvas = Image.new(
        "RGB", (qr_image.width, qr_image.height + footer_height), color="white"
    )
    canvas.paste(qr_image, (0, 0))

    drawer = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    text = venue_code
    bbox = drawer.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (canvas.width - text_width) // 2
    y = qr_image.height + (footer_height - (bbox[3] - bbox[1])) // 2
    drawer.text((x, y), text, fill="black", font=font)
    return canvas


def iter_facilities(csv_path: Path) -> list[tuple[str, str]]:
    facilities: list[tuple[str, str]] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        valid_index = 0
        for row in reader:
            name = (row.get("施設名") or row.get("会場名") or "").strip()
            location = (row.get("住所") or "").strip()
            if not name or not location:
                continue
            valid_index += 1
            code = f"FAC-{valid_index:04d}"
            facilities.append((code, name))
    return facilities


def main() -> None:
    args = parse_args()
    if not args.csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {args.csv_path}")

    expires_at = resolve_expiration(args.expires_at, args.days_valid)
    expires_unix = int(expires_at.timestamp())
    secret = os.environ.get("STAMP_QR_SECRET", "stamp-rally-dev-secret")

    facilities = iter_facilities(args.csv_path)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = args.output_dir / "manifest.csv"
    with manifest_path.open("w", encoding="utf-8", newline="") as manifest_file:
        writer = csv.writer(manifest_file)
        writer.writerow(["code", "name", "expires_unix", "png_path"])
        for code, name in facilities:
            payload = build_payload(secret, code, expires_unix)
            image = build_qr_image(payload, code)
            output_path = args.output_dir / f"{code}.png"
            image.save(output_path, format="PNG")
            writer.writerow([code, name, str(expires_unix), str(output_path)])

    print(
        f"Generated {len(facilities)} QR files in {args.output_dir} "
        f"(expires_at_utc={expires_at.isoformat()})"
    )


if __name__ == "__main__":
    main()
