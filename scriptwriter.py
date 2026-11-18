
import os
from pathlib import Path
from datetime import datetime
from google import genai

# MYSTO AI CONFIGURATION
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY belum ditemukan!")

client = genai.Client(api_key=API_KEY)

# Daftar tema cerita
TOPICS = [
    "Misteri sejarah dunia",
    "Peradaban kuno yang hilang",
    "Misteri tempat terlarang",
    "Legenda dan mitos dunia",
    "Fakta sejarah yang mengejutkan",
    "Misteri laut dan samudra",
    "Kejadian aneh yang belum terpecahkan"
]

today = datetime.now().strftime("%Y-%m-%d")
topic_index = datetime.now().timetuple().tm_yday % len(TOPICS)
topic = TOPICS[topic_index]

# Instruksi untuk AI
prompt = f"""
Kamu adalah MYSTO AI, penulis cerita profesional
untuk TikTok dan YouTube Shorts.

Buat satu episode baru dengan tema: {topic}

ATURAN:
- Bahasa Indonesia.
- Durasi narasi 60 sampai 90 detik.
- Gaya dokumenter misteri sinematik.
- Pembukaan harus sangat menarik.
- Cerita memiliki alur yang kuat.
- Gunakan fakta yang bisa dipertanggungjawabkan.
- Bedakan fakta sejarah dengan legenda.
- Jangan mengarang fakta sebagai kebenaran.
- Akhiri dengan pertanyaan yang memancing komentar.

FORMAT OUTPUT:

JUDUL:
HOOK:
NARASI:
VISUAL SCENE 1:
VISUAL SCENE 2:
VISUAL SCENE 3:
VISUAL SCENE 4:
CAPTION:
HASHTAG:

Karakter utama:
MYSTO, kepala bulat putih, mata ekspresif,
tubuh stickman ramping, memakai jaket gelap.

Gaya visual:
Animasi stickman kartun sinematik,
pencahayaan dramatis, suasana misterius.
"""

# Memanggil Gemini AI
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt
)

result = response.text

if not result:
    raise RuntimeError("Gemini tidak menghasilkan naskah.")

# Menyimpan hasil episode
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

filename = output_dir / f"episode_{today}.md"

filename.write_text(
    result,
    encoding="utf-8"
)

print("MYSTO AI SCRIPTWRITER BERHASIL!")
print(f"Episode: {filename}")
print(result)
