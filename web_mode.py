import re
from dash import Dash, html, dcc, Input, Output, State
from spellchecker import SpellChecker
from api.anki_api import Anki

from utils.dict_util import BaiduFanyi

app = Dash(__name__)
ak = Anki(port=18765)

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Label('单词：'),
            html.Button('填充内容', id='fill_content'),
            html.Button('检查拼写', id='spell_check'),
            html.Button('提交新建', id='submit')
        ]),
        html.Div(dcc.Input(type='text', className='word', id='word')),
        html.Div([
            html.Label('释义例句等详细内容：'),
            html.Label(id='explanation_check_result', className='red')
        ]),
        html.Div(dcc.Textarea(className='wild high', id='explanation')),
        html.Div([
            html.Label('来源例句：'),
            html.Label(id='source_check_result', className='red')
        ]),
        html.Div(dcc.Textarea(className='wild high', id='source')),
        dcc.Store(id='us_phonetic')
    ], className='container')
])


@app.callback(
    Output('explanation_check_result', 'children'),
    Output('source_check_result', 'children'),
    Input('spell_check', 'n_clicks'),
    State('explanation', 'value'),
    State('source', 'value'),
    prevent_initial_call = True
)
def spell_check(n_clicks, explanation, source):
    source_check_result = ''

    def get_words(content):
        words = re.split(r"[ ,\.']", content)
        words = [i for i in words if re.search(r"^[a-zA-Z]*$", i)]
        words = [i for i in words if len(i) >= 3]
        words = [i for i in words if i != ""]
        return words

    spell = SpellChecker()

    if explanation is None or explanation == '':
        explanation_check_result = ''
    else:
        explanation_check_result = spell.unknown(get_words(explanation))
        if explanation_check_result:
            explanation_check_result = f"有拼写错误：{', '.join(explanation_check_result)}"
        else:
            explanation_check_result = ''

    if source is None or source == '':
        source_check_result = ''
    else:
        source_check_result = spell.unknown(get_words(source))
        if source_check_result:
            source_check_result = f"有拼写错误：{', '.join(source_check_result)}"
        else:
            source_check_result = ''

    return explanation_check_result, source_check_result


@app.callback(
    Output('explanation', 'value'),
    Output('us_phonetic', 'data'),
    Output('word', 'value',allow_duplicate=True),
    Input('fill_content', 'n_clicks'),
    State('word', 'value'),
    prevent_initial_call = True
)
def update_explanation(n_clicks, word):
    word = word.strip().lower()
    print(f"word in update_explanation: {word}")
    if word is None or word == '':
        return '', '', ''
    bf = BaiduFanyi(word)
    return bf.definitions, bf.us_phonetic, word


@app.callback(
    Output('word', 'value',allow_duplicate=True),
    Input('submit', 'n_clicks'),
    State('word', 'value'),
    State('us_phonetic', 'data'),
    State('explanation', 'value'),
    prevent_initial_call = True
)
def submit_adding_note(n_clicks, word, us_phonetic, explanation):
    print(f"word in submit_adding_note: {word}")
    if word is None or word == '':
        return ''
    ak.add_note_from_web(word, us_phonetic, explanation)
    return ''


if __name__ == '__main__':
    app.run_server(debug=True)
