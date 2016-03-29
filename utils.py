import datetime
from sqlite3 import OperationalError


def current_date(month=False):
    now = str(datetime.date.today())
    if month:
        # remove the day
        now = now[:-3]
    return now.translate(None, "-")


def table_exists(cursor, table):
    # check if the table exists
    try:
        cursor.execute("SELECT * FROM %s" % table)
        exists = True
    except OperationalError:
        exists = False
    return exists


def build_entry_table(db):
    c = db.cursor()

    if table_exists(c, 'entries'):
        return db

    command = """
    CREATE TABLE entries
    (id INTEGER PRIMARY KEY ASC, month TEXT, date TEXT, price REAL, category TEXT, item TEXT, note TEXT)
    """
    c.execute(command)
    db.commit()
    return db


def build_budget_table(db, budget):
    c = db.cursor()

    # check if the table exists
    if table_exists(c, 'budget'):
        return db

    # build the sql query
    params = []
    command = "CREATE TABLE budget (month TEXT, total REAL"
    for top_level in budget:
        for lower in budget[top_level]:
            command = command + ", " + lower + " REAL"
    command += ")"

    # create it
    c.execute(command)
    db.commit()
    return db


def build_balance_table(db):
    c = db.cursor()

    # check if the table exists
    if table_exists(c, 'balances'):
        return db

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
    all_entries = fetch_month_entries(db, month)
    total = sum_entries(all_entries)
    # iterate over keys, to update individual balances
    balances = [total]
    balance_dict = dict()
    balance_dict['total'] = total
    for top in budget:
        balance_dict[top] = dict()
        top_sum = 0
        for low in budget[top]:
            ent = fetch_month_entries(db, month, low)
            sum_ent = sum_entries(ent)
            item_budget = get_budget_entry(db, month, low)
            balance = int(item_budget) - int(sum_ent)
            top_sum += balance
            balances.append(balance)
            balance_dict[top][low] = balance
        balance_dict[top]['total'] = top_sum
    return balances, balance_dict


def update_balance(db, month, budget):
    balances, _ = get_balance(db, month, budget)
    c = db.cursor()

    # check if balance for this month already exists
    command = "SELECT * FROM balances WHERE month=?"
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

    question_marks = ',?'*len(balances)
    command = """
    INSERT INTO balances
    VALUES (?%s)
    """ % question_marks
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


def write_entry(db, data):
    # data is a dict to write
    c = db.cursor()
    command = """
    INSERT INTO entries
    VALUES
    (NULL, ?, ?, ?, ?, ?, ?)
    """
    params = (data['month'],
              data['date'],
              data['price'],
              data['category'],
              data['item'],
              data['note'],)
    c.execute(command, params)
    db.commit()
    return db


def delete_entry(db, id):
    # id is the uid of the entry to be deleted
    c = db.cursor()
    command = """
    DELETE FROM entries
    WHERE id=?
    """
    c.execute(command, (id,))
    db.commit()
    return db


if __name__ == "__main__":
    print(current_date())
    print(current_date(True))