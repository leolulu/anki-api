import subprocess
import time
from threading import Thread

import psutil

from api.anki_api import Anki
from utils.download_dictvoice import download_us_voice
from utils.env_var_util import ANKI_PATH, LOGSEQ_PATH, read_user_environment_variable, set_user_environment_variable

DOWNLOAD_VOICE_PREFIX = ":"


def starter(env_var_name):
    program_names = {
        ANKI_PATH: "anki",
        LOGSEQ_PATH: "logseq",
    }
    exe_names = {
        ANKI_PATH: "anki.exe",
        LOGSEQ_PATH: "Logseq.exe",
    }

    if exe_names[env_var_name] in [i.info["name"] for i in psutil.process_iter(["name"])]:
        print(f"{exe_names[env_var_name]}在运行中，跳过启动过程...")
        return

    path = read_user_environment_variable(env_var_name)
    if not path:
        path = set_user_environment_variable(env_var_name, input(f"请输入{program_names[env_var_name]}可执行文件路径:").strip().strip('"'))
    Thread(target=lambda: subprocess.run([path])).start()


if __name__ == "__main__":
    starter(LOGSEQ_PATH)
    starter(ANKI_PATH)

    while True:
        try:
            ak = Anki(port=18765)
            break
        except:
            time.sleep(5)

    while True:
        input_info = input(f'输入单词(输入"{DOWNLOAD_VOICE_PREFIX}"开头则只下载发音文件): ').strip().lower()
        if input_info.startswith(DOWNLOAD_VOICE_PREFIX):
            voice_to_download = input_info[len(DOWNLOAD_VOICE_PREFIX) :]
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
