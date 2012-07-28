from __future__ import unicode_literals

from pyes import ES


if __name__ == '__main__':
    conn = ES(["localhost:9200"])
    indices = ('content_index', 'title_index')
    for index in indices:
        if not conn.exists_index(index):
            conn.create_index(index)
