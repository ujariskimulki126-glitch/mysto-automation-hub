
import re
import subprocess
from pathlib import Path

# MYSTO AI EDITOR
OUTPUT = Path("output")
VIDEO_DIR = OUTPUT / "videos"

INPUT_VIDEO = VIDEO_DIR / "mysto_episode.mp4"
OUTPUT_VIDEO = VIDEO_DIR / "mysto_final.mp4"
SUBTITLE_FILE = VIDEO_DIR / "mysto_subtitles.srt"


def get_narration():
    files = sorted(OUTPUT.glob("episode_*.md"))

    if not files:
        raise FileNotFoundError("Naskah tidak ditemukan!")

    text = files[-1].read_text(encoding="utf-8")

    match = re.search(
        r"NARASI\s*:?\s*(.*?)(?=\nVISUAL SCENE|\nCAPTION|\Z)",
        text,
        re.S | re.I
    )

    if not match:
        raise ValueError("Bagian NARASI tidak ditemukan!")

    return match.group(1).strip()


def get_duration():
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(INPUT_VIDEO)
        ],
        capture_output=True,
        text=True,
        check=True
    )

    return float(result.stdout.strip())


def timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)

    return (
        f"{hours:02}:"
        f"{minutes:02}:"
        f"{secs:02},"
        f"{millis:03}"
    )


def create_subtitles(narration, duration):
    words = narration.split()

    if not words:
        raise ValueError("Narasi kosong!")

    # Maksimal enam kata per subtitle
    chunks = [
        words[i:i + 6]
        for i in range(0, len(words), 6)
    ]

    # Distribusi waktu berdasarkan jumlah kata
    total_words = len(words)
    elapsed = 0
    subtitles = []

    for index, chunk in enumerate(chunks, start=1):
        start = elapsed
        segment_duration = (
            duration * len(chunk) / total_words
        )
        end = start + segment_duration
        elapsed = end

        text = " ".join(chunk)

        subtitles.append(
            f"{index}\n"
            f"{timestamp(start)} --> {timestamp(end)}\n"
            f"{text}\n"
        )

    SUBTITLE_FILE.write_text(
        "\n".join(subtitles),
        encoding="utf-8"
    )

    print("Subtitle berhasil dibuat!")


def burn_subtitles():
    if not INPUT_VIDEO.exists():
        raise FileNotFoundError(
            "Video mysto_episode.mp4 belum tersedia!"
        )

    subtitle_path = str(
        SUBTITLE_FILE.resolve()
    ).replace("\\", "/")

    # Escape karakter khusus untuk filter FFmpeg
    subtitle_path = (
        subtitle_path
        .replace(":", r"\:")
        .replace("'", r"\'")
        .replace(",", r"\,")
        .replace("[", r"\[")
        .replace("]", r"\]")
    )

    video_filter = (
        f"subtitles=filename='{subtitle_path}':"
        "force_style='FontName=DejaVu Sans,"
        "FontSize=22,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "BorderStyle=1,"
        "Outline=3,"
        "Shadow=1,"
        "Alignment=2,"
        "MarginV=250'"
    )

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(INPUT_VIDEO),
            "-vf", video_filter,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-c:a", "copy",
            "-movflags", "+faststart",
            str(OUTPUT_VIDEO)
        ],
        check=True
    )

    print("MYSTO VIDEO EDITING SELESAI!")
    print(f"Final video: {OUTPUT_VIDEO}")


def main():
    narration = get_narration()
    duration = get_duration()

    create_subtitles(narration, duration)
    burn_subtitles()


if __name__ == "__main__":
    main()
