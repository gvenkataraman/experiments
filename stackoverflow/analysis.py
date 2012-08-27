from __future__ import division

import sys
import pandas as pd 


if __name__ == '__main__':
    input_file = sys.argv[1]
    # find relation between status and numb deleted
    data = pd.read_csv(input_file)
    num_low_answer_count = 0
    num_low_answer_count_unopen = 0

    num_entries = len(data.index)

    for index in xrange(num_entries):
        undeleted_count = data['OwnerUndeletedAnswerCountAtPostTime'][index]
        status = data['OpenStatus'][index]
        if undeleted_count >= 1000:
            num_low_answer_count += 1
            if status.lower() != 'open':
                num_low_answer_count_unopen += 1

    perc = 100 * num_low_answer_count_unopen / num_low_answer_count
    print round(perc, 2)
