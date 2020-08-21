# Copyright (c) 2019-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
# Script modified by Liubov Nikolenko to generate synthetic unaswerable questions. 
"""
Main interface to user
"""
import json
import attr
import argparse
import os
from .data_classes import Paragraph
from .configs import UNMT_MODEL_SENTENCE_NE, \
    UNMT_MODEL_SENTENCE_NP, UNMT_MODEL_SUBCLAUSE_NE, \
    UNMT_MODEL_SUBCLAUSE_NE_WH_HEURISTIC
from .parsers_and_writers import parse_paragraphs_from_jsonl, parse_paragraphs_from_txt, dump_clozes, clozes2squadformat
from .generate_clozes import generate_clozes_from_paragraph, named_entity_answer_generator as ne_answer_gen, \
    noun_phrase_answer_generator as np_answer_gen, is_appropriate_squad_datapoint
from .constituency_parsing import get_constituency_parsed_clozes, shorten_cloze
from .unmt_translation import get_unmt_questions_for_clozes
from .baseline_translators import identity_translation, noisy_cloze_translation


def _check_args(args):
    if args.use_wh_heuristic:
        assert args.use_named_entity_clozes, \
            'Wh heuristics can only be used in conjunction with Named Entity Answers, Pass --use_named_entity_clozes'

    if args.use_subclause_clozes:
        assert args.use_named_entity_clozes, \
            "Subclause clozes can only be used in conjunction with Named Entity Answers Pass --use_named_entity_clozes"

    assert os.path.exists(args.input_file), f"Input File: {args.input_file} does not exist"

    for o in args.output_file_formats.split(','):
        assert o in {'jsonl', 'squad'},\
            f"Unrecognised output file format requested: {o}, must be one of ['jsonl', 'squad'] "
        if o == 'jsonl':
            p = args.output_file + '.unsupervised_qa.jsonl'
        else:
            p = args.output_file + '.squad.json'
        assert not os.path.exists(p), f'Output file {p} already exists, terminating...'

    # check for downloaded models before allowing unmt
    def _assert_exists(path):
        assert os.path.exists(path), \
            f"Requested model could not be found at {path}, download it using `download_models.sh`"

    if args.translation_method == 'unmt':
        if args.use_subclause_clozes:
            if args.use_wh_heuristic:
                _assert_exists(UNMT_MODEL_SUBCLAUSE_NE_WH_HEURISTIC)
            else:
                _assert_exists(UNMT_MODEL_SUBCLAUSE_NE)
        elif args.use_named_entity_clozes:
            _assert_exists(UNMT_MODEL_SENTENCE_NE)
        else:
            _assert_exists(UNMT_MODEL_SENTENCE_NP)


def get_questions_for_clozes(clozes,
                             subclause_clozes,
                             ne_answers,
                             wh_heuristic,
                             translation_method):

    if translation_method == 'identity':
        clozes_with_questions = [attr.evolve(c, question_text=identity_translation(c, wh_heuristic)) for c in clozes]

    elif translation_method == 'noisy_cloze':
        clozes_with_questions = [attr.evolve(c, question_text=noisy_cloze_translation(c, wh_heuristic)) for c in clozes]

    elif translation_method == 'unmt':
        clozes_with_questions = get_unmt_questions_for_clozes(
            clozes, subclause_clozes,  ne_answers,  wh_heuristic)
    else:
        raise Exception(f'Unrecognised translation type: {translation_method}')

    return clozes_with_questions


def generate_synthetic_training_data(args):
    _check_args(args)

    with open(args.input_file) as f:
        if args.input_file_format == 'jsonl':
            paragraphs = parse_paragraphs_from_jsonl(f)
        else:
            paragraphs = parse_paragraphs_from_txt(f)
        paragraphs = list(paragraphs)
        print(paragraphs)

    print('=' * 50)
    print(f'Parsed {len(paragraphs)} paragraphs from {args.input_file}')
    print('=' * 50)

    # Create clozes:
    answer_generator = ne_answer_gen if args.use_named_entity_clozes else np_answer_gen
    clozes = [c for p in paragraphs for c in generate_clozes_from_paragraph(p, answer_generator)]

    if args.use_subclause_clozes:
        syntax_clozes = get_constituency_parsed_clozes(clozes)
        clozes = [short_cloze for cloze in syntax_clozes for short_cloze in shorten_cloze(cloze)]
        #clozes = list(get_constituency_parsed_clozes(clozes))
    print('=' * 50)
    print(f'{len(clozes)} Cloze questions extracted for Translation')
    print('=' * 50)
    # translate clozes to questions
    clozes_with_questions = get_questions_for_clozes(
        clozes,
        args.use_subclause_clozes,
        args.use_named_entity_clozes,
        args.use_wh_heuristic,
        args.translation_method
    )

    # filter generations
    clozes_with_questions = [
        c for c in clozes_with_questions
        if is_appropriate_squad_datapoint(c.question_text, c.answer_text, c.paragraph.text)
    ]

    # Dump the synthetic training data
    print('=' * 50)
    print('Dumping results')
    print('=' * 50)
    for o in args.output_file_formats.split(','):
        if o == 'jsonl':
            with open(args.output_file + '.unsupervised_qa.jsonl', 'w') as f:
                dump_clozes(clozes_with_questions, f)
            print(f"Exported {len(clozes_with_questions)} instances to {args.output_file + '.unsupervised_qa.jsonl'}")

        elif o == 'squad':
            with open(args.output_file + '.squad.json', 'w') as f:
                clozes2squadformat(clozes_with_questions, f)
            print(f"Exported {len(clozes_with_questions)} instances to {args.output_file + '.squad.json'}")

    print('=' * 50)
    print('Complete')
    print('=' * 50)

