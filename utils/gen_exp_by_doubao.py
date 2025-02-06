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

v. （钟）鸣响
In the distance, a church bell tolled the hour.
The ship's bell tolled mournfully as we mourned the loss of our crewmates.


"chime"的声音更加轻快、悦耳且可能具有旋律性
"toll"的声音则更加深沉、单一且具有庄重或悲哀的情绪色彩
-----------------------------范例结束-------------------------------
我来详细解释格式：
先列出这个单词的不同词性，用诸如n./vi./vt./adj./adv.等简写表示，这个表示法一个词性只用出现一次，其后写出简要中文意思，不同词性间用一个空行隔开。
中文解释的部分格式限定在只有一行，不要换行和多行。这个中文解释尽可能简短，不要出现长句。同一个词性的不同意思之间不要空行。在含义中不要使用分号，用逗号就行。
紧接着给出两个有代表性的纯英语例句，相同含义和其例句之间没有空行。
如果一个词有很多含义，给出常用的含义就行，太生僻的不用。
最后，如果这个词有十分相近的近义词，那么就像范例一样的格式给出区别的解释。近义词区分部分不要直接给出一整段话，每个词单独一行，词在最开头，用半角双引号括起来。这整个部分和前面的部分之间用两个空行隔开。

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
