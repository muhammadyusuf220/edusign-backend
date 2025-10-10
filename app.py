# app.py
from flask import Flask, request, jsonify
from firebase_admin import storage, firestore, credentials, initialize_app
import tempfile, os
from ai_model import generate_sign_language_video

# 🔧 Inisialisasi Firebase
cred = credentials.Certificate("edusign-433e2-firebase-adminsdk-fbsvc-e5d7bb91aa.json")
initialize_app(cred, {'storageBucket': 'edusign-433e2.appspot.com'})
db = firestore.client()
bucket = storage.bucket()

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process_text():
    data = request.get_json()
    input_text = data.get("input_text")

    if not input_text:
        return jsonify({"error": "input_text missing"}), 400

    # 🧠 Jalankan model AI
    output_path = generate_sign_language_video(input_text)

    if not output_path:
        return jsonify({"error": "Video not generated"}), 500

    # ☁️ Upload ke Firebase Storage
    blob = bucket.blob(f"results/{os.path.basename(output_path)}")
    blob.upload_from_filename(output_path)
    blob.make_public()
    result_url = blob.public_url

    # 🧾 Simpan hasil ke Firestore
    db.collection("translations").add({
        "input_text": input_text,
        "result_url": result_url,
        "status": "done"
    })

    return jsonify({"status": "done", "result_url": result_url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
