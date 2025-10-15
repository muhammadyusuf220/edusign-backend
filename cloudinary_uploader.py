# cloudinary_uploader.py
import cloudinary
import cloudinary.uploader
import os

# --- 🔧 Konfigurasi Cloudinary ---
cloudinary.config(
    cloud_name="dwzyymvce",   # ganti dengan milikmu
    api_key="278265395675589",
    api_secret="id2wRGY0jd2sOAst6jfIipMHJgs",
    secure=True
)

def upload_to_cloudinary(file_path, file_type, video_id, folder="EduSign"):
    """
    Mengunggah file ke Cloudinary dengan nama sesuai tipe (subtitle / signLanguage)
    dan ID video dari Firestore.
    
    file_type: "subtitle" atau "signLanguage"
    video_id: ID dokumen video di Firestore
    """
    try:
        # Tentukan nama file di Cloudinary
        file_name = f"{file_type}_{video_id}"
        print(f"☁️ Mengunggah {file_name} ke Cloudinary...")

        upload_result = cloudinary.uploader.upload(
            file_path,
            folder=folder,
            public_id=file_name,        # nama file di Cloudinary
            overwrite=True,             # kalau ada file dengan nama sama, timpa
            resource_type="auto"        # auto: bisa image, video, audio, dll
        )

        public_url = upload_result.get("secure_url")
        print(f"✅ Berhasil diunggah ke Cloudinary: {public_url}")
        return public_url

    except Exception as e:
        print(f"⛔ Gagal mengunggah ke Cloudinary: {e}")
        return None
