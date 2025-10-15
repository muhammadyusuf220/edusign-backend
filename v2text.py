#V2TEXT.PY
import os
import time
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"
import whisper # Import library whisper
# Hapus speech_recognition karena tidak digunakan lagi
from yt_dlp import YoutubeDL
from pydub import AudioSegment

from pydub.utils import which
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

# # Pastikan path FFMPEG masih diatur
# os.environ["FFMPEG_PATH"] = r"C:\ffmpeg\bin\ffmpeg.exe"
# os.environ["FFPROBE_PATH"] = r"C:\ffmpeg\bin\ffprobe.exe"

def format_time(seconds):
    """Mengubah detik menjadi format SRT: HH:MM:SS,ms"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def convert_video_to_srt(video_url):
    print("Memulai proses...")

    # --- Langkah 1: Unduh Audio ---
    print(f"Mengunduh audio dari: {video_url}")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloaded_audio.%(ext)s',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'ffmpeg_location': r"C:\ffmpeg\bin",
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        time.sleep(1)
        audio_filename_mp3 = "downloaded_audio.mp3"
        print(f"Audio berhasil diunduh: {audio_filename_mp3}")
    except Exception as e:
        print(f"Error saat mengunduh video: {e}")
        return

    # --- Langkah 2: Konversi ke WAV ---
    print("Mengonversi audio ke format WAV...")
    audio_filename_wav = "converted_audio.wav"
    try:
        AudioSegment.from_mp3(audio_filename_mp3).export(audio_filename_wav, format="wav")
        print(f"File WAV berhasil dibuat: {audio_filename_wav}")
    except Exception as e:
        print(f"Error saat konversi ke WAV: {e}")
        if os.path.exists(audio_filename_mp3): os.remove(audio_filename_mp3)
        return

    # --- Langkah 3: Transkripsi dengan Whisper untuk Mendapatkan Timestamps ---
    print("Memuat model Whisper (mungkin butuh waktu saat pertama kali)...")
    model = whisper.load_model("base") # "base" adalah model yg cukup cepat dan ringan
    
    print("Memulai transkripsi dengan Whisper...")
    result = model.transcribe(audio_filename_wav, fp16=False) # fp16=False untuk kompatibilitas CPU
    
    # --- Langkah 4: Membuat File SRT ---
    output_srt_filename = "subtitle.srt"
    with open(output_srt_filename, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(result["segments"]):
            start_time = format_time(segment["start"])
            end_time = format_time(segment["end"])
            text = segment["text"].strip()
            
            srt_file.write(f"{i + 1}\n")
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{text}\n\n")

    print("\n--- Proses Selesai ---")
    print(f"File subtitle berhasil dibuat: {output_srt_filename}")

    # --- Langkah 5: Membersihkan file sementara ---
    print("Membersihkan file sementara...")
    if os.path.exists(audio_filename_mp3): os.remove(audio_filename_mp3)
    if os.path.exists(audio_filename_wav): os.remove(audio_filename_wav)
    print("Selesai.")
    return output_srt_filename   # ⬅️ return nama file subtitle


