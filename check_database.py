#!/usr/bin/env python3

import django
django.setup()

from polls.models import Ballot, Restaurant, Feedback, Ranking

for b in Ballot.objects.all():
    print(b, b.id, b.winner, b.win_cause)

for r in Restaurant.objects.all():
    print(r, r.id, r.ballot, r.votes)

for f in Feedback.objects.all():
    print(f, f.id, f.ballot, f.restaurant, f.mark, f.comment)

for r in Ranking.objects.all():
    print(r, r.id, r.restaurant)
