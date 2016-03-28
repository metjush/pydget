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
    c.executescript(command)
    db.commit()
    return db


def enter_budget(db, month, budget, total=1000):
    # build the query
    command = "INSERT INTO budget VALUES (?, ?"
    params = [month, total]
    for top in budget:
        for lower in budget[top]:
            params.append(budget[top][lower])
            command += ",?"
    command += ")"
    # write
    c = db.cursor()
    c.execute(command, tuple(params))
    db.commit()
    return db


def get_budget_entry(db, month, item):
    command = """
    SELECT %s FROM budget
    WHERE month=?
    """ % item
    c = db.cursor()
    c.execute(command, (month,))
    result = c.fetchone()[0]
    return result


def sum_entries(entries):
    sum = 0
    for entry in entries:
        sum += entry[3]
    return sum


def get_balance(db, month, budget):
    # fetch all entries for the given month
    all = fetch_month_entries(db, month)
    total = sum_entries(all)
    # iterate over keys, to update individual balances
    balances = [total]
    for top in budget:
        for low in budget[top]:
            ent = fetch_month_entries(db, month, low)
            sum_ent = sum_entries(ent)
            item_budget = get_budget_entry(db, month, low)
            balance = item_budget - sum_ent
            balances.append(balance)
    return balances


def update_balance(db, month, budget):
    balances = get_balance(db, month, budget)
    c = db.cursor()

    # check if balance for this month already exists
    command = "SELECT * FROM balance WHERE month=?"
    c.execute(command, (month,))
    result = c.fetchall()
    if len(result) > 0:
        # this exists, so need to update
        command = """
        DELETE FROM balance
        WHERE month=?
        """
        c.execute(command, (month,))
        db.commit()

    command = """
    INSERT INTO balance
    VALUES (?%s)
    """ % ',?'*len(balances)
    params = [month] + balances
    c.execute(command, tuple(params))
    db.commit()

    return db


def fetch_month_entries(db, month, item=None):
    c = db.cursor()
    if item is None:
        command = """
        SELECT * FROM entries
        WHERE month=?
        ORDER BY id ASC
        """
        t = (month,)
    else:
        command = """
        SELECT * FROM entries
        WHERE month=? AND
        item=?
        ORDER BY id ASC
        """
        t = (month, item,)
    c.execute(command, t)
    entries = c.fetchall()
    return entries


if __name__ == "__main__":
    print(current_date())
    print(current_date(True))