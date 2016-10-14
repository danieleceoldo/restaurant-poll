import django
django.setup()
from polls.models import Ballot, Restaurant, Ranking

import datetime
import calendar

starting_day = 19
starting_month = 9
ending_month = 12
year = 2016

restaurant_list = ("Aratro", "2 Chef", "Calabianca", "Concorde")

def create_db_monthly_entries(y, m, d):
    for d in range(d, calendar.monthrange(y, m)[1] + 1):
        if calendar.weekday(y, m, d) < 5:
            b = Ballot.objects.create(date = datetime.date(y, m, d))
            print(b, b.id)
            for r in restaurant_list:
                Restaurant.objects.create(ballot = b, name = r)

create_db_monthly_entries(year, starting_month, starting_day)
for m in range(starting_month + 1, ending_month + 1):
    create_db_monthly_entries(year, m, 1)

for restaurant in restaurant_list:
    Ranking.objects.create(restaurant=restaurant)
