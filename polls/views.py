from django.shortcuts import render

# Create your views here.

from django.shortcuts import get_object_or_404

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from django.utils import timezone
import pytz
from datetime import date, timedelta

import random

from .models import Ballot, Restaurant, Feedback, Ranking

poll_time_frame = { 
    'start': {'hour': 12, 'minute': 00},
    'end':   {'hour': 12, 'minute': 30} 
}
feedback_time_frame = {
    'start': {'hour': 13, 'minute': 15},
    'end':   {'hour': 16, 'minute': 30}
}



def index(request):
    ballot = Ballot.objects.get(date=date.today())
    return HttpResponseRedirect(reverse('polls:vote_detail', args=(ballot.id,)))


def vote_detail(request, ballot_id):
    timezone.activate(pytz.timezone('Europe/Rome'))
    now = timezone.localtime(timezone.now())
    poll_open_time = now.replace(microsecond=0, second=0,
         minute=poll_time_frame['start']['minute'],
         hour=poll_time_frame['start']['hour'])
    poll_close_time = now.replace(microsecond=0, second=0,
         minute=poll_time_frame['end']['minute'],
         hour=poll_time_frame['end']['hour'])

    if now < poll_open_time:
        template_name = 'polls/vote_waiting.html'
    elif now < poll_close_time:
        template_name = 'polls/vote_detail.html'
    else:
        return HttpResponseRedirect(reverse('polls:vote_result', args=(ballot_id,)))

    context = {'ballot': get_object_or_404(Ballot, pk=ballot_id),
               'poll_open_time': poll_open_time,
               'poll_close_time': poll_close_time}
    return render(request, template_name, context)


def feedback_detail(request, ballot_id):
    feedback_marks = [
        {'phrase': 'I really liked it', 'value': 2},
        {'phrase': 'I liked it', 'value': 1},
        {'phrase': 'I don\'t know', 'value': 0},
        {'phrase': 'I disliked it', 'value': -1},
        {'phrase': 'I really disliked it', 'value': -2}
    ]
    timezone.activate(pytz.timezone('Europe/Rome'))
    now = timezone.localtime(timezone.now())
    feedback_open_time = now.replace(microsecond=0, second=0,
         minute=feedback_time_frame['start']['minute'],
         hour=feedback_time_frame['start']['hour'])
    feedback_close_time = now.replace(microsecond=0, second=0,
         minute=feedback_time_frame['end']['minute'],
         hour=feedback_time_frame['end']['hour'])
    ballot = get_object_or_404(Ballot, pk=ballot_id)

    if feedback_open_time < now < feedback_close_time:
        template_name = 'polls/feedback_detail.html'
    else:
        template_name = 'polls/feedback_waiting.html'

    context = {'ballot': ballot,
               'feedback_marks': feedback_marks,
               'feedback_open_time': feedback_open_time,
               'feedback_close_time': feedback_close_time}
    return render(request, template_name, context)


class VoteHistoryIndexView(generic.ListView):
    template_name = 'polls/vote_history_index.html'
    context_object_name = 'ballot_list'

    def get_queryset(self):
        return Ballot.objects.filter(date__lt=date.today()).order_by('-date')


class VoteResultHistoryView(generic.DetailView):
    model = Ballot
    template_name = 'polls/vote_result_history.html'


class FeedbackHistoryView(generic.ListView):
    template_name = 'polls/feedback_history.html'
    context_object_name = 'feedback_list'

    def get_queryset(self):
        return Feedback.objects.all().order_by('-id')


