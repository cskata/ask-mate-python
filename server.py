from flask import Flask, render_template, request, redirect, url_for, session
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
    questions = data_manager.get_limited_database("question", limit)
    key = 'submission_time'
    limit_questions = True
    if 'order_by' in request.args:
        key = request.args.get('order_by')
        direction = request.args.get('order_direction')
        questions = data_manager.sort_data(key, 'question', direction)
        questions = questions[:limit]

    if 'username' in session:
        username = session['username']
        return render_template('index.html', questions=questions, header=key, limit=limit_questions, username=username)
    return render_template('index.html', questions=questions, header=key, limit=limit_questions)


@app.route('/question')
@app.route('/list')
def route_list():
    questions = data_manager.get_database("question")
    key = 'submission_time'
    limit_questions = False
    if 'order_by' in request.args:
        key = request.args.get('order_by')
        direction = request.args.get('order_direction')
        questions = data_manager.sort_data(key, 'question', direction)

    if 'username' in session:
        username = session['username']
        return render_template('index.html', questions=questions, header=key, limit=limit_questions, username=username)

    return render_template('index.html', questions=questions, header=key, limit=limit_questions)


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
            'message': request.form['message'].replace('\n', '<br/>'),
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
    data_manager.update_view_counter(question_id, -2)
    return render_template('new_answer.html', question_id=question_id)


@app.route("/question/<question_id>", methods=['GET', 'POST'])
def route_show_question(question_id):
    data_manager.update_view_counter(question_id, 1)

    if request.method == 'GET':
        current_question = data_manager.get_record_by_id('question', question_id)[0]
        current_answers = data_manager.get_answers_by_question_id(question_id)
        number_of_answers = len(current_answers)

        current_question_comments = data_manager.get_comments_by_question_id('comment', question_id)
        current_answer_comments = data_manager.get_answer_comments('comment')
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

    else:
        new_answer = {
            'submission_time': "",
            'vote_number': 0,
            'question_id': question_id,
            'message': request.form['message'].replace('\n', '<br/>'),
            'image': ""
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
    current_question['message'] = current_question['message'].replace('<br/>', "")

    if request.method == 'GET':
        return render_template('edit_question.html', question=current_question)

    else:
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
        return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/question/<question_id>/delete')
def route_delete_question(question_id):
    data_manager.delete_question_and_answers(question_id)
    return redirect(url_for('route_list'))


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def route_edit_answer(answer_id):
    current_answer = data_manager.get_record_by_id('answer', answer_id)[0]
    current_answer['message'] = current_answer['message'].replace('<br/>', "")

    if request.method == 'GET':
        return render_template('edit_answer.html', answer=current_answer)
    else:
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
        return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/answer/<answer_id>/delete')
def route_delete_answer(answer_id):
    current_answer = data_manager.get_record_by_id("answer", answer_id)[0]
    question_id = current_answer['question_id']

    data_manager.delete_single_answer_by_id(answer_id)
    data_manager.update_view_counter(question_id, -1)
    return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/comments/<comment_id>/delete')
def route_delete_comment(comment_id):
    question_id = data_manager.get_question_id_by_comment_id(comment_id)
    data_manager.delete_single_comment_by_id(comment_id)
    data_manager.update_view_counter(question_id, -1)
    return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/question/<question_id>/vote-up')
def route_vote_question_up(question_id):
    data_manager.vote_counter("question", question_id, 'up')
    data_manager.update_view_counter(question_id, -1)
    return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/question/<question_id>/vote-down')
def route_vote_question_down(question_id):
    data_manager.vote_counter("question", question_id, 'down')
    data_manager.update_view_counter(question_id, -1)
    return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/answer/<answer_id>/vote-up')
def route_vote_answer_up(answer_id):
    data_manager.vote_counter('answer', answer_id, 'up')
    question_id = data_manager.get_question_id_by_answer_id(answer_id)
    data_manager.update_view_counter(question_id, -1)
    return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/answer/<answer_id>/vote-down')
def route_vote_answer_down(answer_id):
    data_manager.vote_counter('answer', answer_id, 'down')
    question_id = data_manager.get_question_id_by_answer_id(answer_id)
    data_manager.update_view_counter(question_id, -1)
    return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
def add_new_comment_to_question(question_id):
    if request.method == 'GET':
        return render_template('new_question_comment.html', question_id=question_id)

    else:
        new_comment = {
            'question_id': question_id,
            'message': request.form['comment_message'].replace('\n', '<br/>'),
            'submission_time': "",
            'edited_count': 0
        }

        data_manager.insert_new_question_comment_to_database(new_comment)
        return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
def add_new_comment_to_answer(answer_id):
    question_id = data_manager.get_question_id_by_answer_id(answer_id)

    if request.method == 'GET':
        return render_template('new_answer_comment.html', answer_id=answer_id)

    else:
        new_comment = {
            'question_id': question_id,
            'answer_id': answer_id,
            'message': request.form['comment_message'].replace('\n', '<br/>'),
            'submission_time': "",
            'edited_count': 0
        }

        data_manager.insert_new_answer_comment_to_database(new_comment)
        data_manager.update_view_counter(question_id, -1)
        return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/comments/<comment_id>/edit', methods=['GET', 'POST'])
def update_comment(comment_id):
    if request.method == 'GET':
        comment = data_manager.get_comment_by_comment_id('comment', comment_id)
        comment['message'] = comment['message'].replace("<br/>", "")

        return render_template('edit_comment.html', comment_id=comment_id, comment=comment)

    else:
        edited_comment = {
            'message': request.form['comment_message'].replace('\n', '<br/>')
        }

        data_manager.update_data_by_id('comment', edited_comment, comment_id)

        current_comment = data_manager.get_comment_by_comment_id('comment', comment_id)
        question_id = current_comment['question_id']
        data_manager.update_view_counter(question_id, -1)

        return redirect(url_for("route_show_question", question_id=question_id))


@app.route('/search')
def search():
    key = 'submission_time'

    if 'q' in request.args:
        search_data = request.args.get('q')
        questions = data_manager.get_search_results(search_data, key)[0]
        number_of_results = data_manager.get_search_results(search_data, key)[1]

    return render_template('index.html', questions=questions, header=key,
                           search_data=search_data, results_num=number_of_results)


@app.route('/registration', methods=['GET', 'POST'])
def new_user_registration():
    new_user = True
    if request.method == 'POST':
        new_user = {
            'username': request.form['username'],
            'password': request.form['password']
        }

        is_username_taken = data_manager.check_username_in_database(new_user)

        if is_username_taken:
            message = "That username is already taken, please choose something else."
            return render_template('reg-login.html', message=message, new_user=new_user)
        else:
            data_manager.register_new_user(new_user)
            return redirect(url_for('index'))

    return render_template('reg-login.html', new_user=new_user)


@app.route('/login', methods=['GET', 'POST'])
def log_in_user():
    if request.method == 'POST':
        login_data = {
            'username': request.form['username'],
            'password': request.form['password']
        }

        login_check = data_manager.verify_user(login_data)

        if login_check:
            session['username'] = login_data['username']
            session['user_id'] = ''
            return redirect(url_for('index'))
        else:
            message = "Incorrect username or password"
            return render_template('reg-login.html', message=message)

    return render_template('reg-login.html')


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
