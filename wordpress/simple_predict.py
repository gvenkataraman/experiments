from __future__ import unicode_literals

from collections import Counter, defaultdict
import csv
import json
import multiprocessing
import pandas as pd
from pyes import ES
import redis
import requests
import sys
import time


R_SERVER = redis.Redis('localhost')


def populate_blog_to_posts():
    """docstring for populate_blog_to_posts"""
    pass


def main():
    train_file = sys.argv[1]
    fptr = open(train_file, 'rb')

    for line in fptr:
        data = json.loads(line)
        likes = data.get('likes')
        if not likes:
            continue
        for like in likes:
            blog = like['blog']
            post_id = int(like['post_id'])
            tags = R_SERVER.get(post_id)
            import ipdb; ipdb.set_trace()
            
            print tags


if __name__ == '__main__':
    main()
