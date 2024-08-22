from flask import Flask, request
from flask_cors import CORS
from selenium.common.exceptions import NoSuchElementException

from utils.dict_util import BaiduFanyi


class BaiduFanyiVideoDetector(BaiduFanyi):
    def __init__(self) -> None:
        pass

    def detect_video(self, word) -> str:
        super().__init__(word)

        if not self.if_video_found:
            return "none"

        try:
            video_element = self.edge_browser.find_element("xpath", ".//video")
            video_src = video_element.get_attribute("src") or "none"
        except NoSuchElementException:
            return "none"

        return video_src


app = Flask(__name__)
CORS(app)
video_detector = BaiduFanyiVideoDetector()


@app.route("/detect_video", methods=["POST"])
def detect_video_handler():
    payload = request.form
    word = payload["word"]
    video_url = video_detector.detect_video(word.strip())
    print(f"word: {word}, video url: {video_url}")
    return {"video_url": video_url}


if __name__ == "__main__":
    app.run(debug=False, port=1141, host="0.0.0.0")
