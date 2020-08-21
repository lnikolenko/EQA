import json
import random
def add_false_impossible(qa):
    qa["is_impossible"] = False
    return qa
def add_true_impossible_remove_answers(qa):
    qa["is_impossible"] = True
    qa["answers"] = []
    qa["id"] += "deadcoffee"
    return qa

def generate_indicies(taken, curr_index, length):
    res = []
    for i in range(length):
        if (i != curr_index and i not in taken):
            res.append(i)
    return res
def shuffle_list(l):
    new_list = [None] * len(l)
    taken = set()
    for i in range(len(l)):
        indicies = generate_indicies(taken, i, len(l))
        if (len(indicies) > 0):
            index = random.choice(indicies)
            taken.add(index)
            new_list[index] = l[i]
    new_list = list(filter(lambda x: x is not None, new_list))
    return new_list


def get_num_questions(file_path):
    f = open(file_path)
    total_questions = 0
    impossible_questions = 0
    data = json.load(f)
    f = open(file_path)
    for datum in data['data']:
        for par in datum['paragraphs']:
            qas = par['qas']
            total_questions += len(qas)
            for q in qas:
                if (q['is_impossible']):
                    impossible_questions += 1
    print(impossible_questions)
    return total_questions

NUM_QUESTIONS_SQUAD = 130319
NUM_QUESTIONS_UNSUPERVISED_QA = 3915498
SQUAD_TRAIN_PATH = './data/train-v2.0.json'
UNSUPERVISED_QA_TRAIN_PATH = './unsupervised_qa_data/unsupervised_qa_train.json'
def generate_splits(percent, is_supervised, out_name=None, questions_to_generate=None):
    """
    This function samples questions from either SQuAD or computer-generated dataset.

    @param percent - percent of the data you want to sampple (e.g. 25, 50, ect.)
    @param is_supervised - boolean flag to sample from SQuAD(True) or unsupervised(False) data
    @param out_name [default=None] - if specified it outputs the data into the json file with the specified name.
    Otherwise, the function returns a dictionary object containing the sampled data.
    @param questions_to_generate [default=None] - if specified, then @param percent is ignored and the function samples
    questions_to_generate amount of questions.

    @return None if out name is specified or a dictionary object with sampled data.
    """
    if (is_supervised):
        file_path = SQUAD_TRAIN_PATH
        num_questions = int(NUM_QUESTIONS_SQUAD * 0.01 * percent)
    else:
        file_path = UNSUPERVISED_QA_TRAIN_PATH
        num_questions = int(NUM_QUESTIONS_UNSUPERVISED_QA * 0.01 * percent)
    if (questions_to_generate is not None):
        num_questions = questions_to_generate
    f = open(file_path)
    data = json.load(f)
    length = 0
    generated_data = {}
    generated_data["version"] = "v2.0"
    generated_data["data"] = []
    for datum in data['data']:
        d = {}
        d["title"] = datum["title"]
        d["paragraphs"] = []
        generated_data["data"].append(d)
        for par in datum['paragraphs']:
            qas = par['qas']
            if (not is_supervised):
                qas = list(map(lambda x: add_false_impossible(x), qas))
            d1 = {}
            d["paragraphs"].append(d1)
            d1["context"] = par["context"]
            d1["qas"] = []
            l_qas = len(qas)
            if (length + l_qas < num_questions):
                length += l_qas
                d1["qas"] += qas
            else:
                num_qas = num_questions - length
                d1["qas"] += qas[:num_qas]
                if (out_name is not None):
                    json.dump(generated_data, open(out_name,"w"))
                    return
                return generated_data
def generate_mixed_data(num_questions, percent_squad, out_name):
    """
    This function combines SQuAD and unsupervised data in the proportions specified and
    writes the result in <out_name>.json

    @param num_questions - the *total* number of questions the will be generated
    @param precent_squad - percent of SQuAD questions that will be in the sampled data
    @param out_name - outputs the data into the json file with the specified name.
    """
    num_questions_squad = int(num_questions * 0.01 * percent_squad)
    d_supervised = generate_splits(percent_squad, True, questions_to_generate=num_questions_squad)
    d_unsupervised = generate_splits(100 - percent_squad, False, questions_to_generate=num_questions - num_questions_squad)
    for datum in d_unsupervised['data']:
        d_supervised['data'].append(datum)
    json.dump(d_supervised, open(out_name, "w"))
    return
"""
def generate_unanswerable_questions(is_supervised, num_questions):
    if (is_supervised):
        file_path = SQUAD_TRAIN_PATH
    else:
        file_path = UNSUPERVISED_QA_TRAIN_PATH

    f = open(file_path)
    data = json.load(f)
    length = 0
    generated_data = {}
    generated_data["version"] = "v2.0"
    generated_data["data"] = []
    print('hi')
    for datum in data['data']:
        paragraphs = datum['paragraphs']
        if (len(paragraphs) > 1):
            context_list = []
            for paragraph in paragraphs:
                context_list.append(paragraph['context'])
                paragraph["context"] = None
"""



