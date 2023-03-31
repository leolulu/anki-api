import os
from pathlib import Path
import requests


while True:
    word = input("输入单词：").strip()
    # r = requests.get(f"http://dict.youdao.com/dictvoice?type=1&audio={word}")
    # with open(f"{word}_uk.mp3", 'wb') as f:
    #     f.write(r.content)
    r = requests.get(f"http://dict.youdao.com/dictvoice?type=0&audio={word}")
    with open(os.path.join(str(Path.home() / "Downloads"), f"{word}_us.mp3"), 'wb') as f:
        f.write(r.content)
