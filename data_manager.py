from connection import connection_handler
from datetime import datetime


def convert_counter_to_int(database, key):
    for data in database:
        data[key] = int(data[key])


def view_counter(question_id, increment):
    every_question = import_database("question")
    current_question = get_question_by_id(question_id, every_question)
    remove_data_by_id(every_question, question_id, 'id')

    current_question['view_number'] += increment
    every_question.append(current_question)
    export_all_data("question", every_question)


def vote_counter(data_id, database, up_or_down):
    for data in database:
        if data['id'] == data_id:
            if up_or_down == "up":
                data['vote_number'] += 1
            else:
                data['vote_number'] -= 1
    return database


def get_back_image_name(data):
    if data['image'] != '':
        image = data['image']
        image = image.split()
        image = image[1].replace("'", '')
    else:
        image = ""
    return image


@connection_handler
def get_database(cursor, which_database):
    cursor.execute(f"""
                    SELECT * FROM {which_database}
                    ORDER BY submission_time DESC;
                   """)
    database = cursor.fetchall()
    return database


@connection_handler
def get_limited_database(cursor, which_database, limit):
    cursor.execute(f"""
                    SELECT * FROM {which_database}
                    ORDER BY submission_time DESC
                    LIMIT {limit};
                   """)
    database = cursor.fetchall()
    return database


@connection_handler
def insert_new_question_to_database(cursor, new_data):
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_data['submission_time'] = str(dt)

    data_to_insert = list(new_data.values())
    cursor.execute(f"""
                    INSERT INTO question
                    (submission_time, view_number, vote_number, title, message, image)
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """, data_to_insert)


@connection_handler
def insert_new_answer_to_database(cursor, new_data):
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_data['submission_time'] = str(dt)

    data_to_insert = list(new_data.values())
    cursor.execute(f"""
                    INSERT INTO answer
                    (submission_time, vote_number, question_id, message, image)
                    VALUES (%s, %s, %s, %s, %s);
                    """, data_to_insert)


@connection_handler
def get_record_by_id(cursor, which_database, id):
    cursor.execute(f"""
                    SELECT * FROM {which_database}
                    WHERE id = {id};
                   """)
    record = cursor.fetchall()
    return record


@connection_handler
def update_question(cursor, updated_data, question_id):
    new_data = list(updated_data.values())
    cursor.execute(f"""
                    UPDATE question
                    SET title = %s,
                        message = %s,
                        image = %s
                    WHERE id = {question_id};
                    """, new_data)


@connection_handler
def get_answers_by_question_id(cursor, question_id):
    cursor.execute(f"""
                        SELECT * FROM answer
                        WHERE question_id = {question_id};
                       """)
    current_answers = cursor.fetchall()
    return current_answers


@connection_handler
def delete_every_answer_by_question_id(cursor, question_id):
    current_answers = get_answers_by_question_id(question_id)
    list_of_answer_ids = []
    for answer in current_answers:
        list_of_answer_ids.append(int(answer['id']))

    for answer_id in list_of_answer_ids:
        cursor.execute(f"""
                        DELETE FROM answer
                        WHERE id = {answer_id};
                        """)


@connection_handler
def delete_question_and_answers(cursor, question_id):
    delete_every_answer_by_question_id(question_id)

    cursor.execute(f"""
                    DELETE FROM question
                    WHERE id = {question_id};
                    """)


@connection_handler
def delete_single_answer_by_id(cursor, answer_id):
    cursor.execute(f"""
                        DELETE FROM answer
                        WHERE id = {answer_id};
                        """)
