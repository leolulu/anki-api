import re

import requests
from playwright.sync_api import expect, sync_playwright


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
    url = f"https://fanyi.baidu.com/mtpe-individual/transText?lang=en2zh&query={word}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="load", timeout=120000)
            phonetic_locator = page.get_by_text("美/")
            expect(phonetic_locator).to_be_visible(timeout=5000)
            phonetic_content = phonetic_locator.text_content()
            if phonetic_content is None:
                return None
            else:
                phonetic_match = re.findall(r"美/(.*?)/", phonetic_content)
                if phonetic_match:
                    phonetic = phonetic_match[0]
                else:
                    phonetic = None
        except Exception as e:
            print(f"使用playwright进行百度音标获取失败:\n {e}")
            return None
        finally:
            browser.close()
    return phonetic


def get_phonetic(word):
    def _format(result):
        return f"美[{result}]"

    if result := get_phonetic_by_youdao(word):
        print("通过有道词典获取音标成功...")
        return _format(result)
    if result := get_phonetic_by_bing(word):
        print("通过必应词典获取音标成功...")
        return _format(result)
    if result := get_phonetic_by_baidu(word):
        print("通过百度翻译获取音标成功...")
        return _format(result)

    return "空"
