import json
from typing import Any, Dict
import requests

import copy

from utils.dict_util import BaiduFanyi
from utils.highlight_word import highlight_word


class Anki:
    RESPONSE_RESULT = "result"
    RESPONSE_ERROR = "error"

    def __init__(self, port) -> None:
        self.endpoint = f"http://127.0.0.1:{port}"
        self._build_default_payload()

    def _build_default_payload(self):
        version = int(requests.post(self.endpoint, data='{"action": "version"}').content)
        self.default_payload: Dict[str, Any] = {
            "version": version
        }

    def _execute_action(self, payload: dict):
        r = requests.post(self.endpoint, data=json.dumps(payload))
        r.raise_for_status()
        response = json.loads(r.content)
        if response[Anki.RESPONSE_ERROR] is not None:
            raise UserWarning(f"Request fail: {response[Anki.RESPONSE_ERROR]}")
        return response[Anki.RESPONSE_RESULT]

    def sync(self):
        payload = copy.copy(self.default_payload)
        payload.update({"action": "sync"})
        return self._execute_action(payload)

    def get_deck_names_and_ids(self):
        payload = copy.copy(self.default_payload)
        payload.update({"action": "deckNamesAndIds"})
        return self._execute_action(payload)

    def add_card(self, word):
        payload = copy.copy(self.default_payload)
        payload.update({"action": "guiAddCards"})
        bf = BaiduFanyi(word)
        params = {
            "note": {
                "deckName": "背单词",
                "modelName": "新单词模板",
                "fields": {
                    "单词": word,
                    "英音标": bf.uk_phonetic,
                    "美音标": bf.us_phonetic,
                    "释义例句等详细内容": bf.definitions.replace('\n', '<br>')
                },
                "audio": [
                    {
                        "url": f"http://dict.youdao.com/dictvoice?type=1&audio={word}",
                        "filename": f"{word}_uk.mp3",
                        "fields": [
                            "英音标"
                        ]
                    },
                    {
                        "url": f"http://dict.youdao.com/dictvoice?type=0&audio={word}",
                        "filename": f"{word}_us.mp3",
                        "fields": [
                            "美音标"
                        ]
                    }
                ]
            }
        }
        payload.update({"params": params})
        return self._execute_action(payload)

    def add_note_from_web(self, word, us_phonetic, explanation, source):
        payload = copy.copy(self.default_payload)
        payload.update({"action": "addNote"})
        params = {
            "note": {
                "deckName": "背单词",
                "modelName": "新单词模板",
                "fields": {
                    "单词": word,
                    "美音标": us_phonetic,
                    "释义例句等详细内容": highlight_word(word, explanation).replace('\n', '<br>'),
                    "来源例句": source.replace('\n', '<br>')
                },
                "options": {
                    "allowDuplicate": False,
                    "duplicateScope": "deck"
                },
                "audio": [
                    {
                        "url": f"http://dict.youdao.com/dictvoice?type=0&audio={word}",
                        "filename": f"{word}_us.mp3",
                        "fields": [
                            "美音标"
                        ]
                    }
                ]
            }
        }
        payload.update({"params": params})
        return self._execute_action(payload)


if __name__ == '__main__':
    ak = Anki(port=18765)
    print(ak.add_card('apple'))
