# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

import argparse
import json
import os
import sys

from time import time

from data_utils import *

def select_pars(qa_dct, docs_list, word_freqs, n_sents=100, n_context=3):
    question    = qa_dct['title'][0]
    split_docs  = [sentence_split(doc['text'][0], max_len=64) for doc in docs_list]
    q_ti_dct    = tf_idf_vec(question,
                             word_freqs['title'][0],
                             word_freqs['title'][1])
    split_docs_pre  = [(i, j, sen, tf_idf_vec(sen,
                                              word_freqs['doc'][0],
                                              word_freqs['doc'][1]))
                       for i, doc in enumerate(split_docs) for j, sen in enumerate(doc)]
    split_docs_sc   = [(i, j, tf_idf_dist(q_ti_dct, dct))
                       for k, (i, j, sen, dct) in enumerate(split_docs_pre) if len(sen.split()) >= 4 and sen not in [x[2] for x in split_docs_pre[:k]]]
    split_docs_sort = sorted(split_docs_sc, key=lambda x:x[-1], reverse=True)[:n_sents]
    select_ids      = sorted([(i, j) for i, j, _ in split_docs_sort])
    par_ids     = []
    this_par    = []
    last_seen   = (-1, -1)
    for i, j in select_ids:
        if i > last_seen[0]:
            par_ids     += [this_par]
            this_par    = []
            for k in range(-n_context, n_context+1):
                if j+k >= 0 and j+k < len(split_docs[i]):
                    this_par    += [(i, j+k)]
                    last_seen   = (i, j+k)
        else:
            if j - n_context > last_seen[1] + 1:
                par_ids     += [this_par]
                this_par    = []
            for k in range(-n_context, n_context+1):
                if j+k > last_seen[1] and j+k >= 0 and j+k < len(split_docs[i]):
                    this_par    += [(i, j+k)]
                    last_seen   = (i, j+k)
    par_ids     = par_ids[1:] + [this_par]
    extract_doc = ' <P> '.join([''] + [' '.join([split_docs[i][j] for i, j in par]) for par in par_ids]).strip()
    return extract_doc


def make_example(qa_dct, docs_list, word_freqs, n_sents=100, n_context=3):
    q_id        = qa_dct['id']
    question    = qa_dct['title'][0] + ' --T-- ' + qa_dct['selftext'][0]
    answer      = qa_dct['comments'][0]['body'][0]
    document    = select_pars(qa_dct, docs_list, word_freqs, n_sents, n_context)
    return {'id': q_id,
            'question': question,
            'document': document,
            'answer'  : answer}


def main():
    parser  = argparse.ArgumentParser(description='Gather into train, valid and test')
    parser.add_argument('-sid', '--slice_id', default=0, type=int, metavar='N',
                        help='slice to process')
    parser.add_argument('-ns', '--num_selected', default=15, type=int, metavar='N',
                        help='number of selected passages')
    parser.add_argument('-nc', '--num_context', default=3, type=int, metavar='N',
                        help='number of sentences per passage')
    parser.add_argument('-sr_n', '--subreddit_name', default='explainlikeimfive', type=str,
                        help='subreddit name')
    args        = parser.parse_args()
    reddit      = args.subreddit_name
    n_slice     = args.slice_id
    n_sents     = args.num_selected
    n_context   = args.num_context
    if isfile("processed_data/collected_docs/%s/slices/slice_%d.json" % (reddit, n_slice)):
        print("loading data", reddit, n_slice)
        qa_data     = dict(json.load(open("processed_data/%s_qalist.json" % (reddit,))))
        docs_slice  = json.load(open("processed_data/collected_docs/%s/slices/slice_%d.json" % (reddit, n_slice)))
        word_counts = json.load(open("pre_computed/%s_unigram_counts.json" % (reddit,)))
        qt_freqs    = dict(word_counts['question_title'])
        qt_sum      = sum(qt_freqs.values())
        d_freqs     = dict(word_counts['document'])
        d_sum       = sum(d_freqs.values())
        word_freqs  = {'title': (qt_freqs, qt_sum),
                       'doc'  : (d_freqs, d_sum)}
        print("loaded data")
        processed   = []
        st_time = time()
        for i, (k, docs_list) in enumerate(docs_slice):
            if k in qa_data:
                processed   += [make_example(qa_data[k], docs_list, word_freqs, n_sents, n_context)]
            if i % 10 == 0:
                print(i, len(processed), time() - st_time)
        if not isdir('processed_data/selected_%d_%d' % (n_sents, n_context)):
            os.mkdir('processed_data/selected_%d_%d' % (n_sents, n_context))
        if not isdir('processed_data/selected_%d_%d/%s' % (n_sents, n_context, reddit)):
            os.mkdir('processed_data/selected_%d_%d/%s' % (n_sents, n_context, reddit))
        json.dump(processed, open('processed_data/selected_%d_%d/%s/selected_slice_%d.json' % (n_sents, n_context, reddit, n_slice), 'w'))


if __name__ == '__main__':
    main()
