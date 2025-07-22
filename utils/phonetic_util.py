import json
import re

import requests


def get_phonetic_by_youdao(word):
    url = f"https://www.youdao.com/result?word={word}&lang=en"
    res = requests.get(url.format(word=word))
    for i in re.findall("per-phone.*?点击发音", res.text):
        if "美" in i:
            for i in re.findall(r"phonetic.*?span", i):
                for i in re.findall(r"/(.*?)/", i):
                    return i.strip()
    return None


def get_phonetic_by_bing(word):
    url = f"https://cn.bing.com/dict/search?q={word}"
    res = requests.get(url.format(word=word))
    for i in re.findall(r"美.*?\[(.*?)\]", res.text):
        return i.strip()
    return None


def get_phonetic_by_baidu(word):
    url = "https://fanyi.baidu.com/ait/text/translate"
    payload = {"query": word, "from": "en", "to": "zh"}
    headers = {
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Acs-Token": "1753120806306_1753151273798_LASUC8Befj2p6O2QLYNDCP14jRUhiyRLjvP/DNOKNw0n5eaQkLfl4qSqGxsdHXrB8caqikjHuj6Hiip4luK/cGTsgTcbgPfq1ymQl+ikTZD7b9mmwE0Q/edfHCu2OArdf8iwNDvly3olvvFV+weks0yjozsOjOA4hRF5R5ZyqUfFH09qzrqpCvjz6S4FzDQlKl8CwisSU3ESzt4kcGToLic1fnO+HOm4QMPkmml+yr8+cbh9v5AW2fpygvBfzSHSoJ+m/veUxYFa39lCuea7RtO0/UR9waUORP5K8EmUq+SfNfx2sQLLBg04zwyvGcSWeVS+NqN37E0cIKbRBKIt+zAjPku/DSPszs9dbNhI8j4PCY/kPKO/zeMfX3LaC73I/EhsdMYsFpqoL1xMaqIRY7zBdXg44kBuLoAcB3OCH2VR7bUY9mXR8OkhmgQhix3zdxs4oOiWX8+9T3LRjd021SuyrYIR+c1PG0OX6NnU400=",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Origin": "https://fanyi.baidu.com",
        "Referer": "https://fanyi.baidu.com/mtpe-individual/multimodal?aldtype=85",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "accept": "text/event-stream",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }
    cookies = {
        "BAIDUID": "45DEE27EDA34AE83FB6E97E5AE6C3275:FG=1",
        "BAIDUID_BFESS": "45DEE27EDA34AE83FB6E97E5AE6C3275:FG=1",
        "ab_sr": "1.0.1_MDkwZTgxM2M1ODhkNGFhNjI0MmQyYTk1YjhmYTdkMzdkM2ZmZjE1ZjJkNzA1YWEwMWEyNjBkNGQ4OGVkZTI2MTJkZjY4MjVhYWFlODE0NGRjZjQ1MjA2ZTYzYjMzMGEzNTRlZmNiNTY5ZjNlMzg0Y2YwYmQ2NDhkMjk4YWQ2NTRkZmRmMGUzOTU2OTM2ZDNkY2ZiY2NiN2U4Njc3NGY5Yg==",
        "RT": "z=1&dm=baidu.com&si=e13e6f24-4658-4d9e-b89a-59491feafff7&ss=mddwzk84&sl=1&tt=91s&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf",
    }
    with requests.post(url, json=payload, stream=True, headers=headers, cookies=cookies) as res:
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
                        except Exception as e:
                            print(f"获取和解析百度词典数据失败，返回结果：{json_data}, 错误: {e}")
    return None


def get_phonetic(word):
    def _format(result):
        return f"美[{result}]"

    if result := get_phonetic_by_baidu(word):
        print("通过百度翻译获取音标成功...")
        return _format(result)
    if result := get_phonetic_by_youdao(word):
        print("通过有道词典获取音标成功...")
        return _format(result)
    if result := get_phonetic_by_bing(word):
        print("通过必应词典获取音标成功...")
        return _format(result)

    return "空"
