import datetime
import sqlite3


def current_date(month=False):
    now = str(datetime.date.today())
    if month:
        # remove the day
        now = now[:-3]
    return now.translate(None, "-")


def build_entry_table(db):
    c = db.cursor()
    command = """
    CREATE TABLE entries
    (id INTEGER PRIMARY KEY ASC, month TEXT, date TEXT, price REAL, category TEXT, item TEXT, note TEXT)
    """
    c.execute(command)
    db.commit()
    return db


def build_budget_table(db, budget):
    # build the sql query
    params = []
    command = "CREATE TABLE budget (month TEXT, total REAL"
    for top_level in budget:
        for lower in budget[top_level]:
            command = command + ", " + lower + " REAL"
    command += ")"
    # create it
    c = db.cursor()
    c.execute(command)
    db.commit()
    return db


def build_balance_table(db):
    c = db.cursor()
    command = """
    CREATE TABLE balances
    AS SELECT *
    FROM budget;
    DELETE FROM balances
    """
    c.execute(command)
    db.commit()
    return db


def fetch_month_entries(db, month):
    c = db.cursor()
    command = """
    SELECT * FROM entries
    WHERE month=?
    ORDER BY id ASC
    """
    c.execute(command, (month,))
    entries = c.fetchall()
    return entries



if __name__ == "__main__":
    print(current_date())
    print(current_date(True))