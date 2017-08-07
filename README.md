# BART_baseline
Baseline Alone and Social BART task



Task, data processing, and analysis by Jacob Parelman (jmparelman@gmail.com).

# Task Structure
Between subject design.
Group 1: Competitive social trials
Group 0: Non-Competitive social trials

1. Tutorial
2. Belief Distributiosn
3. Alone run, Social (alone interspersed) run X4, Alone run (belief ratings at beginning of every run)
4. Risk Ambiguity Questionnaire
5. Qualtrics Questionnaire

# Subject Data
Data is stored on Blanca, and should not be backed up on Git.

Data that is stored should include
1. Subject Directories
1.1. Subject Tutorial Data
1.2. Subject Task data
1.3. Distribution ratings
1.4. max belief ratings
1.5. Risk Ambiguity data
1.6. single belief ratings

2. Session payment frames
3. Linker files (encrypted)
4. SubjectID Computer# file

# Processing data
To process data simply change the root directory in `Data_processing.py` to your "Data" and "Payment" directories, and change the
output directory to wherever you would like to store all combined data.

After data processing the following files should be made for each subject:
1. combined_[subjectID].csv
2. dists_with_max.csv
3. summarized_data_combined_[subjectID].csv

And the following files shoudl be saved in the output directory:
1. Allsubs_BART_Baseline_distributions.csv
2. Allsubs_BART_Baseline_meanSDdists.csv
3. sAllsubs_BART_Baseline_Summarized.csv




