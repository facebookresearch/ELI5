# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

"""
Computes ROUGE given one file of hypotheses and one file of references.
Lines should be aligned (e.g. hypothesis 1 corresponds to reference 1)
"""

from rouge import Rouge
from nltk import PorterStemmer
import argparse

stemmer = PorterStemmer()

parser = argparse.ArgumentParser(description='Calculate ROUGE given reference and hypothesis files')
parser.add_argument("--hypotheses", help='path to the hypotheses. One hypothesis per line.', metavar="FILE")
parser.add_argument("--references", help='path to the references. One hypothesis per line.', metavar="FILE")
args = parser.parse_args()

def open_data(hypotheses, references):
	with open(hypotheses) as f:
		hypoth_data = f.readlines()
	with open(references) as f:
		ref_data = f.readlines()
	assert(len(ref_data) == len(hypoth_data))
	return hypoth_data, ref_data

def prepare(hypotheses, references):
	hypoth = [" ".join([stemmer.stem(i) for i in line.split()]) for line in hypotheses]
	ref = [" ".join([stemmer.stem(i) for i in line.split()]) for line in references]
	return hypoth, ref

def rouge_calculation(hypotheses, references):
	rouge = Rouge()
	scores = rouge.get_scores(hypotheses, references, avg=True)
	print(scores)
	return

if __name__ == "__main__":
	hypotheses, references = open_data(args.hypotheses, args.references)
	clean_hypoth, clean_ref = prepare(hypotheses, references)
	rouge_calculation(clean_hypoth, clean_ref)
