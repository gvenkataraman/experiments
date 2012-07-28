from __future__ import unicode_literals

import json
import multiprocessing
from pyes import ES
import sys
import time

import utils


def index(fname, index_name, keys_to_tag):
    fptr = open(fname, 'rb')
    line_count = 0
    conn = ES(["localhost:9200"])
    if not conn.exists_index(index_name):
        conn.create_index(index_name)
    start = time.clock()
    numb_exceptions = 0

    for line in fptr:
        if ((line_count % 10000) == 0):
            end = time.clock()
            minutes = (end - start) / 60.0
            print 'File: %s Done with %d took %f min. ' %(fname, line_count, minutes)
            print 'number of exceptions ', numb_exceptions
        line_count += 1
        data = json.loads(line)
        if not data.get('tags'):
            continue
        post_id = int(data['post_id'])
        found_content = False
        for k in keys_to_tag:
            if data.get(k):
                found_content = True
        if not found_content:
            continue
        index_data = dict()
        for k in keys_to_tag:
            value = data.get(k)
            if (value and (k == 'content')):
                try:
                    stripped_value = utils.strip_tags(value)
                except Exception:
                    stripped_value = value
                index_data[k] = stripped_value
        if post_id and data:
            try:
                conn.index(index_data, index_name, "test-type", post_id)
            except Exception:
                numb_exceptions += 1
                continue

    print 'number of exceptions ', numb_exceptions

if __name__ == '__main__':
    jobs = list()
    index_name = sys.argv[-1]
    keys_to_tag = sys.argv[-2].split()
    conn = ES(["localhost:9200"])
    for fname in sys.argv[1:-2]:
        p = multiprocessing.Process(target=index, args=(fname, index_name, keys_to_tag))
        jobs.append(p)
        p.start()
