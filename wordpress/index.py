"""
Index everything
Schema in redis:
    key = 'stop_words' , value = set of stop_words
    key = <word>, value = idf
    key = post_id value = set of tags
    key = '__c__<post_id>' value = computed tags as tuples <tag, frequency>
    key = '__c__<word>' value = posting list
"""
from __future__ import unicode_literals
from __future__ import division

from collections import defaultdict
import csv
import json
import redis
import sys
import utils


R_SERVER = redis.Redis('localhost')


def stop_words():
    reader = csv.reader(open('stop_words.csv', 'rb'))
    words = set()

    for row in reader:
        for col in row:
            R_SERVER.sadd('stop_words', col)
            words.add(col)

    R_SERVER.bgsave()
    return words


def store_tags(stop_words):
    import time
    fptr = open(sys.argv[1], 'rb')
    start = time.clock()
    line_count = 0
    idf = defaultdict(int)
    computed_tags = dict()

    for line in fptr.readlines(): 
        if ((line_count % 10000) == 0):
            end = time.clock()
            minutes = (end - start) / 60.0
            print 'Done with %d took %f min. ' %(line_count, minutes)
        line_count += 1
        data = json.loads(line)
        tags = data.get('tags')
        post_id = data['post_id']
        if tags:
            R_SERVER.set(int(post_id), set(tags))
        for tag in tags:
            idf[tag] += 1
        content = data['content']
        tags = utils.compute_tags_from_text(content, stop_words)
        if tags:
            key = '__c__' + str(post_id)
            computed_tags[key] = tags

    for tag, count in idf.iteritems():
        R_SERVER.set(tag, count)

    for tag, value in computed_tags.iteritems():
        R_SERVER.set(tag, value)

    R_SERVER.bgsave()


if __name__ == '__main__':
    """
    sys.argv[1] --> testPosts.json
    """
    stop_words = stop_words()
    store_tags(stop_words)
