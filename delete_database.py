import django
django.setup()
from polls.models import Ballot

import datetime
import calendar

starting_day = #19
starting_month = #10
ending_month = #12
year = #2016


def delete_db_monthly_entries(y, m, d):
    for d in range(d, calendar.monthrange(y, m)[1] + 1):
        if calendar.weekday(y, m, d) < 5:
            b = Ballot.objects.get(date = datetime.date(y, m, d))
            print(b, b.id)
            b.delete()

delete_db_monthly_entries(year, starting_month, starting_day)
for m in range(starting_month + 1, ending_month + 1):
    delete_db_monthly_entries(year, m, 1)
