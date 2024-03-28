import time
import traceback

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException,NoSuchElementException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.webdriver import WebDriver as EdgeWebDriver

from utils.load_driver import get_edge_driver


class BaiduFanyi:
    EDGE_BROWSER: EdgeWebDriver
    URL = 'https://fanyi.baidu.com/#en/zh/{word}'

    def __init__(self, word) -> None:
        if not hasattr(BaiduFanyi, "EDGE_BROWSER"):
            edge_options = Options()
            edge_options.add_argument('--headless')
            edge_options.add_argument('--disable-gpu')
            edge_browser = webdriver.Edge(
                service=Service(get_edge_driver()),
                options=edge_options
            )
            BaiduFanyi.EDGE_BROWSER = edge_browser
        self.edge_browser = BaiduFanyi.EDGE_BROWSER
        self.goto_legacy_version()
        self.if_definitions_found = False
        self._get_phonetic(word)
        if self.if_definitions_found:
            self._get_definition()

    def goto_legacy_version(self):
        self.edge_browser.get(BaiduFanyi.URL.format(word="apple"))
        xpath_legacy_changer = r"//span[text()='返回旧版']"
        try:
            self.edge_browser.find_element("xpath", xpath_legacy_changer)
        except NoSuchElementException:
            return
        try:
            self.edge_browser.find_element("xpath", xpath_legacy_changer).click()
        except ElementClickInterceptedException:
            self.edge_browser.refresh()
            self.edge_browser.find_element("xpath", xpath_legacy_changer).click()
            self.edge_browser.refresh()

    def close(self):
        if hasattr(BaiduFanyi, 'EDGE_BROWSER'):
            BaiduFanyi.EDGE_BROWSER.close()

    def _get_definition(self):
        definitions = [i.text for i in self.edge_browser.find_elements('xpath', r"//div[@class='dictionary-comment']/*")]
        definitions = [i.strip().replace('\n', ' ').replace(';', '，') for i in definitions]
        self.definitions = "\n".join(definitions)

    def _get_phonetic(self, word):
        def format_phonetic(p):
            p = p.replace(r'/', '')
            if p[0] != '[':
                p = '['+p
            if p[-1] != ']':
                p = p+']'
            return p

        def parse_page():
            types = [i.text for i in self.edge_browser.find_elements('xpath', r"//label[@class='op-sound-wrap']/span")]
            types = [i.replace(r'/', '').strip() for i in types]
            phonetics = [i.text for i in self.edge_browser.find_elements('xpath', r"//label[@class='op-sound-wrap']/b")]
            phonetics = [format_phonetic(i) for i in phonetics]
            return list(zip(types, phonetics))

        def check_finish_loading(word):
            dictionary_title_obj = self.edge_browser.find_elements('xpath', r"//div[@class='dictionary-title']/h3[@class='strong']")
            if len(dictionary_title_obj) > 0:
                dictionary_title = dictionary_title_obj[0].text
                if dictionary_title == word:
                    return True
                else:
                    return False
            else:
                return False

        try:
            self.edge_browser.get(BaiduFanyi.URL.format(word=word))
            phonetics_info = []
            for _ in range(10):
                phonetics_info = parse_page()
                if (not check_finish_loading(word)) or (len(phonetics_info) == 0):
                    time.sleep(1)
                else:
                    break
            self.uk_phonetic = "N/A"
            self.us_phonetic = "N/A"
            self.definitions = "N/A"
            if len(phonetics_info) > 0:
                self.phonetic_string = "   ".join([f"{i[0]}{i[-1]}" for i in phonetics_info])
                for i in phonetics_info:
                    if i[0] == '英':
                        self.uk_phonetic = f"{i[0]}{i[-1]}"
                    if i[0] == '美':
                        self.us_phonetic = f"{i[0]}{i[-1]}"
                self.if_definitions_found = True
        except:
            traceback.print_exc()


if __name__ == '__main__':
    bf = BaiduFanyi('apple')
    print(bf.definitions)
