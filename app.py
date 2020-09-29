from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

import pyshorteners
from send_mail import send_mail


app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:mathew@localhost/Glance"

else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String, nullable=False)
    message = db.Column(db.Text(), nullable=False)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


@app.route('/writetodb', methods=['POST'])
def writetodb():
    if request.method == "POST":
        # pylint: disable=unused-variable
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        if name == "" or email == "" or message == "":
            return render_template('feedback.html', message='Please enter required fields')
        if db.session.query(Feedback).filter(Feedback.name == name).count() == 0:
            feedback = Feedback(name=name, email=email, message=message)
            db.session.add(feedback)
            db.session.commit()
            send_mail(name, email, message)
            return render_template('feedback.html', success='Thanks For Your Feedback')
        else:
            return render_template('feedback.html', message='You have already submitted feedback')


@app.route('/shortener')
def shortener():
    return render_template('shortener.html')


@app.route('/shorttheurl', methods=['POST'])
def shorttheurl():
    if request.method == "POST":
        url = request.form['url']
        if url == "":
            return render_template('shortener.html', message='Please enter the URL to be shortened')
        else:
            shorten = pyshorteners.Shortener()
            shortenedurl = shorten.tinyurl.short(url)
            return render_template('shortener.html', shortenedurl=shortenedurl)


if __name__ == "__main__":
    app.run()
