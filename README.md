# When in Doubt, Ask: Generating Answerable and UnanswerableQuestions, Unsupervised
This repo contains the scripts for generating synthetic unanswerable questions. 

The repo contains the following scripts:

- `generate_training_data.py` - a script to generate a dataset with a certain ratio of human-labled and synthetic data in it. 
- `generate_synthetic_qa_data.py` - a file from https://github.com/lnikolenko/UnsupervisedQA which I modified to accomondate for unanswerable question generation. 
- `execution_script.py` - a driver scripts with checkpoint and error handling logic
- `combine_synthetic_questions.py` - a script which shuffles the paragraphs and makes questions unanswerable. This is the last step in unaswerable question generation pipeline, can be done locally. 

## Generating Unswerable questions

In order to generate unswerable questions do the following:

1. Clone the repo and navigate to the repo folder. 
2. Make a folder `data` and place [SQuAD 2.0](https://rajpurkar.github.io/SQuAD-explorer/) data there. 
3. Make a folder `unsupervised_qa_data` and place [the synthetic answerable questions by Lewis et al.](https://github.com/lnikolenko/UnsupervisedQA) data there.
4. In a different directory clone and install the code from [this](https://github.com/lnikolenko/UnsupervisedQA) repo. 
5. Navigate to the `UnsupervisedQA` folder. 
6. Copy with replacement `generate_synthetic_qa_data.py` from `.../UnsupervisedUnaswerableQuestions`  into `.../UnsupervisedQA/unsupervisedqa`
7. Make `.../UnsupervisedQA/extracted` and `.../UnsupervisedQA/output` folders.
8. Use [WikiExtractor](https://github.com/attardi/wikiextractor) to pre-process a Wikipedia dump and places it in `.../UnsupervisedQA/extracted` directory. 
9. Copy `.../UnsupervisedUnaswerableQuestions/execution_script.py` to `.../UnsupervisedQA/`.
10. `python execution_script.py`
11. After you have generated enough question answer pairs, place the `combine_synthetic_questions.py` in `.../UnsupervisedQA/` and run `python combine_synthetic_questions.py`
12. Use `generate_training_data.py` to partition the data and generate datasets containing both human-labeled and synthetic training examples. 
