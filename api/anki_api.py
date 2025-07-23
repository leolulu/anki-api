import copy
import json
import time
from typing import Any, Dict

import requests

from utils.audio_util import get_valid_audio
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
        self.default_payload: Dict[str, Any] = {"version": version}

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
        for _ in range(10):
            try:
                result = self._execute_action(payload)
                print("集合同步成功...")
                return result
            except UserWarning as e:
                print(f"集合同步失败，原因：{e}")
                time.sleep(1)

    def exit(self):
        # 不起作用，不要用
        payload = copy.copy(self.default_payload)
        payload.update({"action": "guiExitAnki"})
        return self._execute_action(payload)

    def get_deck_names_and_ids(self):
        payload = copy.copy(self.default_payload)
        payload.update({"action": "deckNamesAndIds"})
        return self._execute_action(payload)

    def find_notes(self, search_content: str):
        payload = copy.copy(self.default_payload)
        payload.update({"action": "findNotes"})
        payload.update({"params": {"query": search_content}})
        return self._execute_action(payload)

    def get_notes_info(self, note_ids_or_note_content: list[int] | str):
        payload = copy.copy(self.default_payload)
        payload.update({"action": "notesInfo"})

        if isinstance(note_ids_or_note_content, list):
            payload.update({"params": {"notes": note_ids_or_note_content}})
        elif isinstance(note_ids_or_note_content, str):
            payload.update({"params": {"query": note_ids_or_note_content}})
        else:
            raise ValueError(f"Invalid type: {type(note_ids_or_note_content)}, must be list[int] or str.")

        return self._execute_action(payload)

    def update_note_fields(self, note_id: int, field_and_contents: dict):
        """
        修改已存在笔记的字段内容

        Args:
            note_id: note的id
            field_and_contents: 要更新的字段和内容，格式为 {"field名": "新内容", ...}

        Returns:
            API返回结果
        """
        payload = copy.copy(self.default_payload)
        payload.update({"action": "updateNoteFields"})
        payload.update({"params": {"note": {"id": note_id, "fields": field_and_contents}}})
        return self._execute_action(payload)

    def search_answer_content(self, search_content: str):
        notes_info = self.get_notes_info(search_content)
        result = []
        for info in notes_info:
            if "fields" in info and "答案" in info["fields"]:
                result.append({"id": info["noteId"], "content": info["fields"]["答案"]["value"]})
        return result

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
                    "释义例句等详细内容": bf.definitions.replace("\n", "<br>"),
                },
                "audio": [
                    {
                        "url": f"http://dict.youdao.com/dictvoice?type=1&audio={word}",
                        "filename": f"{word}_uk.mp3",
                        "fields": [
                            "英音标",
                        ],
                    },
                    {
                        "data": get_valid_audio(word),
                        "filename": f"{word}_us.mp3",
                        "fields": [
                            "美音标",
                        ],
                    },
                ],
            }
        }
        payload.update({"params": params})
        return self._execute_action(payload)

    def add_note_from_web(self, word, us_phonetic, explanation, source):
        if source is None:
            source = ""
        payload = copy.copy(self.default_payload)
        payload.update({"action": "addNote"})
        params = {
            "note": {
                "deckName": "背单词",
                "modelName": "新单词模板",
                "fields": {
                    "单词": word,
                    "美音标": us_phonetic,
                    "释义例句等详细内容": highlight_word(word, explanation).replace("\n", "<br>"),
                    "来源例句": highlight_word(word, source, "font-weight: bold;").replace("\n", "<br>"),
                },
                "options": {
                    "allowDuplicate": False,
                    "duplicateScope": "deck",
                },
                "audio": [
                    {
                        "data": get_valid_audio(word),
                        "filename": f"{word}_us.mp3",
                        "fields": [
                            "美音标",
                        ],
                    }
                ],
            }
        }
        payload.update({"params": params})
        return self._execute_action(payload)

    def add_note_second_mode(self, word, us_phonetic, explanation, source=None):
        if source is None:
            source = ""
        payload = copy.copy(self.default_payload)
        payload.update({"action": "addNote"})
        params = {
            "note": {
                "deckName": "自动添加的初见单词",
                "modelName": "问答题自己的左对齐+来源",
                "fields": {
                    "问题": word,
                    "答案": highlight_word(word, explanation).replace("\n", "<br>"),
                    "美音标": us_phonetic,
                    "来源": highlight_word(word, source, "font-weight: bold;").replace("\n", "<br>"),
                },
                "options": {
                    "allowDuplicate": False,
                    "duplicateScope": "all",
                },
                "audio": [
                    {
                        "data": get_valid_audio(word),
                        "filename": f"{word}_us.mp3",
                        "fields": [
                            "美音标",
                        ],
                    }
                ],
            }
        }
        payload.update({"params": params})
        return self._execute_action(payload)


if __name__ == "__main__":
    ak = Anki(port=18765)
    print(ak.add_card("apple"))
