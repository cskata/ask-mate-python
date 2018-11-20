from flask import Flask, render_template, request, redirect, url_for

import data_manager
import connection

app = Flask(__name__)


@app.route('/')
def index():
    return redirect('/list')


@app.route('/test')
def test():
    return redirect('/')

@app.route('/list')
def route_list():
    questions = connection.import_database("question")
    data_manager.sort_data(questions, "submission_time", 'desc')
    return render_template('list.html', questions=questions)

@app.route('/form')
def route_form():
    return render_template('form.html')


@app.route('/list' , method=['POST'])
def route_save_question():
    return redirect('/')



if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
