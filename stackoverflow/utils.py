from __future__ import division

from collections import Counter, defaultdict
import csv
import dateutil
import numpy as np
import pandas as pd


df_converters = {"PostCreationDate": dateutil.parser.parse,
                 "OwnerCreationDate": dateutil.parser.parse}


def update_prior(old_prior,  old_posterior, new_prior):
    evidence_ratio = (old_prior*(1-old_posterior)) / (old_posterior*(1-old_prior))
    new_posterior = new_prior / (new_prior + (1-new_prior)*evidence_ratio)
    return new_posterior


def cap_and_update_priors(old_priors, old_posteriors, new_priors, epsilon):
    old_posteriors = cap_predictions(old_posteriors, epsilon)
    old_priors = np.kron(np.ones((np.size(old_posteriors, 0), 1)), old_priors)
    new_priors = np.kron(np.ones((np.size(old_posteriors, 0), 1)), new_priors)
    evidence_ratio = (old_priors*(1-old_posteriors)) / (old_posteriors*(1-old_priors))
    new_posteriors = new_priors / (new_priors + (1-new_priors)*evidence_ratio)
    new_posteriors = cap_predictions(new_posteriors, epsilon)
    return new_posteriors


def cap_predictions(probs, epsilon):
    probs[probs>1-epsilon] = 1-epsilon
    probs[probs<epsilon] = epsilon
    row_sums = probs.sum(axis=1)
    probs = probs / row_sums[:, np.newaxis]
    return probs


def get_priors(file_name):
    closed_reasons = [r[14] for r in get_reader(file_name)]
    closed_reason_counts = Counter(closed_reasons)
    reasons = sorted(closed_reason_counts.keys())
    total = len(closed_reasons)
    priors = [closed_reason_counts[reason]/total for reason in reasons]
    return priors


def get_reader(file_name):
    reader = csv.reader(open(file_name, 'rb'))
    reader.next()
    return reader


def write_submission(file_name, predictions):
    writer = csv.writer(open(file_name, "wb"), lineterminator="\n")
    writer.writerows(predictions)


def user_age(data):
    df = pd.DataFrame.from_dict({"UserAge": (data["PostCreationDate"]
            - data["OwnerCreationDate"]).apply(lambda x: x.total_seconds())})
    num_indices = len(df.index)

    for index in xrange(num_indices):
        days = df['UserAge'][index] / 86400.0
        if days < 1:
            df['UserAge'][index] = 0
            continue
        if (1 < days < 7):
            df['UserAge'][index] = 0
            continue
        df['UserAge'][index] = 2

    return df


def get_content_length(data):
    return data['BodyMarkdown'].apply(len)


def markdown_length(data):
    return data['markdown_length']


def open_status(data):
    """docstring for open_status"""
    return data['OpenStatus']


def num_tags(data):

    num_tags_as_dict = defaultdict(int)
    for index in xrange(1,6):
        tag = 'Tag' + str(index)
        rows = [(index, data[tag][index]) for index in xrange(0, len(data.index))]
        for r in rows:
            if not pd.isnull(r[1]):
                num_tags_as_dict[r[0]] += 1


    s1 = pd.Series(data=num_tags_as_dict, index=data.index)
    s1.name = 'num_tags'
    df = pd.DataFrame(s1)
    return df


def _get_reputation_mapping(reputation):

    if reputation <= 0:
        return 0
    if ( 0 < reputation <= 100):
        return 1
    if ( 100 < reputation <= 500):
        return 2
    if ( 1000 < reputation <= 5000):
        return 3 
    return 4


def _get_answere_questions_mapping(undeleted_answer_count):

    if undeleted_answer_count <= 0:
        return 0
    if ( 0 < undeleted_answer_count <= 5):
        return 1
    if ( 100 < undeleted_answer_count <= 10):
        return 2
    if ( 10 < undeleted_answer_count <= 100):
        return 3 
    if ( 100 < undeleted_answer_count <= 500):
        return 4 
    return 5


def simplified_reputation(data):
    reputation_as_dict = defaultdict(int)

    num_indices = len(data.index)

    for index in xrange(num_indices):
        reputation = int(data['ReputationAtPostCreation'][index])
        reputation_as_dict[index] = _get_reputation_mapping(reputation)

    s1 = pd.Series(data=reputation_as_dict, index=data.index)
    s1.name = 'reputation'
    df = pd.DataFrame(s1)
    return df


def simplified_undeleted_answer_count(data):
    undeleted_answer_count_as_dict = defaultdict(int)

    num_indices = len(data.index)

    for index in xrange(num_indices):
        undeleted_answer_count = int(data['OwnerUndeletedAnswerCountAtPostTime'][index])
        undeleted_answer_count_as_dict[index] = _get_answere_questions_mapping(undeleted_answer_count)

    s1 = pd.Series(data=undeleted_answer_count_as_dict, index=data.index)
    s1.name = 'undeleted_answer_count'
    df = pd.DataFrame(s1)
    return df
