import csv
import os
import data_manager
import uuid

QUESTION_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else 'sample_data/question.csv'
QUESTION_HEADERS = ['id', 'submission_time',
                    'view_number', 'vote_number', 'title',
                    'question_id', 'message', 'image']
ANSWER_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else 'sample_data/answer.csv'
ANSWER_HEADERS = ['id', 'submission_time', 'view_number', 'vote_number', 'question_id', 'message', 'image']


def import_database(which_database):
    if which_database == "question":
        filepath = QUESTION_FILE_PATH
    else:
        filepath = ANSWER_FILE_PATH

    reader = csv.DictReader(open(filepath, 'r'))
    database = []
    for line in reader:
        database.append(line)

    data_manager.convert_unix_timestamp_to_date(database)   # ide kéne a dátum konvertáló

    return database     # list of dicts


def generate_id():
    return uuid.uuid4()


def export_new_data_to_database(new_data, which_database):
    if which_database == "question":
        filepath = QUESTION_FILE_PATH
        header = QUESTION_HEADERS
    else:
        header = ANSWER_HEADERS
        filepath = ANSWER_FILE_PATH

    next_id = generate_id()
    new_data.insert(0, next_id)
    new_data_to_save = dict(zip(header, new_data))
    with open(filepath, 'a', newline='') as f:
        w = csv.DictWriter(f, new_data_to_save.keys())
        w.writerow(new_data_to_save)
