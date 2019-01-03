from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import data_manager
import os


UPLOAD_FOLDER = "static/image/"

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "titkoskulcs"


@app.route('/')
def index():
    limit = 5
    questions = data_manager.get_limited_database('question', limit)
    key = 'submission_time'
    limit_questions = True

    if 'order_by' in request.args:
        key = request.args.get('order_by')
        direction = request.args.get('order_direction')
        questions = data_manager.sort_data(key, 'question', direction)
        questions = questions[:limit]

    if 'username' in session:
        username = session['username']
        return render_template('index.html', questions=questions, header=key,
                               limit=limit_questions, username=username)

    return render_template('index.html', questions=questions, header=key,
                           limit=limit_questions)


@app.route('/question')
@app.route('/list')
def route_list():
    questions = data_manager.get_database('question')
    key = 'submission_time'
    limit_questions = False

    if 'order_by' in request.args:
        key = request.args.get('order_by')
        direction = request.args.get('order_direction')
        questions = data_manager.sort_data(key, 'question', direction)

    if 'username' in session:
        username = session['username']
        return render_template('index.html', questions=questions, header=key,
                               limit=limit_questions, username=username)

    return render_template('index.html', questions=questions, header=key,
                           limit=limit_questions)


@app.route('/add-question', methods=['GET', 'POST'])
def route_add_question():
    username = session['username']

    if request.method == 'POST':
        user_id = data_manager.get_user_id_by_username(username)
        new_question = {
            'submission_time': "",
            'view_number': 0,
            'vote_number': 0,
            'title': request.form['title'],
            'message': request.form['message'].replace('\n', '<br/>'),
            'image': "",
            'user_id': user_id
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

    return render_template('new_question.html', username=username)


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def route_new_answer(question_id):
    username = session['username']
    data_manager.update_view_counter(question_id, -2)

    if request.method == 'POST':
        username = session['username']
        user_id = data_manager.get_user_id_by_username(username)
        new_answer = {
            'submission_time': "",
            'vote_number': 0,
            'question_id': question_id,
            'message': request.form['message'].replace('\n', '<br/>'),
            'image': "",
            'user_id': user_id
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
        return redirect(url_for('route_show_question', question_id=question_id))

    return render_template('new_answer.html', question_id=question_id, username=username)


@app.route("/question/<question_id>")
def route_show_question(question_id):
    data_manager.update_view_counter(question_id, 1)
    current_question = data_manager.get_record_by_id('question', question_id)[0]
    current_answers = data_manager.get_answers_by_question_id(question_id)
    number_of_answers = len(current_answers)
    current_question_comments = data_manager.get_comments_by_question_id( question_id)
    current_answer_comments = data_manager.get_answer_comments()

    if 'username' in session:
        username = session['username']
        return render_template('show_question.html', question_id=question_id,
                               question=current_question, answers=current_answers,
                               question_comments=current_question_comments,
                               answer_comments=current_answer_comments,
                               number_of_answers=number_of_answers, username=username)

    return render_template('show_question.html', question_id=question_id,
                           question=current_question, answers=current_answers,
                           question_comments=current_question_comments,
                           answer_comments=current_answer_comments,
                           number_of_answers=number_of_answers)


@app.route('/image/<image_filename>')
def route_open_image(image_filename):
    return render_template('view_image.html', image=image_filename)


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def route_edit_question(question_id):
    current_question = data_manager.get_record_by_id('question', question_id)[0]
    current_question['message'] = current_question['message'].replace('<br/>', "")
    username = session['username']

    if request.method == 'POST':
        edited_question = {
            'title': request.form['title'],
            'message': request.form['message'].replace('\n', '<br/>'),
            'image': current_question['image']
        }

        if len(request.files) > 0:
            if request.files['image'].filename != "":
                current_image_name = str(request.files['image'])
                normal_image_name = data_manager.get_back_image_name(current_image_name)
                edited_question['image'] = normal_image_name

                file = request.files['image']
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        data_manager.update_question(edited_question, question_id)
        data_manager.update_view_counter(question_id, -1)
        return redirect(url_for('route_show_question', question_id=question_id))

    return render_template('edit_question.html', question=current_question, username=username)


@app.route('/question/<question_id>/delete')
def route_delete_question(question_id):
    data_manager.delete_question_and_answers(question_id)
    return redirect(url_for('route_list'))


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def route_edit_answer(answer_id):
    current_answer = data_manager.get_record_by_id('answer', answer_id)[0]
    current_answer['message'] = current_answer['message'].replace('<br/>', "")
    username = session['username']

    if request.method == 'POST':
        edited_answer = {
            'message': request.form['message'].replace('\n', '<br/>'),
            'image': current_answer['image']
        }

        answer_id = int(request.form['id'])
        question_id = int(request.form['question_id'])

        if len(request.files) > 0:
            if request.files['image'].filename != "":
                current_image_name = str(request.files['image'])
                normal_image_name = data_manager.get_back_image_name(current_image_name)
                edited_answer['image'] = normal_image_name

                file = request.files['image']
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        data_manager.update_answer(edited_answer, answer_id)
        data_manager.update_view_counter(question_id, -1)
        return redirect(url_for('route_show_question', question_id=question_id))

    return render_template('edit_answer.html', answer=current_answer, username=username)


@app.route('/answer/<answer_id>/delete')
def route_delete_answer(answer_id):
    current_answer = data_manager.get_record_by_id('answer', answer_id)[0]
    question_id = current_answer['question_id']

    data_manager.delete_single_answer_by_id(answer_id)
    data_manager.update_view_counter(question_id, -1)
    return redirect(url_for('route_show_question', question_id=question_id))


@app.route('/comments/<comment_id>/delete')
def route_delete_comment(comment_id):
    question_id = data_manager.get_question_id_by_comment_id(comment_id)
    data_manager.delete_single_comment_by_id(comment_id)
    data_manager.update_view_counter(question_id, -1)
    return redirect(url_for('route_show_question', question_id=question_id))


@app.route('/question/<question_id>/vote-up')
def route_vote_question_up(question_id):
    data_manager.vote_counter("question", question_id, 'up')
    data_manager.update_view_counter(question_id, -1)
    return redirect(url_for('route_show_question', question_id=question_id))


@app.route('/question/<question_id>/vote-down')
def route_vote_question_down(question_id):
    data_manager.vote_counter("question", question_id, 'down')
    data_manager.update_view_counter(question_id, -1)
    return redirect(url_for('route_show_question', question_id=question_id))


@app.route('/answer/<answer_id>/vote-up')
def route_vote_answer_up(answer_id):
    data_manager.vote_counter('answer', answer_id, 'up')
    question_id = data_manager.get_question_id_by_answer_id(answer_id)
    data_manager.update_view_counter(question_id, -1)
    return redirect(url_for('route_show_question', question_id=question_id))


@app.route('/answer/<answer_id>/vote-down')
def route_vote_answer_down(answer_id):
    data_manager.vote_counter('answer', answer_id, 'down')
    question_id = data_manager.get_question_id_by_answer_id(answer_id)
    data_manager.update_view_counter(question_id, -1)
    return redirect(url_for('route_show_question', question_id=question_id))


@app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
def add_new_comment_to_question(question_id):
    username = session['username']

    if request.method == 'POST':
        user_id = data_manager.get_user_id_by_username(username)
        new_comment = {
            'question_id': question_id,
            'message': request.form['comment_message'].replace('\n', '<br/>'),
            'submission_time': "",
            'edited_count': 0,
            'user_id': user_id
        }

        data_manager.insert_new_question_comment_to_database(new_comment)
        return redirect(url_for('route_show_question', question_id=question_id))

    return render_template('new_question_comment.html', question_id=question_id, username=username)


@app.route('/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
def add_new_comment_to_answer(answer_id):
    if request.method == 'POST':
        question_id = data_manager.get_question_id_by_answer_id(answer_id)
        username = session['username']
        user_id = data_manager.get_user_id_by_username(username)
        new_comment = {
            'question_id': question_id,
            'answer_id': answer_id,
            'message': request.form['comment_message'].replace('\n', '<br/>'),
            'submission_time': "",
            'edited_count': 0,
            'user_id': user_id
        }

        data_manager.insert_new_answer_comment_to_database(new_comment)
        data_manager.update_view_counter(question_id, -1)
        return redirect(url_for('route_show_question', question_id=question_id))

    return render_template('new_answer_comment.html', answer_id=answer_id)


@app.route('/comments/<comment_id>/edit', methods=['GET', 'POST'])
def update_comment(comment_id):
    comment = data_manager.get_comment_by_comment_id('comment', comment_id)
    comment['message'] = comment['message'].replace("<br/>", "")
    username = session['username']

    if request.method == 'POST':
        edited_comment = {
            'message': request.form['comment_message'].replace('\n', '<br/>')
        }

        data_manager.update_data_by_id('comment', edited_comment, comment_id)

        current_comment = data_manager.get_comment_by_comment_id('comment', comment_id)
        question_id = current_comment['question_id']
        data_manager.update_view_counter(question_id, -1)
        return redirect(url_for('route_show_question', question_id=question_id))

    return render_template('edit_comment.html', comment_id=comment_id, comment=comment, username=username)


@app.route('/search')
def search():
    key = 'submission_time'
    username = session['username']
    if 'q' in request.args:
        search_data = request.args.get('q')
        questions = data_manager.get_search_results(search_data, key)[0]
        number_of_results = data_manager.get_search_results(search_data, key)[1]

    return render_template('index.html', questions=questions, header=key, search_data=search_data,
                           results_num=number_of_results, username=username)


@app.route('/registration', methods=['POST'])
def new_user_registration():
    new_user = {
        'username': request.form['username'],
        'password': request.form['password']
    }

    is_username_taken = data_manager.check_username_in_database(new_user)
    password = request.form['password']
    password_confirm = request.form['confirm_password']

    if password != password_confirm:
        flash("Password does not match!")
    elif is_username_taken:
        flash("Username is already taken!")
    else:
        flash("Registration was successful!")
        data_manager.register_new_user(new_user)
    return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def log_in_user():
    login_data = {
        'username': request.form['username'],
        'password': request.form['password']
    }

    login_check = data_manager.verify_user(login_data)

    if login_check:
        session['username'] = login_data['username']
    else:
        flash("Invalid username or password!")
    return redirect(url_for('index'))


@app.route('/list_users')
def list_registered_users():
    users_data = data_manager.get_all_user_data()
    username = session['username']
    return render_template('list_users.html', users_data=users_data, username=username)


@app.route('/logout')
def log_user_out():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.static_folder = 'static'
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
