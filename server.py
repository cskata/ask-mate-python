from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import data_manager
from connection import import_database, export_new_data_to_database, export_all_data
import os


UPLOAD_FOLDER = '/home/bertalan/Asztal/webroom/First TW/ask-mate-python/static/img'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
@app.route('/question')
def index():
    return redirect('/list')


@app.route('/list')
def route_list():
    questions = import_database("question")
    data_manager.sort_data(questions)
    return render_template('index.html', questions=questions, header="submission_time")


@app.route('/list?order_by=<key>&order_direction=desc', methods=['GET', 'POST'])
def route_order_list():
    questions = import_database("question")
    key = request.form['header']
    if request.method == 'POST':
        data_manager.sort_data(questions, key)
        return render_template('index.html', questions=questions, header=key)


@app.route('/add-question', methods=['GET', 'POST'])
def route_add_question():
    if request.method == 'GET':
        return render_template('new_question.html')
    else:
        new_question = {
            'id': "",
            'submission_time': "",
            'view_number': 0,
            'vote_number': 0,
            'title': request.form['title'],
            'message': request.form['message'],
            'image': request.files['image']
        }
        export_new_data_to_database(new_question, 'question')
        file = request.files['image']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('index', filename=filename))


@app.route('/question/<question_id>/new-answer')
def route_new_answer(question_id):
    data_manager.view_counter(question_id, -1)
    return render_template('new_answer.html', question_id=question_id)


@app.route("/question/<question_id>", methods=['GET', 'POST'])
def route_show_question(question_id):
    data_manager.view_counter(question_id, 1)

    if request.method == 'GET':
        every_question = import_database("question")
        every_answer = import_database("answer")

        current_answers = data_manager.get_answers_for_question(question_id, every_answer)
        current_question = data_manager.get_question_by_id(question_id, every_question)

        return render_template('show_question.html', question_id=question_id,
                               question=current_question, answers=current_answers)
    else:
        new_answer = {
            'id': "",
            'submission_time': "",
            'vote_number': 0,
            'question_id': question_id,
            'message': request.form['message'],
            'image': request.form['image']
        }
        export_new_data_to_database(new_answer, "answer")
        return redirect('/question/'+question_id)


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def route_edit_question(question_id):
    every_question = import_database("question")
    current_question = data_manager.get_question_by_id(question_id, every_question)
    if request.method == 'GET':
        return render_template('edit_question.html', question=current_question)
    else:
        edited_question = {
            'id': question_id,
            'submission_time': current_question['submission_time'],
            'view_number': current_question['view_number'],
            'vote_number': current_question['vote_number'],
            'title': request.form['title'],
            'message': request.form['message'],
            'image': request.form['image']
        }

        data_manager.remove_data_by_id(every_question, question_id, 'id')
        every_question.append(edited_question)
        export_all_data("question", every_question)
        return redirect('/question/'+question_id)


@app.route('/question/<question_id>/delete')
def route_delete_question(question_id):
    every_question = import_database("question")
    every_answer = import_database("answer")

    data_manager.remove_data_by_id(every_question, question_id, 'id')
    data_manager.remove_data_by_id(every_answer, question_id, 'question_id')

    export_all_data("question", every_question)
    export_all_data("answer", every_answer)

    return redirect('/list')


@app.route('/answer/<answer_id>/delete')
def route_delete_answer(answer_id):
    every_answer = import_database("answers")
    question_id = data_manager.get_question_id_by_answer_id(answer_id, every_answer)
    data_manager.remove_data_by_id(every_answer, answer_id, 'id')

    export_all_data("answers", every_answer)
    return redirect('/question/'+question_id)


@app.route('/question/<question_id>/vote-up')
def route_vote_question_up(question_id):
    every_question = import_database("question")
    every_question = data_manager.vote_counter(question_id, every_question, 'up')
    export_all_data('question', every_question)

    data_manager.view_counter(question_id, -1)
    return redirect('/question/'+question_id)


@app.route('/question/<question_id>/vote-down')
def route_vote_question_down(question_id):
    every_question = import_database("question")
    every_question = data_manager.vote_counter(question_id, every_question, 'down')
    export_all_data('question', every_question)

    data_manager.view_counter(question_id, -1)
    return redirect('/question/' + question_id)


@app.route('/answer/<answer_id>/vote-up')
def route_vote_answer_up(answer_id):
    every_answer = import_database("answer")
    every_answer = data_manager.vote_counter(answer_id, every_answer, 'up')

    question_id = data_manager.get_question_id_by_answer_id(answer_id, every_answer)
    data_manager.view_counter(question_id, -1)

    export_all_data('answer', every_answer)
    return redirect('/question/' + question_id)


@app.route('/answer/<answer_id>/vote-down')
def route_vote_answer_down(answer_id):
    every_answer = import_database("answer")
    every_answer = data_manager.vote_counter(answer_id, every_answer, 'down')

    question_id = data_manager.get_question_id_by_answer_id(answer_id, every_answer)
    data_manager.view_counter(question_id, -1)

    export_all_data('answer', every_answer)
    return redirect('/question/' + question_id)


if __name__ == '__main__':
    app.static_folder = 'static'
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
