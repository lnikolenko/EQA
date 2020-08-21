# When in Doubt, Ask: Generating Answerable and UnanswerableQuestions, Unsupervised
This repo contains the scripts for generating synthetic unanswerable questions. 

The repo contains the following scripts:

- `generate_training_data.py` - a script to generate a dataset with a certain ratio of human-labled and synthetic data in it. 
- `generate_synthetic_qa_data.py` - a file from https://github.com/lnikolenko/UnsupervisedQA which I modified to accomondate for unanswerable question generation. 
- `execution_script.py` - a driver scripts with checkpoint and error handling logic
- `combine_synthetic_questions.py` - a script which shuffles the paragraphs and makes questions unanswerable. This is the last step in unaswerable question generation pipeline, can be done locally. 
