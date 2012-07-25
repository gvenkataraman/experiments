from __future__ import unicode_literals

import csv
import redis

R_SERVER = redis.Redis('localhost')

def main():
    reader = csv.reader(open('stop_words.csv', 'rb'))

    for row in reader:
        import ipdb; ipdb.set_trace()
        
        for col in row:
            R_SERVER.sadd('stop_words', col)

    R_SERVER.bgsave()

if __name__ == '__main__':
    main()