#shuffle
"""
f = open("./squad_25_base_for_unanswerable.json")
length = 0
data = json.load(f)
generated_data = {}
generated_data["version"] = "v2.0"
generated_data["data"] = []
for datum in data['data']:
    if (len(datum['paragraphs']) > 1):
        d = {}
        d["title"] = datum["title"]
        d["paragraphs"] = []
        generated_data["data"].append(d)
        context_list = list(map(lambda x: x["context"], datum['paragraphs']))
        shuffled_context_list = shuffle_list(context_list)
        while(len(shuffled_context_list) < len(context_list)):
            shuffled_context_list = shuffle_list(context_list)
            print('shuffling')
        for i, par in enumerate(datum['paragraphs']):
            qas = par['qas']
            d1 = {}
            d["paragraphs"].append(d1)
            d1["context"] = shuffled_context_list[i]
            d1["qas"] = list(map(lambda x: add_true_impossible_remove_answers(x), qas))
json.dump(generated_data, open("generated_unanswerable.json","w"))
f.close()
"""
#generate_splits(20, True, "generated_20.json")
#print(get_num_questions("./data/train-v2.0.json"))
"""
d_supervised = generate_splits(100, True, questions_to_generate=26063)
d_unsupervised = generate_splits(100, False, questions_to_generate=391549)
for datum in d_unsupervised['data']:
    d_supervised['data'].append(datum)
json.dump(d_supervised, open("experiment_1.json", "w"))
"""
"""
x = 76818
y = 391549
d_supervised = generate_splits(100, True, questions_to_generate=26063)
d_unsupervised = generate_splits(100, False, questions_to_generate=(x + y))
for datum in d_unsupervised['data']:
    d_supervised['data'].append(datum)
json.dump(d_supervised, open("experiment_2-1.json", "w"))

f1 = open("generated_wiki_unanswerable_new.json")
data = json.load(f1)
d_supervised = generate_splits(100, True, questions_to_generate=26063)
d_unsupervised = generate_splits(100, False, questions_to_generate=391549)
for datum in d_unsupervised['data']:
    d_supervised['data'].append(datum)
for datum in data['data']:
    d_supervised['data'].append(datum)
print(len(d_supervised['data']))
json.dump(d_supervised, open("experiment_2-2.json", "w"))
"""
"""
x = 76818
y = 391549
d_supervised = generate_splits(100, True, questions_to_generate=26063)
d_unsupervised = generate_splits(100, False, questions_to_generate=x)
for datum in d_unsupervised['data']:
    d_supervised['data'].append(datum)
json.dump(d_supervised, open("experiment_3-1.json", "w"))

f2 = open("generated_wiki_unanswerable_new.json")
data = json.load(f2)
f2.close()
d_supervised = generate_splits(100, True, questions_to_generate=26063)
for datum in data['data']:
    d_supervised['data'].append(datum)
print(len(d_supervised['data']))
json.dump(d_supervised, open("experiment_1-2.json", "w"))
"""
"""

x = 76818
y = 391549
y1 = 15000
f4 = open("generated_wiki_unanswerable_new.json")
data = json.load(f4)
f4.close()
d_supervised = generate_splits(100, True, questions_to_generate=26063)
d_unsupervised = generate_splits(100, False, questions_to_generate=(y - x))
for datum in d_unsupervised['data']:
    d_supervised['data'].append(datum)
for datum in data['data']:
    d_supervised['data'].append(datum)
print(len(d_supervised['data']))
json.dump(d_supervised, open("experiment_2.json", "w"))
"""
"""
x = 76818
y1 = 120000
f4 = open("generated_wiki_unanswerable_new.json")
data = json.load(f4)
f4.close()
d_supervised = generate_splits(100, True, questions_to_generate=26063)
d_unsupervised = generate_splits(100, False, questions_to_generate=y1)
for datum in d_unsupervised['data']:
    d_supervised['data'].append(datum)
for datum in data['data']:
    d_supervised['data'].append(datum)
json.dump(d_supervised, open("experiment_2_3.json", "w"))
"""
d_supervised = generate_splits(100, True, questions_to_generate=130319)
d_unsupervised = generate_splits(100, False, questions_to_generate=1000000)
for datum in d_unsupervised['data']:
    d_supervised['data'].append(datum)
print(len(d_supervised['data']))
json.dump(d_supervised, open("experiment_human_and_synthetic_large.json", "w"))


#d_supervised = generate_splits(100, True, questions_to_generate=26063)
#print(d_supervised['data'][0]['title'])

#generate_mixed_data(228059, 14, "mixed_150_synthetic_data.json")
#generate_splits(100, True,  out_name='test_un.json', questions_to_generate=20)
#generate_splits(100, True, out_name='u_test2.json', questions_to_generate=10)
#print(get_num_questions('experiment_2_3.json'))
