#ai_model.py
import os
from moviepy import VideoFileClip, concatenate_videoclips
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

factory = StemmerFactory()
stemmer = factory.create_stemmer()

def generate_sign_language_video(input_text, folder_video="video_kata"):
    """
    Fungsi untuk membuat video bahasa isyarat dari input kalimat.
    """
    awalan_list = ["me", "ke", "di", "ber", "ter", "pe"]
    kata_kunci = input_text.split()
    list_klip_video = []

    for kata in kata_kunci:
        kata_dasar = stemmer.stem(kata)
        awalan_ditemukan = None
        for awalan in awalan_list:
            if kata.startswith(awalan):
                awalan_ditemukan = awalan
                break

        # cek awalan
        if awalan_ditemukan:
            nama_file_awalan = f"Awalan-{awalan_ditemukan.capitalize()}.mp4"
            path_file_awalan = os.path.join(folder_video, nama_file_awalan)
            if os.path.exists(path_file_awalan):
                list_klip_video.append(VideoFileClip(path_file_awalan))

        # cek kata dasar
        nama_file_dasar = f"{kata_dasar.capitalize()}.mp4"
        path_file_dasar = os.path.join(folder_video, nama_file_dasar)
        if os.path.exists(path_file_dasar):
            list_klip_video.append(VideoFileClip(path_file_dasar))

    if list_klip_video:
        video_final = concatenate_videoclips(list_klip_video)
        output_path = os.path.abspath("hasil_terjemahan_sibi.mp4")
        video_final.write_videofile(output_path, codec="libx264", audio=False)

        # cleanup
        for klip in list_klip_video:
            klip.close()
        video_final.close()

        return output_path
    else:
        print("⚠️ Tidak ada klip video yang cocok dengan input.")
        return None
