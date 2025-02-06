import re
from utils.highlight_word_rule import simple_rules, complex_rules


def highlight_word_impl(word_provided, explanation, style):
    essence = re.sub(r"<span .*?<\/span>", "", explanation)
    words = re.findall(word_provided, essence, re.IGNORECASE)
    for word in set(words):
        print(f"highlight word: {word}")
        highlighted_word = f'<span style="{style}">{word}</span>'
        explanation = explanation.replace(word, highlighted_word)
    return explanation


def highlight_word(word, explanation, style="color: rgb(219, 147, 23);"):
    for deformer in simple_rules:
        explanation = highlight_word_impl(deformer(word), explanation, style)

    for complex_rule in complex_rules:
        conditioner, deformers = complex_rule
        if conditioner(word):
            for deformer in deformers:
                explanation = highlight_word_impl(deformer(word), explanation, style)

    explanation = highlight_word_impl(word, explanation, style)
    return explanation
