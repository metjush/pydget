from flask import Flask, render_template, request, url_for, json, redirect, flash
from flask.ext.basicauth import BasicAuth
import random
import string
from utils import *
import os
import sqlite3

app = Flask(__name__)
app.config['budget'] = "static/budget.json"
app.config['regular'] = "static/regular.json"

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
    last_month = get_last_month()
    # day = current_date()

    # check if the entries table is created
    db = sqlite3.connect(app.config['db'])
    db = build_entry_table(db)

    # check if the budget table is created
    db = build_budget_table(db, budget)

    # check if regular payment check table is created
    db = build_regular_table(db)

    # check if the balances table is created
    db = build_balance_table(db)

    # check if a budget is entered for this month
    # if not, calculate leftover from last month and create new budget entry
    if not check_budget(db, month):
        leftover = calculate_leftover(db, last_month)
        budget['remainder']['leftover'] += leftover
        db = enter_budget(db, month, budget)

    # check if there is a balance for this month

    # get the current balance
    _, balance = get_balance(db, month, budget)

    # render the main template
    return render_template('balance.html', balance=balance, budget=budget)


@app.route('/new_entry')
@basic_auth.required
def new_entry():
    # load the budget
    budget = json.load(open(app.config['budget'], 'rb'))

    return render_template('new_entry.html', budget=budget)


@app.route('/entries')
@app.route('/entries/<month>')
@basic_auth.required
def entries(month=None):
    # connect to db
    db = sqlite3.connect(app.config['db'])

    # fetch this month's entries
    if month is None:
        entries = fetch_all_entries(db)
    else:
        entries = fetch_month_entries(db, month)

    # fetch all months
    months = fetch_months(db)

    return render_template('entries.html', entries=entries, months=months)


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


@app.route('/add_regular')
def add_regular():
    """
    Add regular payments to this month's entries
    - google play and spotify
    - charity / giving
    - saving and tax and insurance

    :return:
    """
    # load json of regular payments
    regular = json.load(open(app.config['regular'], 'rb'))

    # connect to database
    db = sqlite3.connect(app.config['db'])

    # check if regulars were added this month
    month = current_date(True)
    day = current_date()
    if not write_regular(db, month, day):
        flash("Regular payments already added this month")
        return redirect(url_for('index'))

    # write them into database
    for payment in regular:
        entry = dict() # init the entry dict
        entry['month'] = month
        entry['date'] = day
        entry['price'] = payment[0]
        entry['category'] = payment[1]
        entry['item'] = payment[2]
        entry['note'] = payment[3]
        # write to db
        db = write_entry(db, entry)

    flash("Regular payments added successfully!")
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