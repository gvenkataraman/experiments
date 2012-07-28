from __future__ import unicode_literals

import csv
import json
from pyes import ES
import requests
import sys


if __name__ == '__main__':
    fname = sys.argv[1]
    fptr = open(sys.argv[1], 'rb')
    line_count = 0
    conn = ES(["localhost:9200"])
    q = {
        #'more_like_this': {
        'like_text': 'miami',
        "min_term_freq" : 1,
        'min_doc_freq': 1,
        'percent_terms_to_match': 0.10,
        #}
    }
    url_base_tag = 'http://localhost:9200/tags_index/test-type/'
    url_base_content = 'http://localhost:9200/content_index/test-type/'
    stop_words = list()
    with open('stop_words.csv', 'rb') as f:
        fptr1 = csv.reader(f)
        for row in fptr1:
            for col in row:
                stop_words.append(col)
    tail = ''
    for word in stop_words:
        tail = tail + word + ','
    
    tail = tail[0:-1]

    for line in fptr:
        data = json.loads(line)
        if data.get('tags'):
            search_string = ' '.join(data['tags'])
            #q['more_like_this']['like_text'] = search_string
            q['like_text'] = search_string
            post_id = int(data.get('post_id'))
            url_tag = url_base_tag + str(post_id) + '/_mlt'
            url_content = url_base_content + str(post_id) + '/_mlt?stop_words=' + tail
            
            #results = conn.morelikethis('content_index', fields=None, doc_type=None, id=post_id, query=q)
            result_tags = requests.get(url_tag)
            if not result_tags:
                continue
            numb_tags = result_tags.json['hits']['total']
            
            results_content = requests.get(url_content)
            import ipdb; ipdb.set_trace()
            
            
            if not results_content:
                continue
            numb_contents = results_content.json['hits']['total']
            if numb_contents:
                import ipdb; ipdb.set_trace()
                print 'here'
            continue
            if result_tags.json and result_content.json:
                if result.json['hits']['total'] == 0:
                    continue
                import ipdb; ipdb.set_trace()
                hits = result.json['hits']['hits'][0] 
                
                source = hits['_source']
                title = hits['title']
                tags = hits['tags']
                import ipdb; ipdb.set_trace()
                print hits
            #results = conn.morelikethis('mpx_selective_index', fields=['tags'], doc_type=None, id=None, query=search_string)
            #results = conn.search(q, indices=['mpx_selective_index'])
            #print results.hits
            print 'done'
