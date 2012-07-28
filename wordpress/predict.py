from __future__ import unicode_literals

from collections import Counter, defaultdict
import csv
import json
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


def predict(conn, fname, max_users, stop_words):

    fptr = open(fname, 'rb')
    tail = ''
    for word in stop_words:
        tail = tail + word + ','
    tail = tail[0:-1]
    start = time.clock()
    numb_computed = 0
    max_like_count = 20
    max_to_be_computed = 1000

    for line in fptr:
        data = json.loads(line)
        if not data.get('inTestSet'):
            continue
        numb_computed += 1
        if numb_computed > max_to_be_computed:
            break
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
        recommended_posts = set()
        numb_common = 0
        if numb_recommendation_found:
            common = counter.most_common(max_users)
            posts = set()
            for c in common:
                posts.add(c[0])
            recommended_posts = posts.difference(posts_liked)
            numb_common = len(posts.intersection(posts_liked))
    end = time.clock()
    time_taken = (end - start) / 60.0
    print ' time taken ', time_taken
    print 'numb completed ', numb_computed



if __name__ == '__main__':
    """
    predict trainUsers.json stop_words.csv
    """
    fname = sys.argv[1]
    conn = ES(["localhost:9200"])

    stop_words = list()
    with open(sys.argv[2], 'rb') as f:
        fptr1 = csv.reader(f)
        for row in fptr1:
            for col in row:
                stop_words.append(col)
    max_users = 100
    predict(fname=fname, 
            conn=conn, 
            max_users=max_users, 
            stop_words=stop_words)
