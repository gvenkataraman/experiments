"""
Index everything
Schema in redis:
    key = 'stop_words' , value = set of stop_words
    key = <word>, value = idf
    key = post_id value = set of tags
    key = '__c__<post_id>' value = computed tags as tuples <tag, frequency>
    key = '__p__<word>' value = posting list
    key = '__f__<word>' value = idf for computed_tags
"""
from __future__ import unicode_literals
from __future__ import division

from collections import defaultdict
import csv
import json
import multiprocessing
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


def _add_word_to_posting_list(word, posting_list, post_id):
    posting_list_str = '__p__' + word
    try:
        current_posting_list = posting_list[posting_list_str]
    except KeyError:
        current_posting_list = set()
        posting_list[posting_list_str] = current_posting_list
    current_posting_list.add(post_id)


def store_tags(stop_words, fname):
    """
    1. key = 'word', value = idf - Done
    2. key = post_id value = set of tags - Done
    3. key = '__c__<post_id>' value = computed tags as tuples <tag, frequency> - Done
    4. key = '__p__<word>' value = posting list
    5. key = '__f__<word>' value = idf for computed_tags
    """
    import time
    fptr = open(fname, 'rb')
    start = time.clock()
    line_count = 0
    idf = defaultdict(int)
    idf_computed_tags = defaultdict(int)
    #computed_tags = dict()
    posting_list = dict()

    for line in fptr:
        if ((line_count % 10000) == 0):
            end = time.clock()
            minutes = (end - start) / 60.0
            print 'file: %s Done with %d took %f min. ' %(fname, line_count, minutes)

        line_count += 1
        data = json.loads(line)
        tags = data.get('tags')
        post_id = int(data['post_id'])
        tag_set = set()
        if tags:
            tag_set = set([t.lower() for t in tags if t])
            # number_2
            R_SERVER.set(post_id, tag_set)

        for tag in tags:
            if not tag:
                continue
            idf[tag] += 1
            _add_word_to_posting_list(tag, posting_list, post_id)

        content = data['content']
        computed_tags = utils.compute_tags_from_text(content, stop_words)
        if computed_tags:
            key = '__c__' + str(post_id)
            # number_3
            R_SERVER.set(key, computed_tags)

            for tag in computed_tags:
                word = tag[0]
                idf_computed_tags[word] += 1
                _add_word_to_posting_list(word, posting_list, post_id)

    for tag, count in idf.iteritems():
        # number_1
        current_count = R_SERVER.get(tag)
        total_count = (count + int(current_count)) if current_count else count
        R_SERVER.set(tag, total_count)

    for tag, count in idf_computed_tags.iteritems():
        tag_str = '__f__' + tag
        # number_5
        current_count = R_SERVER.get(tag_str)
        total_count = (count + int(current_count)) if current_count else count
        R_SERVER.set(tag_str, total_count)

    for tag, current_list in posting_list.iteritems():
        tag_str = '__p__' + tag
        # number_4
        stored_list = R_SERVER.get(tag_str)
        new_list = stored_list.extend(current_list) if stored_list else current_list 
        R_SERVER.set(tag_str, new_list)

    fptr.close()
    R_SERVER.bgsave()


if __name__ == '__main__':
    """
    sys.argv[1] --> testPosts.json
    """
    stop_words = stop_words()
    if len(sys.argv) == 2:
        store_tags(stop_words, sys.argv[1])
    else:
        jobs = list()
        for fname in sys.argv[1:]:
            print fname
            p = multiprocessing.Process(
                target=store_tags,
                args=(stop_words, fname)
            )
            jobs.append(p)
            p.start()