def vote_result(request, ballot_id):
    timezone.activate(pytz.timezone('Europe/Rome'))
    now = timezone.localtime(timezone.now())
    poll_open_time = now.replace(microsecond=0, second=0,
         minute=poll_time_frame['start']['minute'],
         hour=poll_time_frame['start']['hour'])
    poll_close_time = now.replace(microsecond=0, second=0,
         minute=poll_time_frame['end']['minute'],
         hour=poll_time_frame['end']['hour'])
    feedback_open_time = now.replace(microsecond=0, second=0,
         minute=feedback_time_frame['start']['minute'],
         hour=feedback_time_frame['start']['hour'])
    feedback_close_time = now.replace(microsecond=0, second=0,
         minute=feedback_time_frame['end']['minute'],
         hour=feedback_time_frame['end']['hour'])
    ballot = get_object_or_404(Ballot, pk=ballot_id)

    if now < poll_open_time:
        template_name = 'polls/vote_waiting.html'
    elif now < poll_close_time:
        template_name = 'polls/voting.html'
    else:
        if ballot.winner == "":
            win_name = []
            for restaurant in ballot.restaurant_set.all():
                if len(win_name) == 0:
                    win_name = [restaurant.name]
                    win_vote = restaurant.votes
                elif restaurant.votes > win_vote:
                    win_name = [restaurant.name]
                    win_vote = restaurant.votes
                elif restaurant.votes == win_vote:
                    win_name.append(restaurant.name)
            if len(win_name) == 1:
                ballot.winner = win_name[0]
                ballot.win_cause = 'Majority Vote' 
            else:
                selected = []
                for name in win_name:
                    restaurant = Ranking.objects.get(restaurant=name)
                    name_mark = 0
                    for feedback in restaurant.feedback_set.all():
                        name_mark += feedback.mark
                    if len(selected) == 0:
                        selected = [name]
                        max_mark = name_mark
                    elif name_mark > max_mark:
                        selected = [name]
                        max_mark = name_mark
                    elif name_mark == max_mark:
                        selected.append(name)
                if len(selected) == 1:
                    ballot.winner = selected[0]
                    ballot.win_cause = 'Best Feedback'
                else:
                    new_selected = []
                    max_fn = 1
                    for name in selected:
                        name_fn = Ranking.objects.get(restaurant=name).feedback_set.count()
                        if name_fn > max_fn:
                            new_selected = [name]
                            max_fn = name_fn
                        elif name_fn == max_fn:
                            new_selected.append(name)
                    if len(new_selected) == 1:
                         ballot.winner = new_selected[0]
                         ballot.win_cause = 'Most Rated'
                    elif len(new_selected) == 0:
                         ballot.winner = random.choice(win_name)
                         ballot.win_cause = 'Random No Feedback'
                    else:
                         ballot.winner = random.choice(new_selected)
                         ballot.win_cause = 'Random Same Feedback'
            ballot.save()
        template_name = 'polls/vote_result.html'

    total_votes = 0
    for restaurant in Ballot.objects.get(pk=ballot_id).restaurant_set.all():
        total_votes += restaurant.votes
    total_marks = 0
    for feedback in Ballot.objects.get(pk=ballot_id).feedback_set.all():
        total_marks +=  feedback.mark
    feedback_num = Ballot.objects.get(pk=ballot_id).feedback_set.count()
    context = {'ballot': ballot,
               'total_votes': total_votes,
               'total_marks': total_marks,
               'feedback_num': feedback_num,
               'poll_open_time': poll_open_time,
               'poll_close_time': poll_close_time,
               'feedback_open_time': feedback_open_time,
               'feedback_close_time': feedback_close_time}
    return render(request, template_name, context)


def statistics(request):
    stat = []
    stat_index = {}
    for name in Ranking.objects.all():
        stat.append(
            {'name': name.restaurant, 'win': 0, 'parity': 0, 'vote': 0,
             'majority': 0, 'feedback': 0, 'most_rated': 0, 'rand_feedback': 0,
             'rand_no_feedback': 0, 'mark': 0, 'feedback_num': 0}
        )
    for x in stat:
        stat_index[x['name']] = stat.index(x)
    
    ballot_dates = Ballot.objects.filter(date__lt=date.today()).order_by('date')
    for ballot in ballot_dates:
        if ballot.winner != '':
            stat[stat_index[ballot.winner]]['win'] += 1
            if ballot.win_cause == 'Majority Vote':
                stat[stat_index[ballot.winner]]['majority'] += 1
            elif ballot.win_cause == 'Best Feedback':
                stat[stat_index[ballot.winner]]['feedback'] += 1
            elif ballot.win_cause == 'Most Rated':
                stat[stat_index[ballot.winner]]['most_rated'] += 1
            elif ballot.win_cause == 'Random Same Feedback':
                stat[stat_index[ballot.winner]]['rand_feedback'] += 1
            elif ballot.win_cause == 'Random No Feedback':
                stat[stat_index[ballot.winner]]['rand_no_feedback'] += 1
            win_vote = 0
            win_name = []
            for restaurant in ballot.restaurant_set.all():
                stat[stat_index[restaurant.name]]['vote'] += restaurant.votes
                if restaurant.votes > win_vote:
                    win_name = [restaurant.name]
                    win_vote = restaurant.votes
                elif restaurant.votes == win_vote:
                    win_name.append(restaurant.name)
        if len(win_name) > 1:
            for name in win_name:
                stat[stat_index[name]]['parity'] += 1
    for name in Ranking.objects.all():
        for feedback in name.feedback_set.all():
            stat[stat_index[name.restaurant]]['mark'] += feedback.mark
        stat[stat_index[name.restaurant]]['feedback_num'] = name.feedback_set.count()

    if ballot_dates:
        context = {
            'stat': stat,
            'from_ballot_date' : ballot_dates[0],
            'to_ballot_date' : ballot_dates[len(ballot_dates)-1]
        }
    else:
        context = {}

    return render(request, 'polls/statistics.html', context)


def vote(request, ballot_id):
    ballot = get_object_or_404(Ballot, pk=ballot_id)
    try:
        selected_restaurant = ballot.restaurant_set.get(pk=request.POST['restaurant'])
    except (KeyError, Restaurant.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/vote_detail.html', {
            'ballot': ballot,
            'error_message': "You didn't select a restaurant.",
        })
    else:
        selected_restaurant.votes += 1
        selected_restaurant.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:vote_result', args=(ballot.id,)))


def feedback(request, ballot_id):
    ballot = get_object_or_404(Ballot, pk=ballot_id)
    selected_mark = int(request.POST['mark'])
    posted_comment = request.POST['comment']
    restaurant = Ranking.objects.get(restaurant=ballot.winner)
    Feedback.objects.create(ballot=ballot, restaurant=restaurant,
        mark = selected_mark, comment = posted_comment
    )
            
    return HttpResponseRedirect(reverse('polls:vote_result', args=(ballot.id,)))

