import os
import subprocess
import time
from multiprocessing import Process
from typing import Any, Dict

import psutil

from api.anki_api import Anki
from constants.env import ENV_VAR_ANKI_PATH, ENV_VAR_LOGSEQ_PATH, EXE_NAME_ANKI, EXE_NAME_LOGSEQ, PROGRAM_NAME_ANKI, PROGRAM_NAME_LOGSEQ
from utils.dict_util import BaiduFanyi
from utils.download_dictvoice import download_us_voice
from utils.env_var_util import read_user_environment_variable, set_user_environment_variable

DOWNLOAD_VOICE_PREFIX = ":"


def starter(env_var_name):
    program_names = {
        ENV_VAR_ANKI_PATH: PROGRAM_NAME_ANKI,
        ENV_VAR_LOGSEQ_PATH: PROGRAM_NAME_LOGSEQ,
    }
    exe_names = {
        ENV_VAR_ANKI_PATH: EXE_NAME_ANKI,
        ENV_VAR_LOGSEQ_PATH: EXE_NAME_LOGSEQ,
    }

    if exe_names[env_var_name] in [i.info["name"] for i in psutil.process_iter(["name"])]:
        print(f"{program_names[env_var_name]}在运行中，跳过启动过程...")
        return
    else:
        print(f"开始启动{program_names[env_var_name]}...")

    path = read_user_environment_variable(env_var_name)
    if not path:
        path = set_user_environment_variable(env_var_name, input(f"请输入{program_names[env_var_name]}可执行文件路径:").strip().strip('"'))

    kwargs: Dict[str, Any] = {"shell": True}
    if env_var_name == ENV_VAR_ANKI_PATH:
        cmd = ["start", "/b", path]
        anki_env = os.environ.copy()
        anki_env["http_proxy"] = "http://127.0.0.1:10809"
        anki_env["https_proxy"] = "http://127.0.0.1:10809"
        kwargs["env"] = anki_env
    else:
        cmd = [path]

    Process(target=subprocess.Popen, args=[cmd], kwargs=kwargs).start()


if __name__ == "__main__":
    BaiduFanyi.init_edge_browser()
    starter(ENV_VAR_LOGSEQ_PATH)
    starter(ENV_VAR_ANKI_PATH)

    while True:
        try:
            ak = Anki(port=18765)
            break
        except:
            time.sleep(5)

    while True:
        input_info = input(f'输入单词(输入"{DOWNLOAD_VOICE_PREFIX}"开头则只下载发音文件): ').strip().lower()
        if not input_info:
            continue
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
