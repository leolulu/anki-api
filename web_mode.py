import re
from time import sleep
from urllib.parse import unquote

import psutil
from dash import Dash, Input, Output, State, dcc, html
from spellchecker import SpellChecker

from api.anki_api import Anki
from constants.env import ENV_VAR_ANKI_PATH, EXE_NAME_ANKI, PROGRAM_NAME_ANKI
from utils.anki_initiator import AnkiProcess, init_anki
# from utils.dict_util import BaiduFanyi
from utils.env_var_util import read_user_environment_variable, set_user_environment_variable
from utils.gen_exp_by_doubao import get_explanation_by_doubao
from utils.youdao import get_phonetic_by_youdao


# BaiduFanyi.init_edge_browser()
spell = SpellChecker()


def start_anki(actually_start=True):
    path = read_user_environment_variable(ENV_VAR_ANKI_PATH)
    if not path:
        path = set_user_environment_variable(ENV_VAR_ANKI_PATH, input(f"请输入{PROGRAM_NAME_ANKI}可执行文件路径:").strip().strip('"'))
    if actually_start:
        if not EXE_NAME_ANKI in [i.info["name"] for i in psutil.process_iter(["name"])]:
            init_anki(path)


start_anki(actually_start=False)


app = Dash(__name__)
app.title = "Anki添加器"
app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Label("单词："),
                        html.Button("填充内容", id="fill_content"),
                        html.Button("检查拼写", id="spell_check"),
                        html.Button("提交新建", id="submit"),
                    ]
                ),
                html.Div(dcc.Input(type="text", className="word", id="word")),
                html.Div([html.Label("释义例句等详细内容："), html.Label(id="explanation_check_result", className="red")]),
                html.Div(dcc.Textarea(className="wild triple-high", id="explanation")),
                html.Div([html.Label("来源例句："), html.Label(id="source_check_result", className="red")]),
                html.Div(dcc.Textarea(className="wild high", id="source")),
                dcc.Store(id="us_phonetic"),
            ],
            className="container",
        ),
        dcc.Location(id="url"),
    ]
)


@app.callback(
    Output("explanation_check_result", "children"),
    Output("source_check_result", "children"),
    Input("spell_check", "n_clicks"),
    State("explanation", "value"),
    State("source", "value"),
    prevent_initial_call=True,
)
def spell_check(n_clicks, explanation, source):
    source_check_result = ""

    def get_words(content):
        words = re.split(r"[ ,\.']", content)
        words = [i for i in words if re.search(r"^[a-zA-Z]*$", i)]
        words = [i for i in words if len(i) >= 3]
        words = [i for i in words if i != ""]
        return words

    if explanation is None or explanation == "":
        explanation_check_result = ""
    else:
        explanation_check_result = spell.unknown(get_words(explanation))
        explanation_check_result = [i for i in explanation_check_result if i not in ["adj", "sth", "adv", "conj", "prep"]]
        if explanation_check_result:
            explanation_check_result = f"有拼写错误：{', '.join(explanation_check_result)}"
        else:
            explanation_check_result = ""

    if source is None or source == "":
        source_check_result = ""
    else:
        source_check_result = spell.unknown(get_words(source))
        if source_check_result:
            source_check_result = f"有拼写错误：{', '.join(source_check_result)}"
        else:
            source_check_result = ""

    return explanation_check_result, source_check_result


@app.callback(
    Output("explanation", "value"),
    Output("us_phonetic", "data"),
    Output("word", "value", allow_duplicate=True),
    Input("fill_content", "n_clicks"),
    State("word", "value"),
    prevent_initial_call=True,
)
def fetch_explanation(n_clicks, word):
    word = word.strip().lower()
    print(f"word in update_explanation: {word}")
    if word is None or word == "":
        return "", "", ""
    # bf = BaiduFanyi(word)
    # return bf.definitions, bf.us_phonetic, word
    return get_explanation_by_doubao(word), get_phonetic_by_youdao(word), word


@app.callback(
    Output("word", "value"),
    Output("fill_content", "n_clicks"),
    Input("url", "search"),
    State("fill_content", "n_clicks"),
)
def gen_content_from_url_params(search_string, n_clicks):
    if not search_string:
        return "", 0
    for param_pair in search_string.replace("?", "").split("&"):
        key, value = param_pair.split("=")
        key = unquote(key)
        value = unquote(value)
        if key == "word":
            return value, (0 if not n_clicks else n_clicks) + 1


@app.callback(
    Output("word", "value", allow_duplicate=True),
    Output("explanation", "value", allow_duplicate=True),
    Output("source", "value", allow_duplicate=True),
    Input("submit", "n_clicks"),
    State("word", "value"),
    State("us_phonetic", "data"),
    State("explanation", "value"),
    State("source", "value"),
    prevent_initial_call=True,
)
def submit_adding_note(n_clicks, word, us_phonetic, explanation, source):
    print(f"word in submit_adding_note: {word}")
    if word is None or word == "":
        return "", "", ""
    start_anki()
    ak = Anki(port=18765)
    while not "背单词" in ak.get_deck_names_and_ids():
        sleep(1)
    ak.add_note_from_web(word, us_phonetic, explanation, source)
    ak.sync()
    ak.exit()
    AnkiProcess.terminate()
    return "", "", ""


@app.callback(
    Output("fill_content", "disabled"),
    Output("submit", "disabled"),
    Input("explanation", "value"),
)
def disable_new_before_submit(value):
    if_has_content = True if value else False
    return if_has_content, not if_has_content


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=1130, debug=False)
