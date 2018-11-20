import csv
import os
import data_manager
import uuid
import time

QUESTION_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else 'sample_data/question.csv'
QUESTION_HEADERS = ['id', 'submission_time', 'view_number',
                    'vote_number', 'title', 'message', 'image']
ANSWER_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else 'sample_data/answer.csv'
ANSWER_HEADERS = ['id', 'submission_time','vote_number', 'question_id', 'message', 'image']


def import_database(which_database):
    if which_database == "question":
        filepath = QUESTION_FILE_PATH
    else:
        filepath = ANSWER_FILE_PATH

    reader = csv.DictReader(open(filepath, 'r'))
    database = []
    for line in reader:
        database.append(line)

    data_manager.convert_unix_timestamp_to_date(database)

    return database     # list of dicts


def generate_id():
    return str(uuid.uuid4())[:8]


def export_new_data_to_database(new_data, which_database):
    next_id = generate_id()

    new_data['id'] = next_id
    new_data['submission_time'] = int(time.time())

    if which_database == "question":
        filepath = QUESTION_FILE_PATH
    else:
        filepath = ANSWER_FILE_PATH


    with open(filepath, 'a', newline='') as f:
        w = csv.DictWriter(f, new_data.keys())
        w.writerow(new_data)


def export_all_data(which_database, data):
    if which_database == "question":
        filepath = QUESTION_FILE_PATH
        header = QUESTION_HEADERS
    else:
        filepath = ANSWER_FILE_PATH
        header = ANSWER_HEADERS
    data_manager.convert_date_to_unix_timestamp(data)
    with open(filepath, 'w') as output_file:
       dict_writer = csv.DictWriter(output_file, header)
       dict_writer.writeheader()
       dict_writer.writerows(data)