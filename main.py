from api.anki_api import Anki


if __name__ == '__main__':
    ak = Anki(port=18765)
    print(ak.add_card('symbiotic'))
