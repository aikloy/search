import hgtk
from hgtk.exception import NotHangulException


def split_char(sentence):
    sentence = "".join(sentence.strip().split())
    clean_sentence = ""
    for char in sentence:
        try:
            decompose_char = hgtk.letter.decompose(char)
            for x in decompose_char:
                if x != "":
                    clean_sentence += x
        except NotHangulException:
            clean_sentence += char

    return clean_sentence
