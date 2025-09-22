import base64
import os
import subprocess
from pathlib import Path

import pyttsx3
import requests

default_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}


def get_valid_audio(word: str, return_bytes=False, need_ffmpeg_recode=True) -> str | bytes | None:
    audio_byte_data = None

    try:
        url = f"http://dict.youdao.com/dictvoice?type=0&audio={word}"
        res = requests.get(url, headers=default_headers)
        res.raise_for_status()
        audio_byte_data = res.content
    except Exception as e:
        print(f"从有道获取音频失败: {e}")

    if audio_byte_data is None:
        try:
            url = f"https://dict-co.iciba.com/api/dictionary.php?key=AA6C7429C3884C9E766C51187BD1D86F&type=json&w={word}"
            res = requests.get(url, headers=default_headers)
            res.raise_for_status()
            data = res.json()

            audio_url = ""
            if au := data["symbols"][0]["ph_am_mp3"]:
                audio_url = au
            elif au := data["symbols"][0]["ph_tts_mp3"]:
                audio_url = au

            if audio_url:
                res = requests.get(audio_url, headers=default_headers)
                res.raise_for_status()
                audio_byte_data = res.content
            else:
                print(f"金山词霸没有找到音频: {word}")
        except Exception as e:
            print(f"从金山词霸获取音频失败: {e}")

    # If both APIs fail, use pyttsx3 to generate audio
    if audio_byte_data is None:
        try:
            temp_output_audio_file_path = os.path.join(str(Path.home() / "Downloads"), "temp_us.mp3")
            engine = pyttsx3.init()
            engine.save_to_file(word, temp_output_audio_file_path)
            engine.runAndWait()
            engine.stop()
            with open(temp_output_audio_file_path, "rb") as f:
                audio_byte_data = f.read()
            os.remove(temp_output_audio_file_path)
        except Exception as e:
            print(f"使用 pyttsx3 生成音频失败: {e}")

    if need_ffmpeg_recode:
        command = "ffmpeg -hide_banner -i - -f mp3 -"
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(input=audio_byte_data)
        if process.returncode != 0:
            print(f"ffmpeg转码失败: {stderr.decode('utf-8')}")
        else:
            audio_byte_data = stdout

    if audio_byte_data:
        if return_bytes:
            return audio_byte_data
        else:
            return base64.b64encode(audio_byte_data).decode("utf-8")
    else:
        return None


def download_us_voice(word):
    word = word.strip().lower()
    audio_byte_data = get_valid_audio(word, return_bytes=True)
    if audio_byte_data and isinstance(audio_byte_data, bytes):
        with open(os.path.join(str(Path.home() / "Downloads"), f"{word}_us.mp3"), "wb") as f:
            f.write(audio_byte_data)
    else:
        print(f"Api上没有找到 {word} 的音频数据...")


if __name__ == "__main__":
    while True:
        word = input("输入单词：").strip()
        if not word:
            continue
        download_us_voice(word)
