import csv
import os

QUESTION_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else '/sample/question.csv'
QUESTION_HEADERS = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
ANSWER_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else '/sample/answer.csv'
ANSWER_HEADERS = ['id', 'submission_time', 'view_number', 'vote_number', 'question_id', 'message', 'image']


def import_database(which_databate):
    if which_databate == "question":
        filepath = QUESTION_FILE_PATH
    else:
        filepath = ANSWER_FILE_PATH

    reader = csv.DictReader(open(filepath, 'r'))
    database = []
    for line in reader:
        database.append(line)

    return database     # list of dicts
