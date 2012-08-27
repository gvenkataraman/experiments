"""
Input = full file
output = take out the markdown and just put the length
"""
from __future__ import division

import csv
import sys


def main(input_file, output_file):
    fptr_in = open(input_file, 'rb')
    reader = csv.DictReader(fptr_in)
    fptr = open(output_file, 'wb')
    output= ('PostId,PostCreationDate,OwnerUserId,OwnerCreationDate,ReputationAtPostCreation,OwnerUndeletedAnswerCountAtPostTime,Title,markdown_length,Tag1,Tag2,Tag3,Tag4,Tag5,PostClosedDate,OpenStatus')
    output_fieldnames = [s1 for s1 in output.split(',')]
    writer = csv.DictWriter(fptr, fieldnames=output_fieldnames)
    headers = dict( (n,n) for n in output_fieldnames)
    writer.writerow(headers)

    for row in reader:
        markdown_length = len(row['BodyMarkdown'])
        row.pop('BodyMarkdown')
        row['markdown_length'] = markdown_length
        writer.writerow(row)


if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)
