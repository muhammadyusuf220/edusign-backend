from flask import Flask, jsonify
from firebase_admin import firestore, credentials, initialize_app
from v2text import convert_video_to_srt
from ai_model import generate_sign_language_video
from cloudinary_uploader import upload_to_cloudinary
import os

# --- 🔧 Inisialisasi Firebase ---
cred = credentials.Certificate("edusign-433e2-firebase-adminsdk-fbsvc-e5d7bb91aa.json")
initialize_app(cred)
db = firestore.client()

# --- 🔧 Inisialisasi Flask ---
app = Flask(__name__)

def get_text_from_srt(srt_path):
    """
    Membaca file .srt dan menggabungkan hanya teks subtitle (tanpa nomor & timestamp)
    menjadi satu string yang bersih untuk diterjemahkan ke bahasa isyarat.
    """
    try:
        full_text = []
        with open(srt_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Abaikan baris kosong, nomor urut, dan timestamp
                if not line or line.isdigit() or '-->' in line:
                    continue
                # Hanya ambil teks subtitle
                full_text.append(line)
        
        # Gabungkan teks antar segmen jadi satu kalimat panjang
        clean_text = " ".join(full_text)
        return clean_text

    except Exception as e:
        print(f"Error membaca file SRT: {e}")
        return None

# --- 🔥 Endpoint utama ---
@app.route('/process/<video_id>', methods=['GET'])
def process_video(video_id):
    """
    Endpoint: http://localhost:5000/process/<video_id>
    Akan memproses video berdasarkan ID Firestore.
    """
    print(f"\n🚀 Memproses video ID: {video_id}")

    try:
        # Ambil dokumen video dari Firestore
        doc_ref = db.collection("videos").document(video_id)
        doc = doc_ref.get()

        if not doc.exists:
            return jsonify({"status": "error", "message": f"Video dengan ID '{video_id}' tidak ditemukan."}), 404

        video_data = doc.to_dict()
        youtube_url = video_data.get("link")

        if not youtube_url:
            return jsonify({"status": "error", "message": "Kolom 'link' kosong di Firestore."}), 400

        # Langkah 1: Buat subtitle dari video YouTube
        print("   1️⃣ Membuat subtitle dari video...")
        local_srt_path = convert_video_to_srt(youtube_url)
        if not local_srt_path:
            return jsonify({"status": "error", "message": "Gagal membuat subtitle."}), 500

        # Langkah 2: Ekstrak teks dari SRT
        print("   2️⃣ Mengekstrak teks dari subtitle...")
        full_text = get_text_from_srt(local_srt_path)
        if not full_text:
            return jsonify({"status": "error", "message": "Gagal mengekstrak teks dari SRT."}), 500

        # # Langkah 3: Buat video bahasa isyarat dari teks
        print("   3️⃣ Membuat video bahasa isyarat...")
        local_sign_video_path = generate_sign_language_video(full_text)
        if not local_sign_video_path:
            return jsonify({"status": "error", "message": "Gagal membuat video bahasa isyarat."}), 500

        # --- Jika ingin unggah ke Drive, aktifkan ini ---
        subtitle_cloud_url = upload_to_cloudinary(local_srt_path, "sub", video_id)
        sign_language_cloud_url = upload_to_cloudinary(local_sign_video_path, "signLanguage", video_id)

        # Langkah 4: Update Firestore
        print("   4️⃣ Memperbarui dokumen di Firestore...")
        doc_ref.update({
            "Status": True,
            "subtitle": subtitle_cloud_url,
            "signLanguage": sign_language_cloud_url
        })

        print("✅ Selesai memproses video.")
        return jsonify({
            "status": "success",
            "message": f"Video {video_id} berhasil diproses.",
            "subtitle_path": local_srt_path,
            "sign_language_video": local_sign_video_path
        }), 200

    except Exception as e:
        print(f"⛔ Terjadi error saat memproses video {video_id}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# --- Jalankan server Flask ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
