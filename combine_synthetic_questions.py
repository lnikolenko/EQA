import os
import json
import random
import copy

PATH = './outputs_2020_1'
out_name = 'wiki_synthetic.json'
squad = {}
squad["version"] = "v2.0"
squad["data"] = []
num_questions = 0
list_of_files = os.listdir(PATH)
for file in list_of_files:
    f = open(PATH + "/" + file)
    data = json.load(f)
    f.close()
    squad["data"] += data["data"]
    for datum in data["data"]:
        for par in datum['paragraphs']:
            num_questions += len(par['qas'])
json.dump(squad, open(out_name,"w"))
print(num_questions)



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
def add_true_impossible_remove_answers(qa):
    qa["is_impossible"] = True
    qa["answers"] = []
    return qa


f = open("./wiki_synthetic.json")
length = 0
data = json.load(f)
generated_data = {}
generated_data["version"] = "v2.0"
generated_data["data"] = []
num_questions = 0
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
            print('shuffing')
        for i, par in enumerate(datum['paragraphs']):
            qas = par['qas']
            d1 = {}
            d["paragraphs"].append(d1)
            d1["context"] = shuffled_context_list[i]
            d1["qas"] = list(map(lambda x: add_true_impossible_remove_answers(x), qas))
            num_questions += len(d1["qas"])
    else:
        pass
        #generated_data["data"].append(datum)
print(num_questions)
json.dump(generated_data, open("generated_wiki_unanswerable_new.json","w"))
f.close()
