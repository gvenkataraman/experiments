"""
Something very very basic
"""
from __future__ import division

import dateutil
import pandas as pd
from sklearn import tree
from sklearn import cross_validation
import sys

import utils


feature_mapping = {
    'content_length': utils.get_content_length,
    'num_tags': utils.num_tags,
    'reputation': utils.simplified_reputation,
    'undeleted_answer_count': utils.simplified_undeleted_answer_count,
    'open_status': utils.open_status,
    'user_age': utils.user_age,
    'markdown_length': utils.markdown_length,
}

features = ('num_tags', 
            'reputation', 'undeleted_answer_count',
            'user_age', 'markdown_length')


def convert_datetime(data):
    num_indices = len(data.index)
    for index in xrange(num_indices):
        data['PostCreationDate'][index] = (
            dateutil.parser.parse(data['PostCreationDate'][index]))
        data['OwnerCreationDate'][index] = (
            dateutil.parser.parse(data['OwnerCreationDate'][index]))


def get_dataframe(data):
    convert_datetime(data)
    required_features = pd.DataFrame(index=data.index)
    for feature in features:
        required_features = (required_features.join(
            feature_mapping[feature](data)))
    return required_features


def main(train_file, test_file, output_file, full_train_file):
    data = pd.read_csv(train_file)
    
    required_features = get_dataframe(data)
    clf = tree.DecisionTreeClassifier()
    fit = clf.fit(required_features, data['OpenStatus'])
    out = tree.export_graphviz(fit, out_file='tree.out')
    out.close()

    test_data = pd.read_csv(test_file)
    test_features = get_dataframe(test_data)
    print 'Predicting probabilities'
    probs = fit.predict_proba(test_features)

    print 'Correction probabilities'
    new_priors = utils.get_priors(full_train_file)
    old_priors = utils.get_priors(train_file)
    probs = utils.cap_and_update_priors(old_priors, probs, new_priors, 0.001)

    print 'Writing file'

    utils.write_submission(output_file, probs)
#    scores = cross_validation.cross_val_score(
#        clf, 
#        required_features,
#        data['OpenStatus'],
#    )
#    print "Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() / 2)


if __name__ == '__main__':
    """
    python basic.py <input_file> <test_file> <output_file>
    """
    main(
        train_file=sys.argv[1],
        full_train_file=sys.argv[2],
        test_file=sys.argv[3],
        output_file=sys.argv[4],
    )
