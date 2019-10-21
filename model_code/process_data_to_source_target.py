# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

"""
Sample script to process the dataset into source/target files.
"""

import json
import argparse
import random
import numpy as np

parser = argparse.ArgumentParser(description='Process json file to source/target files')
parser.add_argument('--input', help='path to the location of the json files created by the data extraction scripts')
parser.add_argument('--output', help='path to the location to write the output')
args = parser.parse_args()

def read_data(json_input):
    with open(json_input) as f:
        data = json.load(f)
    questions = []
    answers = []
    supports = []
    for d in data:
        questions.append(d["question"].strip())
        answers.append(d["answer"].strip())
        supports.append(d["document"].strip())
    assert(len(questions) == len(answers) == len(supports))
    return questions, answers, supports

def write_output(filename, lines):
    with open(filename, "w") as o:
        for line in lines:
            o.write(line + "\n")

def form_source_target(questions, documents, answers, output, dataset_name):
    """
    constructs question + document to answer, question to answer
    """
    qd_source = [questions[i] + " " + documents[i] for i, value in enumerate(documents)]
    write_output(output + "/" + dataset_name + ".qd_source", qd_source)
    write_output(output + "/" + dataset_name + ".qd_target", answers)
    write_output(output + "/" + dataset_name + ".q_source", questions)
    write_output(output + "/" + dataset_name + ".q_target", answers)
    return

def form_multitask_source_target(questions, documents, answers, output, dataset_name, valid=False):
    """
    constructs question + document to answer, question to answer with multitasking
    """
    mask_source = []
    mask_target = []
    if not valid:
        multitask_source, multitask_target = form_multitask(questions, documents, answers)

        for doc in documents:
            ms, mt = masking_tokens(doc)
            mask_source.extend(ms)
            mask_target.extend(mt)
    else:
        multitask_source, multitask_target = form_multitask_valid(questions, documents, answers)

    qd_source = multitask_source + mask_source
    targets = multitask_target + mask_target
    assert(len(qd_source) == len(targets))

    combined = list(zip(qd_source, targets))
    random.shuffle(combined)
    sources, targets = zip(*combined)

    write_output(output + "/" + dataset_name + ".multitask_source", sources)
    write_output(output + "/" + dataset_name + ".multitask_target", targets)
    return

def form_multitask(questions, documents, answers):
    source = []
    target = []
    for i, question in enumerate(questions):
        # language modeling tasks
        source.append("<lm_qda>")
        target.append("<startQuestion> " + question + " " + documents[i] + " <startAnswer> " + answers[i])
        source.append("<lm_qd>")
        target.append("<startQuestion> " + question + " " + documents[i])
        source.append("<lm_a>")
        target.append(answers[i])
        source.append("<lm_q>")
        target.append(question)
        source.append("<lm_d>")
        target.append(documents[i])
        # seq2seq tasks
        source.append("<s2s_q_da> <startQuestion> " + question)
        target.append(documents[i] + " <startAnswer> " + answers[i])
        source.append("<s2s_qd_a> <startQuestion> " + question + " " + documents[i])
        target.append(answers[i])
        source.append("<s2s_q_a> <startQuestion> " + question)
        target.append(answers[i])
        source.append("<s2s_q_d> <startQuestion> " + question)
        target.append(documents[i])
    return source, target

def form_multitask_valid(questions, documents, answers):
    """
    At testing time, only the standard Q + D -> A task is conducted
    """
    source = []
    target = []
    for i, question in enumerate(questions):
        source.append("<s2s_qd_a> <startQuestion> " + question + documents[i])
        target.append(answers[i])
    return source, target

def masking_tokens(document):
    source = []
    target = []
    to_replace = document.split()
    mask_answers = []
    k = int(len(to_replace) * 0.15)
    indices = sorted(random.sample([i for i in range(len(to_replace))], k))
    for j in indices:
        mask = np.random.uniform(0, 1, 1) < 0.8
        if mask:
            mask_answers.append(to_replace[j])
            to_replace[j] = "[MASK]"
        else:
            mask_answers.append(to_replace[j])
    source.append("<masking> " + " ".join(to_replace))
    target.append(" ".join(mask_answers))
    return source, target

if __name__ == "__main__":
	train_q, train_a, train_d = read_data(args.input + "/explainlikeimfive_train.json")
	form_source_target(train_q, train_d, train_a, args.output, "train")
	valid_q, valid_a, valid_d = read_data(args.input + "/explainlikeimfive_valid.json")
	form_source_target(valid_q, valid_d, valid_a, args.output, "valid")
	test_q, test_a, test_d = read_data(args.input + "/explainlikeimfive_test.json")
	form_source_target(test_q, test_d, test_a, args.output, "test")

	train_q, train_a, train_d = read_data(args.input + "/explainlikeimfive_train.json")
	form_multitask_source_target(train_q, train_d, train_a, args.output, "train")
	valid_q, valid_a, valid_d = read_data(args.input + "/explainlikeimfive_valid.json")
	form_multitask_source_target(valid_q, valid_d, valid_a, args.output, "valid", True)
	test_q, test_a, test_d = read_data(args.input + "/explainlikeimfive_test.json")
	form_multitask_source_target(test_q, test_d, test_a, args.output, "test", True)
