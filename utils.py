import datetime


def current_date(month=False):
    now = str(datetime.date.today())
    if month:
        # remove the day
        now = now[:-3]
    return now.translate(None, "-")


if __name__ == "__main__":
    print(current_date())
    print(current_date(True))