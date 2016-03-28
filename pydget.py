from flask import Flask, render_template, request, jsonify
from flask.ext.basicauth import BasicAuth
import random
import string

app = Flask(__name__)
app.config['budget'] = "budget.json"

# setup authentification
app.config['BASIC_AUTH_USERNAME'] = 'metjush'
app.config['BASIC_AUTH_PASSWORD'] = '`@#$~^&*{}^'

basic_auth = BasicAuth(app)


@app.route('/')
@basic_auth.required
def index():
    """
    Load the budget
    Load saved entries
    Display current month status
    Display the form for quickly adding a new entry
    :return: template
    """
    pass


@app.route('/add', methods=['POST'])
def add():
    """
    Endpoint for submitting a new entry
    Parameters:
    date, amount, category, notes
    Write entry
    :return: redirect to index to show updated status
    """
    pass


@app.route('/budget')
def budget():
    """
    A tool for editing the budget
    Not needed initially
    :return: template
    """
    pass


@app.route('/delete/<entry>')
def delete(entry):
    """
    Endpoint to delete an existing entry
    Submit an ID, the entry is deleted
    :param entry: ID of an entry to be deleted
    :return: redirect to index to show updated status
    """
    pass


@app.route('/report/<month>')
def report(month):
    """
    Generate a report for the supplied month
    :param month: month in a YYYYMM format
    :return: the report
    """
    pass


if __name__ == "__main__":
    N = 64
    app.secret_key = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(N))
    app.debug = True
    app.run(host='0.0.0.0', port=987)