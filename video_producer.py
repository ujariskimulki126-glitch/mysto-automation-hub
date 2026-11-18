
import asyncio
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import edge_tts

# MYSTO VIDEO SETTINGS
WIDTH = 1080
HEIGHT = 1920
FPS = 30
VOICE = "id-ID-ArdiNeural"

OUTPUT = Path("output")
VIDEO_DIR = OUTPUT / "videos"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)


def read_script():
    files = sorted(OUTPUT.glob("episode_*.md"))

    if not files:
        raise FileNotFoundError(
            "Naskah episode belum ditemukan di folder output."
        )

    return files[-1].read_text(encoding="utf-8")


def get_section(text, label, next_label=None):
    pattern = rf"{re.escape(label)}\s*:?\s*(.*?)(?=\n[A-Z][A-Z0-9 _]*\s*:|\Z)"
    match = re.search(pattern, text, re.S | re.I)

    return match.group(1).strip() if match else ""


def load_font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
    ]

    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


def create_scene(text, title, index):
    image = Image.new("RGB", (WIDTH, HEIGHT), (12, 19, 29))
    draw = ImageDraw.Draw(image)

    # Background decoration
    for y in range(0, HEIGHT, 100):
        draw.line((0, y, WIDTH, y), fill=(20, 34, 48), width=2)

    draw.ellipse(
        (300, 350, 780, 830),
        outline=(75, 105, 120),
        width=5
    )

    title_font = load_font(58)
    body_font = load_font(43)
    small_font = load_font(30)

    draw.text(
        (75, 100),
        "MYSTO",
        font=title_font,
        fill=(255, 255, 255)
    )

    draw.text(
        (75, 220),
        f"EPISODE SCENE {index}",
        font=small_font,
        fill=(110, 190, 205)
    )

    draw.line((75, 310, 1005, 310), fill=(80, 120, 140), width=3)

    # Wrap scene text
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = (current + " " + word).strip()

        if draw.textbbox((0, 0), test, font=body_font)[2] > 900:
            lines.append(current)
            current = word
        else:
            current = test

    if current:
        lines.append(current)

    y = 950

    for line in lines[:8]:
        draw.text(
            (75, y),
            line,
            font=body_font,
            fill=(235, 240, 245)
        )
        y += 75

    draw.text(
        (75, 1750),
        "MYSTO AI STUDIO",
        font=small_font,
        fill=(110, 190, 205)
    )

    path = VIDEO_DIR / f"scene_{index}.png"
    image.save(path)
    return path


async def create_voice(narration, path):
    communicator = edge_tts.Communicate(
        narration,
        VOICE
    )
    await communicator.save(str(path))


def make_video(images, audio_path, output_path):
    probe = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path)
        ],
        capture_output=True,
        text=True,
        check=True
    )

    duration = float(probe.stdout.strip())
    scene_duration = duration / len(images)

    clips = []

    for i, image in enumerate(images):
        clip = VIDEO_DIR / f"clip_{i}.mp4"
        clips.append(clip)

        subprocess.run([
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(image),
            "-t", str(scene_duration),
            "-vf",
            f"scale={WIDTH}:{HEIGHT},"
            "zoompan=z='min(zoom+0.0005,1.08)':"
            "d=1:s=1080x1920:fps=30",
            "-r", str(FPS),
            "-pix_fmt", "yuv420p",
            "-c:v", "libx264",
            str(clip)
        ], check=True)

    concat_file = VIDEO_DIR / "clips.txt"

    concat_file.write_text(
        "".join(f"file '{clip.name}'\n" for clip in clips),
        encoding="utf-8"
    )

    silent_video = VIDEO_DIR / "silent.mp4"

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(silent_video)
    ], check=True)

    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(silent_video),
        "-i", str(audio_path),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        "-movflags", "+faststart",
        str(output_path)
    ], check=True)


def main():
    script = read_script()

    title = get_section(script, "JUDUL")
    narration = get_section(script, "NARASI")

    scenes = re.findall(
        r"VISUAL SCENE \d+\s*:?\s*(.*?)(?=\nVISUAL SCENE \d+\s*:|\n[A-Z][A-Z0-9 _]*\s*:|\Z)",
        script,
        re.S | re.I
    )

    if not narration or not scenes:
        raise ValueError(
            "Format naskah tidak lengkap. Periksa bagian NARASI dan VISUAL SCENE."
        )

    audio_path = VIDEO_DIR / "narration.mp3"

    asyncio.run(create_voice(narration, audio_path))

    images = [
        create_scene(scene.strip(), title, i + 1)
        for i, scene in enumerate(scenes)
    ]

    output_path = VIDEO_DIR / "mysto_episode.mp4"

    make_video(images, audio_path, output_path)

    print("VIDEO MYSTO BERHASIL DIBUAT!")
    print(output_path)


if __name__ == "__main__":
    main()
