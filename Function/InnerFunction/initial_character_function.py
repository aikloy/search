import hgtk
from hgtk.exception import NotHangulException


def convert_to_initial_sentence(sentence):
    sentence = "".join(sentence.strip().split())

    initial_sentence = ""
    for char in sentence:
        try:
            split_char = hgtk.letter.decompose(char)
            initial_sentence += split_char[0]
        except NotHangulException:
            initial_sentence += char

    return initial_sentence


def find_related_sentences(initial_query, sentences):
    results = []
    for initial_sentence in sentences:
        score = 0
        if initial_sentence in initial_query:
            score += len(initial_sentence)
        results.append({"score": score, "sentence": sentences[initial_sentence]})
    return sorted(results, key=lambda x: x["score"], reverse=True)
