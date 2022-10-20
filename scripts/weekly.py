from app.models import get_report


def run(*args):
    if args:
        week = f"2022W{args[0]}5"
    else:
        week = None
    print(get_report(week_number=week, driver=False, sleep=0, headless=True))



