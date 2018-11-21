import operator
import pandas
from connection import import_database, export_all_data


def convert_unix_timestamp_to_date(database):
    for data in database:
        data["submission_time"] = pandas.to_datetime(data["submission_time"], unit='s')
    return database


def convert_date_to_unix_timestamp(database):
    for data in database:
        data["submission_time"] = pandas.to_datetime(data["submission_time"]).value // 10**9
    return database


def sort_data(data, key="submission_time", order="desc"):
    if order == "asc":
        result = data.sort(key=operator.itemgetter(key))
    else:
        result = data.sort(key=operator.itemgetter(key), reverse=True)
    return result


def get_answers_for_question(question_id, every_answer):
    answers = []
    for answer in every_answer:
        if answer['question_id'] == str(question_id):
            answers.append(answer)
    sort_data(answers, "submission_time", 'asc')
    return answers


def get_question_by_id(question_id, every_question):
    for question_data in every_question:
        if question_data['id'] == question_id:
            current_question = question_data
    return current_question


def get_question_id_by_answer_id(answer_id, every_answer):
    question_id = ""
    for answer_data in every_answer:
        if answer_data['id'] == answer_id:
            question_id = answer_data['question_id']
    return question_id


def remove_data_by_id(database, data_id, key):
    for data in database:
        if data[key] == data_id:
            database.remove(data)


def convert_counter_to_int(database, key):
    for data in database:
        data[key] = int(data[key])


def view_counter(question_id, count):
    every_question = import_database("question")
    current_question = get_question_by_id(question_id, every_question)
    remove_data_by_id(every_question, question_id, 'id')

    current_question['view_number'] += count
    every_question.append(current_question)
    export_all_data("question", every_question)
