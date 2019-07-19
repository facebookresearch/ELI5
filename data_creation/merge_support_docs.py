# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

import sys

from data_utils import *

name    = sys.argv[1]
ca      = sys.argv[2]

if ca == 'finalize':
    num_slice   = 0
    docs        = []
    for i in range(10):
        docs    += json.load(open(pjoin('processed_data/collected_docs', name, '%d.json' % (i,))))
        while len(docs) > 3000:
            print('writing slice', num_slice, name)
            json.dump(docs[:3000], open(pjoin('processed_data/collected_docs', name, 'slice_%d.json' % num_slice), 'w'))
            docs        = docs[3000:]
            num_slice   += 1
else:
    if ca == '9':
        c_l = ['9', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p']
    elif ca == '0':
        c_l = ['q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    else:
        c_l = [ca]
    merged  = []
    for c in c_l:
        d_name	= pjoin('processed_data/collected_docs', name, c)
        if isdir(d_name):
            merged  += merge_support_docs(d_name)
    if len(merged) > 0:
        json.dump(merged, open(pjoin('processed_data/collected_docs', name, ca) + '.json', 'w'))

