import re
import time
import traceback
from typing import cast

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.webdriver import WebDriver as EdgeWebDriver
from selenium.webdriver.remote.webelement import WebElement

from utils.load_driver import get_edge_driver


class BaiduFanyi:
    EDGE_BROWSER: EdgeWebDriver
    URL = "https://fanyi.baidu.com/#en/zh/{word}"

    def __init__(self, word) -> None:
        if not hasattr(BaiduFanyi, "EDGE_BROWSER"):
            edge_options = Options()
            edge_options.add_argument("--headless")
            edge_options.add_argument("--disable-gpu")
            edge_browser = webdriver.Edge(service=Service(get_edge_driver()), options=edge_options)
            BaiduFanyi.EDGE_BROWSER = edge_browser
        self.edge_browser = BaiduFanyi.EDGE_BROWSER
        self.init_parameter()
        self.if_definitions_found = False
        self._get_phonetic(word)
        if self.if_definitions_found:
            self._get_definition()
            self._detect_video_existence()

    def init_parameter(self):
        self.xpath_phonetic_symbol_us = r"//span[contains(text(), '美')]"
        self.xpath_phonetic_symbol_uk = r"//span[contains(text(), '英')]"
        self.xpath_description_area = r"../../../following-sibling::div"
        self.xpath_actual_description_from_area = r"./div[1]/ul/li"
        self.xpath_video_from_area = r"./div[2]"
        self.reset_status()

    def reset_status(self):
        self.description_area_element = cast(WebElement, None)
        self.video_element = cast(WebElement, None)
        self.if_video_found = False

    def close(self):
        if hasattr(BaiduFanyi, "EDGE_BROWSER"):
            BaiduFanyi.EDGE_BROWSER.close()

    def _detect_video_existence(self):
        try:
            self.video_element = self.description_area_element.find_element("xpath", self.xpath_video_from_area)
            self.if_video_found = True
        except NoSuchElementException:
            return

    def _get_definition(self):
        definitions = [i.text for i in self.description_area_element.find_elements("xpath", self.xpath_actual_description_from_area)]
        definitions = [i.strip().replace("\n", " ").replace("；", "，") for i in definitions]
        self.definitions = "\n".join(definitions)

    def _get_phonetic(self, word):
        def format_phonetic(p):
            p = p.replace(r"/", "")
            if p[0] != "[":
                p = "[" + p
            if p[-1] != "]":
                p = p + "]"
            return p

        def parse_page():
            phonetic_symbol_pattern = r"/(.*?)/"
            phonetics = []
            self.description_area_element = None
            for xpath_phonetic_symbol in [self.xpath_phonetic_symbol_uk, self.xpath_phonetic_symbol_us]:
                elements = self.edge_browser.find_elements("xpath", xpath_phonetic_symbol)
                for elem in elements:
                    if re.search(phonetic_symbol_pattern, elem.text):
                        phonetics.append(format_phonetic(re.findall(phonetic_symbol_pattern, elem.text)[0]))
                        if self.description_area_element is None:
                            self.description_area_element = elem.find_element("xpath", self.xpath_description_area)
                        break
            return list(zip(["英", "美"], phonetics))

        try:
            self.edge_browser.get(BaiduFanyi.URL.format(word=word))
            self.edge_browser.refresh()
            phonetics_info = []
            for _ in range(10):
                phonetics_info = parse_page()
                if len(phonetics_info) == 0:
                    time.sleep(1)
                else:
                    break
            self.uk_phonetic = "N/A"
            self.us_phonetic = "N/A"
            self.definitions = "N/A"
            if len(phonetics_info) > 0:
                self.phonetic_string = "   ".join([f"{i[0]}{i[-1]}" for i in phonetics_info])
                for i in phonetics_info:
                    if i[0] == "英":
                        self.uk_phonetic = f"{i[0]}{i[-1]}"
                    if i[0] == "美":
                        self.us_phonetic = f"{i[0]}{i[-1]}"
                self.if_definitions_found = True
        except:
            traceback.print_exc()


if __name__ == "__main__":
    bf = BaiduFanyi("apple")
    print(bf.definitions)
