from __future__ import unicode_literals

from collections import Counter, defaultdict
import csv
import json
import multiprocessing
import pandas as pd
from pyes import ES
import requests
import sys
import time


def get_most_recent_likes(likes, max_number):

    df = pd.DataFrame(likes)
    posts = df.sort('like_dt', ascending=False)['post_id']
    post_ids = [p for p in posts]
    return post_ids[:max_number]


def similar_posts_with_content(post_id, stop_words):
    url_base_content = 'http://localhost:9200/content_index/test-type/'
    url = url_base_content + str(post_id) + '/_mlt?min_score=0.50&size=100&stop_words' + stop_words
    result = requests.get(url)
    tag_score = defaultdict(float)
    try:
        numb_tags = result.json['hits']['total']
    except KeyError:
        return tag_score
    if numb_tags == 0:
        return tag_score
    for hit in result.json['hits']['hits']:
        post_id = int(hit['_id'])
        tag_score[post_id] = float(hit['_score'])
    return tag_score


def similar_posts_with_tags(post_id, stop_words):

    url_base_tag = 'http://localhost:9200/tags_index/test-type/'
    url_tag = url_base_tag + str(post_id) + '/_mlt?size=100&stop_words' + stop_words
    result_tags = requests.get(url_tag)
    tag_score = defaultdict(float)
    try:
        numb_tags = result_tags.json['hits']['total']
    except KeyError:
        return tag_score
    if numb_tags == 0:
        return tag_score
    hits = result_tags.json['hits']['hits']

    for hit in hits:
        post_id = int(hit['_id'])
        tag_score[post_id] = float(hit['_score'])
    return tag_score


def predict_for_user():
    """docstring for predict_for_user"""
    pass


def get_posts_liked(likes):
    posts_liked = set()
    if not likes:
        return posts_liked
    for l in likes:
        posts_liked.add(int(l['post_id']))
    return posts_liked


def predict(fname, max_users, stop_words, output_fname):

    conn = ES(["localhost:9200"])
    fptr = open(fname, 'rb')
    tail = ''
    for word in stop_words:
        tail = tail + word + ','
    tail = tail[0:-1]
    start = time.clock()
    numb_computed = 0
    max_like_count = 50 
    max_to_be_computed = 200 
    fptr_out = open(output_fname, 'wb')

    for line in fptr:
        try:
            data = json.loads(line)
        except ValueError: 
            print 'Value error on json read'
            print line
            continue
        data = json.loads(line)
        in_test_set = data.get('inTestSet')
        
        if not in_test_set:
            continue
        if ((numb_computed % 100) == 0):
            end = time.clock()
            minutes = (end - start) / 60.0
            print 'File: %s Done with %d took %f min. ' %(output_fname, numb_computed, minutes)
        numb_computed += 1
        #if numb_computed > max_to_be_computed:
        #    break
        likes = data.get('likes')
        posts_liked = get_most_recent_likes(likes, max_like_count)
        tag_score = defaultdict(float)
        for like in posts_liked:
            current_tag_score = similar_posts_with_tags(
                post_id=like,
                stop_words=tail
            )
            for post, score in current_tag_score.iteritems():
                tag_score[post] += score
            current_tag_score = similar_posts_with_content(
                post_id=like,
                stop_words=tail,
            )
            for post, score in current_tag_score.iteritems():
                tag_score[post] += score

        counter = Counter(tag_score)
        numb_recommendation_found = len(counter.keys())
        recommended_posts = list()
        numb_liked = len(posts_liked)
        if numb_recommendation_found:
            common = counter.most_common(max_users+numb_liked)
            recommended_posts = [str(c[0]) for c in common if c not in posts_liked]
        uid = data['uid']
        recommended_string = str(uid) + ', ' + ' '.join(recommended_posts[:max_users])
        #print 'number posts liked %d recommended: %d ' %(len(posts_liked), len(recommended_posts))
        fptr_out.write(recommended_string)
        fptr_out.write('\n')
        
    end = time.clock()
    time_taken = (end - start) / 60.0
    fptr_out.close()
    print ' time taken: %f file: %s numb completed', time_taken, output_fname, numb_computed


if __name__ == '__main__':
    """
    predict trainUsers.json stop_words.csv output.csv
    predict <f1> <f2> ...<f8> stop_words.csv output.csv
    """
    stop_words_file = sys.argv[-1]
    conn = ES(["localhost:9200"])

    stop_words = list()
    with open(stop_words_file, 'rb') as f:
        fptr1 = csv.reader(f)
        for row in fptr1:
            for col in row:
                stop_words.append(col)
    max_users = 100
    index = 0
    jobs = list()
    if len(sys.argv) == 3:
        predict(
            fname=sys.argv[1],
            max_users=max_users,
            stop_words=stop_words,
            output_fname='output0.csv',
        )
    else:
        for fname in sys.argv[1:-1]:
            output_fname = 'output' + str(index) + '.csv'
            p = multiprocessing.Process(
                target=predict,
                args=(fname, max_users, stop_words, output_fname)
            )
            index += 1
            jobs.append(p)
            p.start()

