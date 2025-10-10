# test_app.py
from flask import Flask, request, jsonify
from ai_model import generate_sign_language_video
import os

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process_text():
    data = request.get_json()
    input_text = data.get("input_text")

    if not input_text:
        return jsonify({"error": "input_text missing"}), 400

    print(f"[INFO] Memproses teks: {input_text}")

    # Jalankan model AI kamu
    output_path = generate_sign_language_video(
        input_text,
        folder_video="./video_kata"  # ubah sesuai folder kamu
    )

    if not output_path or not os.path.exists(output_path):
        return jsonify({"error": "Video gagal dibuat"}), 500

    print(f"[INFO] Video hasil tersimpan di: {output_path}")

    return jsonify({
        "status": "done",
        "result_path": os.path.abspath(output_path)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
