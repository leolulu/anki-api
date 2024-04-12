import time

from flask import Flask, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

from utils.dict_util import BaiduFanyi
from utils.load_driver import get_edge_driver


class BaiduFanyiVideoDetector(BaiduFanyi):
    def __init__(self) -> None:
        edge_options = Options()
        edge_options.add_argument("--headless")
        edge_options.add_argument("--disable-gpu")
        self.edge_browser = webdriver.Edge(service=Service(get_edge_driver()), options=edge_options)
        self.init_parameter()
        self.goto_legacy_version()

    def detect_video(self, word) -> str:
        self.edge_browser.get(f"https://fanyi.baidu.com/?aldtype=85#en/zh/{word}")
        self.edge_browser.refresh()
        retry_times = 10

        while True:
            try:
                try:
                    self.edge_browser.find_element("xpath", "//a[@class='desktop-guide-close']").click()
                except:
                    pass
                self.edge_browser.find_element("xpath", "//div[@class='dictionary-explain-video']").click()
                break
            except Exception as e:
                print(e)
                retry_times -= 1
                if retry_times < 0:
                    return "none"
                time.sleep(1)

        while True:
            try:
                video_element = self.edge_browser.find_element("xpath", "//video[@class='query-video']")
                video_src = video_element.get_attribute("src") or "none"
                break
            except Exception as e:
                print(e)
                time.sleep(1)

        self.edge_browser.get(f"https://www.baidu.com")
        return video_src


app = Flask(__name__)
CORS(app)
Video_detector = BaiduFanyiVideoDetector()


@app.route("/detect_video", methods=["POST"])
def detect_video_handler():
    payload = request.form
    word = payload["word"]
    video_url = Video_detector.detect_video(word.strip())
    print(f"word: {word}, video url: {video_url}")
    return {"video_url": video_url}


if __name__ == "__main__":
    app.run(debug=False, port=1141, host="0.0.0.0")
