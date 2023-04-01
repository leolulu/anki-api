from api.anki_api import Anki


if __name__ == '__main__':
    ak = Anki(port=18765)
    while True:
        ak.add_card(input("输入单词：").strip().lower())
