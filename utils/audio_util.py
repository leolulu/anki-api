import base64

import requests


def get_valid_audio(word: str) -> str | None:
    audio_byte_data = None

    try:
        url = f"http://dict.youdao.com/dictvoice?type=0&audio={word}"
        res = requests.get(url)
        res.raise_for_status()
        audio_byte_data = res.content
    except Exception as e:
        print(f"从有道获取音频失败: {e}")

    try:
        url = f"https://dict-co.iciba.com/api/dictionary.php?key=AA6C7429C3884C9E766C51187BD1D86F&type=json&w={word}"
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()

        audio_url = ""
        if au := data["symbols"][0]["ph_am_mp3"]:
            audio_url = au
        elif au := data["symbols"][0]["ph_tts_mp3"]:
            audio_url = au

        if audio_url:
            res = requests.get(audio_url)
            res.raise_for_status()
            audio_byte_data = res.content
        else:
            print(f"金山词霸没有找到音频: {word}")
    except Exception as e:
        print(f"从金山词霸获取音频失败: {e}")

    if audio_byte_data:
        return base64.b64encode(audio_byte_data).decode("utf-8")
    else:
        return None

if __name__ == "__main__":
    word = "stub files"
    audio_data = get_valid_audio(word)
    print(audio_data)