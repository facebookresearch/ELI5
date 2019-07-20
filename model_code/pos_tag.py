# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

"""
Reads the first 2000 examples of valid and test and tags them as noun, verb, adjective.
It's set to 2000 because this is what we used in the paper.
Outputs 6 files: valid/test source/target for each part of speech
The word to predict is the last word of the target

Note: If you do not have spacy models downloaded, you will need to:
python -m spacy download en_core_web_lg
"""

import spacy
import argparse

parser = argparse.ArgumentParser(description='Generate nouns, verbs, adjectives one-word-fill task')
parser.add_argument('--input', help='path to the location of the target and source files')
parser.add_argument('--output', help='path to the location to write the output')
parser.add_argument('--dataset-name', help='name of the source/target pair, e.g. "q_d"')
args = parser.parse_args()

nlp = spacy.load('en_core_web_lg')

def open_files(input_location, dataset, dataset_name):
	with open(input_location + "/" + dataset + "." + dataset_name + "_target") as f:
		target = f.readlines()[0:2000]

	with open(input_location + "/" + dataset + "." + dataset_name + "_source") as f:
		source = f.readlines()[0:2000]
	return target, source

def file_writer(path, lines):
	with open(path, "w") as o:
		for line in lines:
			o.write(line + "\n")
	return

def tag_and_write(tgt, src, output, dataset, dataset_name):
	verbs = []
	nouns = []
	adj = []
	matching_verbs = []
	matching_nouns = []
	matching_adj = []
	for num, line in enumerate(tgt):
		doc = nlp(line.strip())
		for i, token in enumerate(doc):
			if token.pos_ == "VERB":
				verbs.append(" ".join(line.split()[0:i+1]))
				matching_verbs.append(src[num].strip())
			if token.pos_ == "NOUN":
				nouns.append(" ".join(line.split()[0:i+1]))
				matching_nouns.append(src[num].strip())
			if token.pos_ == "ADJ":
				adj.append(" ".join(line.split()[0:i+1]))
				matching_adj.append(src[num].strip())
	file_writer(output + "/" + dataset + "." + dataset_name + "_verb_source", matching_verbs)
	file_writer(output + "/" + dataset + "." + dataset_name + "_noun_source", matching_nouns)
	file_writer(output + "/" + dataset + "." + dataset_name + "_adj_source", matching_adj)
	file_writer(output + "/" + dataset + "." + dataset_name + "_verb_target", verbs)
	file_writer(output + "/" + dataset + "." + dataset_name + "_noun_target", nouns)
	file_writer(output + "/" + dataset + "." + dataset_name + "_adj_target", adj)
	return


if __name__ == "__main__":
	valid_target, valid_source = open_files(args.input, "valid", args.dataset_name)
	test_target, test_source = open_files(args.input, "test", args.dataset_name)
	tag_and_write(valid_target, valid_source, args.output, "valid", args.dataset_name)
	tag_and_write(test_target, test_source, args.output, "test", args.dataset_name)
