from api.anki_api import Anki
from utils.download_dictvoice import download_us_voice

if __name__ == "__main__":
    download_voice_prefix = ":"
    ak = Anki(port=18765)
    while True:
        input_info = input(f'输入单词(输入"{download_voice_prefix}"开头则只下载发音文件): ').strip().lower()
        if input_info.startswith(download_voice_prefix):
            voice_to_download = input_info[len(download_voice_prefix) :]
            print(f'\n下载"{voice_to_download}"的发音文件...\n')
            download_us_voice(voice_to_download)
        else:
            retry_times = 10
            while retry_times > 0:
                try:
                    ak.add_card(input_info)
                    break
                except:
                    retry_times -= 1
