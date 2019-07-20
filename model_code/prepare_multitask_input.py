# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

"""
Prepares input for multi-task pretrained model
"""
import argparse

parser = argparse.ArgumentParser(description='Process text file to file readable by the multi-task pretrained model')
parser.add_argument('--input', help='path to the location of the input text file')
parser.add_argument('--output', help='path to the location to write the output')
args = parser.parse_args()

with open(args.input) as f:
    data = f.readlines()

output_data = ["<s2s_qd_a> <startQuestion> " + i for i in data]

with open(args.output, "w") as f:
    for line in output_data:
        f.write(line)
