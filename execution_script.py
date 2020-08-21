import os

def generate_command(path, counter):
    s = "python -m unsupervisedqa.generate_synthetic_qa_data " + path + " "
    output = "/outputs/wiki_output_" + str(counter)
    s += output + " --input_file_format \"txt\" --output_file_format \"squad\" "
    s += "--translation_method unmt --use_named_entity_clozes --use_subclause_clozes --use_wh_heuristic --use_custom_processing"
    return s

num_files = 0
counter = 0
listOfFiles = os.listdir("./extracted")
for l in listOfFiles:
    if (l != ".DS_Store"):
        path = os.listdir("./extracted/" + l)
        for file in path:
            counter += 1
            file_path = "./extracted/" + l + "/" + file
            command = generate_command(file_path, counter)
            print('excecuting...')
            os.system(command)
        if (counter % 10 == 0):
            print('=' * 80)
            print('Processed ' + str(counter) + ' files')
            print('=' * 80)
