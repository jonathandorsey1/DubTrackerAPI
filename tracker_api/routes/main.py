from flask import Blueprint, request

from flask_qa.extensions import db
from flask_qa.models import GameEntry

main = Blueprint('main', __name__)

@main.route('/')
def index():
    questions = Question.query.filter(Question.answer != None).all()

    context = {
        'questions' : questions
    }

    return render_template('home.html', **context)