# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

import json
import sys

from glob import glob

name    = sys.argv[1]
n_sel   = int(sys.argv[2])
n_cont  = int(sys.argv[3])

data_split  = json.load(open('pre_computed/%s_split_keys.json' % (name,)))
qda_list    = []
for f_name in glob('processed_data/%s_selected_slice_*_ns_%d_%d.json' % (name, n_sel, n_cont)):
    qda_list    += json.load(open(f_name))

qda_dict    = dict([(dct['id'], dct) for dct in qda_list])
for spl in ['train', 'valid', 'test']:
    split_list  = [qda_dict[k] for k in data_split[spl] if k in qda_dict]
    json.dump(split_list, open('processed_data/%s_%s.json' % (name, spl), 'w'))
