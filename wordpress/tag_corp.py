"""
Simple way to tag docs
"""
from __future__ import unicode_literals
from __future__ import division

from collections import Counter, defaultdict
from HTMLParser import HTMLParser
import json
import redis
import nltk
import sys

R_SERVER = redis.Redis('localhost')


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


def _is_word_eligible(word, stop_words):
    if word in stop_words:
        return False
    if len(word) <= 1:
        return False
    if not word.isalpha():
        return False
    return True


def frequency_tags():
    import time
    fptr = open(sys.argv[1], 'rb')
    start = time.clock()
    added_words = set()
    line_count = 0
    
    for line in fptr.readlines():
        if ((line_count % 10000) == 0):
            end = time.clock()
            minutes = (end - start) / 60.0
            print 'Done with %d took %f min. ' %(line_count, minutes)
            start = end
        line_count += 1
        data = json.loads(line)
        tags = data['tags']
        if not tags:
            continue
        for tag in tags:
            if not tag:
                continue
            tag_lower = tag.lower()
            tag_string = '__tag__' + tag_lower
            if tag_lower not in added_words:
                added_words.add(tag_lower)
                R_SERVER.set(tag_string, 1)
            else:
                R_SERVER.incr(tag_string)


def generated_tags():
    import time
    fptr = open(sys.argv[1], 'rb')
    stop_words = R_SERVER.smembers('stop_words')
    start = time.clock()
    added_words = set()
    line_count = 0
    
    for line in fptr.readlines():
        if ((line_count % 10000) == 0):
            end = time.clock()
            minutes = (end - start) / 60.0
            print 'Done with %d took %f min. ' %(line_count, minutes)
            start = end
        line_count += 1
        data = json.loads(line)
        content = data['content']
        try:
            reduced_content = strip_tags(content)
        except Exception:
            continue
        text = nltk.word_tokenize(reduced_content)
        word_count = defaultdict(int)
        for t1 in text:
            t = t1.lower()
            if _is_word_eligible(t, stop_words):
                word_count[t] += 1
        count = Counter(word_count)
        tags = list()
        for word, count in count.most_common(10):
            if count < 3:
                break
            tags.append((word, count))
            if word in added_words:
                R_SERVER.incr(word)
            else:
                added_words.add(word)
                R_SERVER.set(word, 1)

        if len(tags) > 1:
            value = json.dumps({
                'computed_tags': tags,
                'tags': data['tags'],
                'categeries': data['categories'],
                'language': data['language'],
                'title': data['title'],
                'blog': data['blog'],
            }
            )
            post_id = data['post_id']
            R_SERVER.set(int(post_id), value)

    R_SERVER.bgsave()

if __name__ == '__main__':
    frequency_tags()
