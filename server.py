from flask import Flask, render_template, request, redirect, url_for

import data_manager
from connection import import_database, export_new_data_to_database

app = Flask(__name__)


@app.route('/')
@app.route('/question')
def index():
    return redirect('/list')


@app.route('/list')
def route_list():
    questions = import_database("question")
    data_manager.sort_data(questions, "submission_time", 'desc')
    return render_template('index.html', questions=questions)


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
            'image': request.form['image']
        }
        export_new_data_to_database(new_question, 'question')
        return redirect('/')


@app.route('/question/<question_id>/new-answer')
def route_new_answer(question_id):
    return render_template('new_answer.html', question_id=question_id)


@app.route("/question/<question_id>", methods=['GET' , 'POST'])
def route_question(question_id):
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

if __name__ == '__main__':
    app.static_folder = 'static'
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
