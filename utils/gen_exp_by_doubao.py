import textwrap

import requests

from utils.config_util import get_or_create_config

system_message = "你是一个背单词的flashcard的生成器，专业效果的那种，你会仔细分析用户的要求，然后完美地生成用户所需要的背单词卡片的内容"
user_message = textwrap.dedent(
"""
我将提供一个标准范例，你会按照这样的格式生成新单词的flashcard。
比如单词“toll”: 
--------------------------范例开始------------------------------
n. (道路、桥梁的)通行费
motorway tolls
a toll road/bridge
伤亡人数
The official death toll has now reached 7000.
the war's growing casualty toll
代价
Years of smoking have taken their toll on his health.
a heavy toll on the environment

v. （钟）鸣响
In the distance, a church bell tolled the hour.
The ship's bell tolled mournfully as we mourned the loss of our crewmates.
征收
The bridge is tolled during peak hours.
Motorists are tolled when they enter the city.


"chime"的声音更加轻快、悦耳且可能具有旋律性
"toll"的声音则更加深沉、单一且具有庄重或悲哀的情绪色彩
-----------------------------范例结束-------------------------------

有几个要注意的点：
输出内容不包括'范例开始'和'范例结束'这两行
换行和空行分隔数量需要与范例保持一致，不要自由发挥。
中文解释中不要出现分号，用逗号
近义词区分部分不要直接给出一整段话，如同范例格式一样，每个词单独一行，每行以半角双引号包裹的词开头，紧接着在同一行写完该词的内容
词性标识中的动词尤其要区分vt./vi.，不能统写为v.
例句要能充分表达这个词的内涵和使用方法，不要类似于 'this is 某个名词' 'sth. is 某个形容词' 这样的对于学习理解几乎没用的
如果一个词有很多含义，给出常用的含义就行，太生僻的不用
近义词区分部分不是必要的，除非这个词有在日常使用中容易搞混的近义词

好的，在充分理解规则以后，我们现在就开始。请给出“{word}”这个词的flashcard
""".strip()
)


def get_explanation_by_doubao(word):
    url = get_or_create_config("doubao_endpoint")
    payload = {"system_message": system_message, "user_message": user_message.format(word=word)}
    res = requests.post(url, json=payload)
    res.raise_for_status()
    return _post_process_explanation(res.text)


def _post_process_explanation(exp):
    exp = exp.replace("“", '"')
    exp = exp.replace("”", '"')
    exp = exp.replace(' "', '"')
    exp = exp.replace('" ', '"')
    exp = exp.replace("。\n", "\n")
    exp = exp.replace("，而", "\n")
    exp = exp.strip().strip("。")
    return exp
