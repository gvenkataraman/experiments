from __future__ import unicode_literals

import multiprocessing
import json
from pyes import ES
import sys


def index(fname):
    """docstring for fname"""
    import time
    fptr = open(fname, 'rb')
    line_count = 0
    conn = ES(["localhost:9200"])
    #conn.create_index('mpx-test-index')
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
        post_id = int(data['post_id'])
        if post_id and data:
            try:
                conn.index(data, "test-index", "test-type", post_id)
            except Exception:
                numb_exceptions += 1
                continue

    print 'number of exceptions ', numb_exceptions

if __name__ == '__main__':
    jobs = list()
    for fname in sys.argv[1:]:
        p = multiprocessing.Process(target=index, args=(fname,))
        jobs.append(p)
        p.start()
