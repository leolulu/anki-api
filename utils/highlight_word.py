import re


def highlight_word(word, explanation):
    explanation = re.sub(r"<span .*?<\/span>", "", explanation)
    if word in explanation:
        print(f"highlight word: {word}")
        highlighted_word = f'<span style="color: rgb(219, 147, 23);">{word}</span>'
        explanation = explanation.replace(word, highlighted_word)
    return explanation
