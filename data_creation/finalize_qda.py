# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

import argparse
import json
import sys

from glob import glob
from os.path import join as pjoin

def main():
    parser  = argparse.ArgumentParser(description='Gather into train, valid and test')
    parser.add_argument('-ns', '--num_selected', default=15, type=int, metavar='N',
                        help='number of selected passages')
    parser.add_argument('-nc', '--num_context', default=1, type=int, metavar='N',
                        help='number of sentences per passage')
    parser.add_argument('-sr_l', '--subreddit_list', default='["explainlikeimfive"]', type=str,
                        help='subreddit name')
    args    = parser.parse_args()
    n_sel   = args.num_selected
    n_cont  = args.num_context
    for name in json.loads(args.subreddit_list):
        data_split  = json.load(open('pre_computed/%s_split_keys.json' % (name,)))
        qda_list    = []
        for f_name in glob('processed_data/selected/slices/%s_selected_slice_*_ns_%d_%d.json' % (name, n_sel, n_cont)):
            qda_list    += json.load(open(f_name))
        qda_dict    = dict([(dct['id'], dct) for dct in qda_list])
        for spl in ['train', 'valid', 'test']:
            split_list  = [qda_dict[k] for k in data_split[spl] if k in qda_dict]
            json.dump(split_list, open('processed_data/selected/%s_%s.json' % (name, spl), 'w'))


if __name__ == '__main__':
    main()
