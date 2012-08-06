"""
Everything related to graph
"""
from __future__ import division

import json
import networkx as nx
import sys

class Data(object):

    def __init__(self, fname):
        super(Data, self).__init__()
        self.fname = fname
        self.affinity = nx.Graph()
        self.post_id_to_blog_id = dict()
        self.blog_id_to_post_id = dict()
        self.uid_to_post_id_likes = dict()

    def read(self):
        fptr = open(self.fname, 'rb')

        for line in fptr:
            data = json.loads(line)
            blog_id = int(data['blog'])
            post_id = int(data['post_id'])
            self.post_id_to_blog_id[post_id] = blog_id
            try:
                post_id_set = self.blog_id_to_post_id[blog_id]
            except KeyError:
                post_id_set = set()
                self.blog_id_to_post_id[blog_id] = post_id_set
            post_id_set.add(post_id)
            likes = data.get('likes')
            if likes:
                self._store_affinity_graph(likes)
            for like in likes:
                uid = int(like['uid'])
                try:
                    post_id_likes = self.uid_to_post_id_likes[uid]
                except KeyError:
                    post_id_likes = set()
                    self.uid_to_post_id_likes[uid] = post_id_likes
                post_id_likes.add(post_id)

    def _store_affinity_graph(self, likes):
        uids = list()
        for like in likes:
            uids.append(int(like['uid']))
        numb_uids = len(uids)
        for index1 in xrange(numb_uids):
            uid1 = uids[index1]
            for uid2 in uids[index1:]:
                try:
                    edge = self.affinity[uid1][uid2]
                    weight = edge['weight']
                    self.affinity.add_edge(uid1, uid2, weight=weight+1)
                except KeyError: 
                    self.affinity.add_edge(uid1, uid2, weight=1)


if __name__ == '__main__':
    data = Data(sys.argv[1])
    data.read()
    import ipdb; ipdb.set_trace()
    print 'done'
