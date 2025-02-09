import json
import requests
import re


def get_phonetic_by_youdao(word):
    url = "https://www.youdao.com/result?word={word}&lang=en"
    res = requests.get(url.format(word=word))
    for i in re.findall(f"per-phone.*?点击发音", res.text):
        if "美" in i:
            for i in re.findall(r"phonetic.*?span", i):
                for i in re.findall(r"/(.*?)/", i):
                    return i.strip()
    return None


def get_phonetic_by_bing(word):
    url = "https://cn.bing.com/dict/search?q={word}"
    res = requests.get(url.format(word=word))
    for i in re.findall(r"美.*?\[(.*?)\]", res.text):
        return i.strip()
    return None


def get_phonetic_by_baidu(word):
    url = "https://fanyi.baidu.com/ait/text/translate"
    payload = {"query": word, "from": "en", "to": "zh"}
    with requests.post(url, json=payload, stream=True) as res:
        if res.status_code == 200:
            for line in res.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    if decoded_line.startswith("data:"):
                        data = decoded_line[5:].strip()
                        try:
                            json_data = json.loads(data)
                            if json_data["data"]["message"] == "获取词典成功":
                                for symbol in json_data["data"]["dictResult"]["simple_means"]["symbols"]:
                                    return symbol["ph_am"]
                        except:
                            pass
    return None


def get_phonetic(word):
    def _format(result):
        return f"美[{result}]"

    if result := get_phonetic_by_baidu(word):
        print(f"通过百度翻译获取音标成功...")
        return _format(result)
    if result := get_phonetic_by_youdao(word):
        print(f"通过有道词典获取音标成功...")
        return _format(result)
    if result := get_phonetic_by_bing(word):
        print(f"通过必应词典获取音标成功...")
        return _format(result)

    return "空"
