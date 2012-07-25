from __future__ import unicode_literals
from __future__ import division

from collections import Counter, defaultdict
from HTMLParser import HTMLParser
import nltk


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def is_word_eligible(word, stop_words):
    if word in stop_words:
        return False
    if len(word) <= 1:
        return False
    if not word.isalpha():
        return False
    return True


def compute_tags_from_text(content, stop_words):
    try:
        reduced_content = strip_tags(content)
    except Exception:
        return None
    text = nltk.word_tokenize(reduced_content)
    word_count = defaultdict(int)
    for t1 in text:
        t = t1.lower()
        if is_word_eligible(t, stop_words):
            word_count[t] += 1
    count = Counter(word_count)
    tags = list()
    for word, count in count.most_common(10):
        if count < 3:
            break
        tags.append((word, count))
    return tags
