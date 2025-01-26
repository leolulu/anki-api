import requests
import re


def get_phonetic_by_youdao(word):
    url = "https://www.youdao.com/result?word={word}&lang=en"
    res = requests.get(url.format(word=word))
    for i in re.findall(f"per-phone.*?点击发音", res.text):
        if "美" in i:
            for i in re.findall(r"phonetic.*?span", i):
                for i in re.findall(r"/(.*?)/", i):
                    print("取到美音标：", i)
                    return i.strip()
    return None


def get_phonetic_by_bing(word):
    url = "https://cn.bing.com/dict/search?q={word}"
    res = requests.get(url.format(word=word))
    for i in re.findall(r"美.*?\[(.*?)\]", res.text):
        print("取到美音标：", i)
        return i.strip()
    return None


def get_phonetic(word):
    if result := get_phonetic_by_youdao(word):
        return result
    if result := get_phonetic_by_bing(word):
        return result
    return "空"