def extract_id(line):
    header = {}
    line_list = line.split(' ')
    for entry in line_list:
        if ('=' in entry):
            entry_list = entry.split('=')
            if (entry_list[0] == 'id'):
                return entry_list[1]

def clozes2squadparagraph(clozes):
    assert all([c.question_text is not None for c in clozes]), 'Translate these clozes first, some dont have questions'
    data_list = []
    cloze_dict = {}
    for cloze in clozes:
        if (cloze.paragraph.text not in cloze_dict):
            cloze_dict[cloze.paragraph.text] = []
        cloze_dict[cloze.paragraph.text].append({'question': cloze.question_text, 'id': cloze.cloze_id, 'is_impossible': False, 'answers': [{'text': cloze.answer_text, 'answer_start': cloze.answer_start}]})
    #data = {'context': cloze.parag
    for par, qas in cloze_dict.items():
        data_list.append({'context': par, 'qas': qas})
    return data_list

def custom_data_generation(args):
    f = open(args.input_file)
    curr_id = None
    next_is_title = False
    squad = {}
    articles = {}
    title = None
    paragraphs = []
    squad["version"] = "v2.0"
    squad["data"] = []
    answer_generator = ne_answer_gen if args.use_named_entity_clozes else np_answer_gen
    num_articles = 0
    for line in f.readlines():
        if (len(line.strip()) > 0 and line.strip().lower() != '</doc>'):
            if ('<doc' in line and '>' in line and 'id=' in line):
                num_articles += 1
                if (num_articles > 3):
                    break
                curr_id = extract_id(line)
                next_is_title = True
            elif (next_is_title):
                title = curr_id + "_" + line.strip()
                next_is_title = False
                articles[title] = []
            else:
                articles[title].append(Paragraph(paragraph_id=123, text=line.strip()))
    print(len(articles.keys()))
    for title, paragraphs in articles.items():
        paragraphs_truncated = paragraphs[:25]
        if (len(paragraphs) > 0):
            d = {}
            d["title"] = "_".join(title.split(' '))
            d["paragraphs"] = []
            clozes = [c for p in paragraphs_truncated for c in generate_clozes_from_paragraph(p, answer_generator)]
            if args.use_subclause_clozes:
                syntax_clozes = get_constituency_parsed_clozes(clozes)
                clozes = [short_cloze for cloze in syntax_clozes for short_cloze in shorten_cloze(cloze)]
                #clozes = list(get_constituency_parsed_clozes(clozes))
            # translate clozes to questions
            clozes_with_questions = get_questions_for_clozes(clozes, args.use_subclause_clozes, args.use_named_entity_clozes, args.use_wh_heuristic, args.translation_method)
            # filter generations
            clozes_with_questions = [ c for c in clozes_with_questions if is_appropriate_squad_datapoint(c.question_text, c.answer_text, c.paragraph.text)]
            d["paragraphs"] += clozes2squadparagraph(clozes_with_questions)
            squad["data"].append(d)

    print('Making a dump')
    json.dump(squad, open(args.output_file + ".json", 'w'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate synthetic training data for extractive QA tasks without supervision')
    parser.add_argument("input_file", type=str,
                        help="input file, see readme for formatting info")
    parser.add_argument("output_file", type=str,
                        help="Path to write generated data to, see readme for formatting info")
    parser.add_argument("--input_file_format", type=str, default='txt', choices=['txt', 'jsonl'],
                        help="input file format, see readme for more info, default is txt")
    parser.add_argument("--output_file_formats", type=str, default='jsonl,squad',
                        help="comma-seperated list of output file formats, from [jsonl, squad],"
                             " an output file will be created for each format. Default is 'jsonl,squad'")
    parser.add_argument("--translation_method", type=str, default="unmt", choices=['identity', 'noisy_cloze', 'unmt'],
                        help="define the method to generate clozes -- either the Unsupervised NMT method (unmt),"
                             " or the identity  or noisy cloze baseline methods. UNMT is recommended for downstream performance, "
                             " but the noisy_cloze is relatively stong on downstream QA and fast to generate. Default is unmt"
                        )
    parser.add_argument("--use_named_entity_clozes", action='store_true',
                        help="pass this flag to use named entity answer prior instead of noun phrases (recommended for downstream performance) ")
    parser.add_argument('--use_subclause_clozes', action='store_true',
                        help="pass this flag to shorten clozes with constituency parsing instead of using sentence boundaries (recommended for downstream performance)")
    parser.add_argument('--use_wh_heuristic', action='store_true',
                        help="pass this flag to use the wh-word heuristic (recommended for downstream performance). Only compatable with named entity clozes")
    parser.add_argument('--use_custom_processing', action='store_true', help='use custom parsing for CS224N project')
    args = parser.parse_args()
    if (not args.use_custom_processing):
       generate_synthetic_training_data(args)
    else:
       custom_data_generation(args)
