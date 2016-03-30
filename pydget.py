from flask import Flask, render_template, request, url_for, json, redirect, flash
from flask.ext.basicauth import BasicAuth
import random
import string
from utils import *
import os
import sqlite3

app = Flask(__name__)
app.config['budget'] = "static/budget.json"

# setup authentification
app.config['BASIC_AUTH_USERNAME'] = 'metjush'
app.config['BASIC_AUTH_PASSWORD'] = '`@#$~^&*{}^'

basic_auth = BasicAuth(app)

# setup database connection
app.config['db'] = 'static/pydget.db'


@app.route('/')
@basic_auth.required
def index():
    """
    Load the budget
    Display current month status
    :return: template
    """

    # load the budget
    budget = json.load(open(app.config['budget'], 'rb'))

    # get current day and month
    month = current_date(True)
    # day = current_date()

    # check if the entries table is created
    db = sqlite3.connect(app.config['db'])
    db = build_entry_table(db)

    # check if the budget table is created
    db = build_budget_table(db, budget)

    # check if the balances table is created
    db = build_balance_table(db)

    # get the current balance
    _, balance = get_balance(db, month, budget)

    # render the main template
    return render_template('balance.html', balance=balance, budget=budget)


@app.route('/new')
@basic_auth.required
def new_entry():
    # load the budget
    budget = json.load(open(app.config['budget'], 'rb'))

    return render_template('new_entry.html', budget=budget)


@app.route('/entries')
@basic_auth.required
def entries():
    # get current month
    month = current_date(True)

    # connect to db
    db = sqlite3.connect(app.config['db'])

    # fetch this month's entries
    entries = fetch_month_entries(db, month)

    return render_template('entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add():
    """
    Endpoint for submitting a new entry
    Parameters:
    date, price, category, item, note
    Write entry
    :return: redirect to index to show updated status
    """
    # connect to database
    db = sqlite3.connect(app.config['db'])

    # init the entry dict
    entry = dict()

    # write the data
    entry['month'] = current_date(True)
    entry['date'] = str(request.form['date']).translate(None, '-')
    entry['price'] = float(request.form['price'])
    entry['category'] = request.form['category']
    item = 'item-' + request.form['category']
    entry['item'] = request.form[item]
    entry['note'] = request.form['note']
    # write to db
    db = write_entry(db, entry)
    # redirect to index
    flash("Entry added successfully!")
    return redirect(url_for('index'))


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
    # connect to database
    db = sqlite3.connect(app.config['db'])
    # delete the entry
    db = delete_entry(db, entry)
    # redirect to index
    flash("Entry successfully deleted!")
    return redirect(url_for('index'))


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
    app.run(host='0.0.0.0', port=9876)