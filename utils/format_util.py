import re


def format_explanation(explanation: str, word: str):
    explanation = re.sub(rf'^"{word}"', rf'"<b>{word}</b>"', explanation, flags=re.MULTILINE)
    return explanation
