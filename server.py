from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import data_manager
import os


UPLOAD_FOLDER = "static/image/"

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    questions = data_manager.get_limited_database("question", 5)
    key = 'submission_time'
    # if 'order_by' in request.args:
    #     key = request.args.get('order_by')
    #     direction = request.args.get('order_direction')
    #     data_manager.sort_data(questions, key, direction)

    return render_template('index.html', questions=questions, header=key)


@app.route('/question')
@app.route('/list')
def route_list():
    questions = data_manager.get_database("question")
    key = 'submission_time'
    # if 'order_by' in request.args:
    #     key = request.args.get('order_by')
    #     direction = request.args.get('order_direction')
    #     data_manager.sort_data(questions, key, direction)

    return render_template('index.html', questions=questions, header=key)


@app.route('/add-question', methods=['GET', 'POST'])
def route_add_question():
    if request.method == 'GET':
        return render_template('new_question.html')
    else:
        new_question = {
            'submission_time': "",
            'view_number': 0,
            'vote_number': 0,
            'title': request.form['title'],
            'message': request.form['message'],
            'image': ""
        }

        if len(request.files) > 0:
            if request.files['image'].filename != "":
                current_image_name = str(request.files['image'])
                normal_image_name = data_manager.get_back_image_name(current_image_name)
                new_question['image'] = normal_image_name

                file = request.files['image']
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        filename = ""

        data_manager.insert_new_question_to_database(new_question)
        return redirect(url_for('index', filename=filename))


@app.route('/question/<question_id>/new-answer')
def route_new_answer(question_id):
    #data_manager.view_counter(question_id, -2)
    return render_template('new_answer.html', question_id=question_id)


@app.route("/question/<question_id>", methods=['GET', 'POST'])
def route_show_question(question_id):
    #data_manager.view_counter(question_id, 1)
    if request.method == 'GET':
        current_question = data_manager.get_record_by_id('question', question_id)
        current_answers = data_manager.get_answers_by_question_id(question_id)

        return render_template('show_question.html', question_id=question_id,
                               question=current_question[0], answers=current_answers)
    else:
        new_answer = {
            'submission_time': "",
            'vote_number': 0,
            'question_id': question_id,
            'message': request.form['message'],
            'image': "",
        }

        if len(request.files) > 0:
            if request.files['image'].filename != "":
                current_image_name = str(request.files['image'])
                normal_image_name = data_manager.get_back_image_name(current_image_name)
                new_answer['image'] = normal_image_name

                file = request.files['image']
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        data_manager.insert_new_answer_to_database(new_answer)
        return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/image/<image_filename>')
def route_open_image(image_filename):
    return render_template('view_image.html', image=image_filename)


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def route_edit_question(question_id):
    current_question = data_manager.get_record_by_id('question', question_id)[0]
    if request.method == 'GET':
        return render_template('edit_question.html', question=current_question)

    else:
        edited_question = {
            'title': request.form['title'],
            'message': request.form['message'],
            'image': ""
        }

        question_id = int(request.form['id'])

        if len(request.files) > 0:
            if request.files['image'].filename != "":
                edited_question['image'] = request.files['image']
                file = request.files['image']
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        data_manager.update_question(edited_question, question_id)
        #data_manager.view_counter(question_id, -1)
        return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/question/<question_id>/delete')
def route_delete_question(question_id):
    data_manager.delete_question_and_answers(question_id)
    return redirect(url_for('route_list'))


@app.route('/answer/<answer_id>/delete')
def route_delete_answer(answer_id):
    current_answer = data_manager.get_record_by_id("answer", answer_id)[0]
    question_id = current_answer['question_id']
    data_manager.delete_single_answer_by_id(answer_id)
    return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/question/<question_id>/vote-up')
def route_vote_question_up(question_id):
    every_question = import_database("question")
    every_question = data_manager.vote_counter(question_id, every_question, 'up')

    export_all_data('question', every_question)
    data_manager.view_counter(question_id, -1)
    return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/question/<question_id>/vote-down')
def route_vote_question_down(question_id):
    every_question = import_database("question")
    every_question = data_manager.vote_counter(question_id, every_question, 'down')

    export_all_data('question', every_question)
    data_manager.view_counter(question_id, -1)
    return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/answer/<answer_id>/vote-up')
def route_vote_answer_up(answer_id):
    every_answer = import_database("answer")
    every_answer = data_manager.vote_counter(answer_id, every_answer, 'up')

    question_id = data_manager.get_question_id_by_answer_id(answer_id, every_answer)
    data_manager.view_counter(question_id, -1)

    export_all_data('answer', every_answer)
    return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/answer/<answer_id>/vote-down')
def route_vote_answer_down(answer_id):
    every_answer = import_database("answer")
    every_answer = data_manager.vote_counter(answer_id, every_answer, 'down')

    question_id = data_manager.get_question_id_by_answer_id(answer_id, every_answer)
    data_manager.view_counter(question_id, -1)

    export_all_data('answer', every_answer)
    return redirect(url_for("route_show_question", question_id=question_id))


if __name__ == '__main__':
    app.static_folder = 'static'
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
