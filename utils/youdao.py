import requests
import re


def get_phonetic_by_youdao(word):
    url = "https://www.youdao.com/result?word={word}&lang=en"
    res = requests.get(url.format(word=word))
    for i in re.findall(f"per-phone.*?点击发音", res.text):
        if "美" in i:
            print(i)
            for i in re.findall(r"phonetic.*?span", i):
                for i in re.findall(r"/(.*?)/", i):
                    return i.strip()
    return "空"
