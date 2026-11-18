
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent

def run_step(name, script):
    print("\n" + "=" * 50)
    print(f"MYSTO ENGINE: {name}")
    print("=" * 50)

    result = subprocess.run(
        [sys.executable, str(ROOT / script)],
        cwd=ROOT
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Proses gagal pada: {name}"
        )

    print(f"{name} BERHASIL!")


def main():
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError(
            "GEMINI_API_KEY belum tersedia!"
        )

    print("MYSTO AI STUDIO STARTED")
    print(datetime.now().isoformat())

    # 1. Generate script
    run_step(
        "AI SCRIPTWRITER",
        "scriptwriter.py"
    )

    # 2. Produce video
    run_step(
        "AI VIDEO PRODUCTION",
        "video_producer.py"
    )

    # 3. Add subtitles
    run_step(
        "AI VIDEO EDITOR",
        "subtitle_editor.py"
    )

    final_video = (
        ROOT / "output" / "videos" /
        "mysto_final.mp4"
    )

    if not final_video.exists():
        raise FileNotFoundError(
            "Final video tidak ditemukan!"
        )

    print("\n" + "=" * 50)
    print("MYSTO AI PRODUCTION COMPLETED!")
    print(f"VIDEO: {final_video}")
    print("=" * 50)


if __name__ == "__main__":
    main()
