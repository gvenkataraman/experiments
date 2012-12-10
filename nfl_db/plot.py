from __future__ import unicode_literals

import argparse
from collections import defaultdict
import csv
from dateutil import parser

from nfl import db, Game


def hist_plot(x, y, output_file):
    import numpy as np
    import matplotlib.pyplot as plt

    pos = np.arange(len(x))
    width = 1.0    # gives histogram aspect to the bar diagram

    ax = plt.axes()
    ax.set_xticks(pos + (width / 2))
    ax.set_xticklabels(x)

    plt.bar(pos, y, width, color='r')
    plt.savefig(output_file)


def execute(args):
    with open(args.input_file, 'rb') as f:
        reader = csv.DictReader(f)
        spread_stats_count = defaultdict(int)
        for row in reader:
            diff = int(row['spread']) - int(row['actual_spread'])
            spread_stats_count[diff] += 1
        spread_data = [(k, v) for k, v in spread_stats_count.iteritems()]
        spread_data.sort(key = lambda tup: tup[0])
        x = [s[0] for s in spread_data]
        y = [s[1] for s in spread_data]
        hist_plot(x, y, args.output_file)


def main():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('--input_file', action='store', 
                            dest='input_file',)
    arg_parser.add_argument('--output_file', action='store', 
                            dest='output_file',)
    args = arg_parser.parse_args()
    execute(args)


if __name__ == '__main__':
    main()
