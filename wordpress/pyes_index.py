from __future__ import unicode_literals

import json
from pyes import ES
import sys


def index():
    """docstring for fname"""
    import time
    fptr = open(sys.argv[1], 'rb')
    line_count = 0
    conn = ES(["localhost:9200"])
    #conn.create_index('test-index')
    start = time.clock()
    numb_exceptions = 0

    for line in fptr:
        if ((line_count % 10000) == 0):
            end = time.clock()
            minutes = (end - start) / 60.0
            print 'Done with %d took %f min. ' %(line_count, minutes)
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
    index()
#    fname = sys.argv[1]
#    fptr = open(sys.argv[1], 'rb')
#    line_count = 0
#    conn = ES(["localhost:9200"])
#    q = {
#        'more_like_this': {
#            'like_text': 'miami',
#            "min_term_freq" : 1,
#            'min_doc_freq': 1,
#            'percent_terms_to_match': 0.10,
#        }
#    }
#    results = conn.search(q)
#    
#    print results
#    for line in fptr:
#        data = json.loads(line)
#        q['more_like_this']['like_text'] = data['content']
#        results = conn.search(q)
#        print results.hits
#        import ipdb; ipdb.set_trace()
#        print 'done'
#    conn.create_index('test-index7')
#    start = time.clock()
#    
#    for line in fptr:
#        
#        if ((line_count % 1000) == 0):
#            end = time.clock()
#            minutes = (end - start) / 60.0
#            print 'Done with %d took %f min. ' %(line_count, minutes)
#        line_count += 1
#
#        data = json.loads(line)
#        post_id = int(data['post_id'])
#        content = data['content']
#        conn.index({ "tags": data.get('tags'), 'content': content}, 
#            "test-index", "test-type", post_id)
#
