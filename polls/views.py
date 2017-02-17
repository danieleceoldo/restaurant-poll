#
# project: restaurant-poll
# author: Daniele Ceoldo
# 
#
#
# This file is part of restaurant-poll.
#
# restaurant-poll is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# restauran-poll is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with restaurant-poll.  If not, see <http://www.gnu.org/licenses/>.
#



from django.shortcuts import render, get_object_or_404

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from datetime import datetime, timedelta
from django.utils import timezone

import random

from .models import Ballot, Restaurant, Feedback, Ranking

from os import system, path, chdir, getcwd, stat

from django.contrib.auth.decorators import login_required


poll_restaurant_list = sorted(("Aratro", "2 Chef", "Calabianca", "Concorde"))

poll_time_frame = {
    'start': {'hour': 12, 'minute': 00},
    'end':   {'hour': 19, 'minute': 30}
}

feedback_time_frame = {
    'start': {'hour': 13, 'minute': 15},
    'end':   {'hour': 16, 'minute': 30}
}

feedback_marks = [
    {'phrase': 'I really liked it', 'value': 2},
    {'phrase': 'I liked it', 'value': 1},
    {'phrase': 'I don\'t know', 'value': 0},
    {'phrase': 'I disliked it', 'value': -1},
    {'phrase': 'I really disliked it', 'value': -2}
]



def index(request):

    now = timezone.localtime(timezone.now())
    poll_open_time = now.replace(microsecond=0, second=0,
        minute=poll_time_frame['start']['minute'],
        hour=poll_time_frame['start']['hour'])
    poll_close_time = now.replace(microsecond=0, second=0,
        minute=poll_time_frame['end']['minute'],
        hour=poll_time_frame['end']['hour'])
    feedback_close_time = now.replace(microsecond=0, second=0,
        minute=feedback_time_frame['end']['minute'],
        hour=feedback_time_frame['end']['hour'])

    if now > feedback_close_time:
        ballot_dates = Ballot.objects.filter(date__lte=now.date()).order_by('date')
    else:
        ballot_dates = Ballot.objects.filter(date__lt=now.date()).order_by('date')


    # Graph generation

    if ballot_dates.count() != 0 and path.exists('polls/static/polls/'):

        old_wd = getcwd()
        chdir('polls/static/polls/')

        # The feedback image file must ALWAYS be present in the directory
        feedback_graph_stat_mtime = timezone.make_aware(datetime.fromtimestamp(stat('images/feedback_graph.png').st_ctime))

        # Graphs need to be updated if some time has passed
        if now > feedback_graph_stat_mtime + timedelta(minutes=15):

            # Feedback Graph
            f = open('feedback_graph_data.txt','w')
            for name in Ranking.objects.all():
                f.write('# ' + str(name.restaurant) + '\n')
                mark = 0
                for ballot in ballot_dates:
                    if ballot.winner == name.restaurant:
                        for feedback in ballot.feedback_set.all():
                            mark += feedback.mark
                    f.write(str(mark) + '\n')
                f.write('\n\n')
            f.close()

            f = open('generate_feedback_graph.gnuplot','w')
            f.write('set terminal png medium size 640,480\n')
            f.write('set output "feedback_graph.png"\n')
            f.write('set xlabel "Days"\n')
            f.write('show xlabel\n')
            f.write('set ylabel "Mark"\n')
            f.write('show ylabel\n')
            f.write('set grid\n')
            f.write('show grid\n')
            f.write('set key left top\n')
            f.write('show key\n')
            f.write('set title "Feedback History" font "sans, 14"\n')
            f.write('show title\n')
            plot_str = ""
            for name in Ranking.objects.all():
                plot_str += ' "feedback_graph_data.txt" index "' + name.restaurant + '" with lines title "' + name.restaurant + '" linewidth 3,'
            f.write('plot' + plot_str + '\n')
            f.close()

            system('gnuplot generate_feedback_graph.gnuplot')
            system('mv feedback_graph.png images')


            # Win History Graph
            restaurant_list = []
            for name in Ranking.objects.all():
                restaurant_list.append(name.restaurant)
            restaurant_list.sort()

            f = open('win_history_graph_data.txt','w')
            for ballot in ballot_dates:
                f.write(str(restaurant_list.index(ballot.winner)) + '\n')
            f.close()

            f = open('generate_win_history_graph.gnuplot','w')
            f.write('set terminal png medium size 640,480\n')
            f.write('set output "win_history_graph.png"\n')
            f.write('set xlabel "Days"\n')
            f.write('show xlabel\n')
            f.write('set grid\n')
            f.write('set grid noxtics\n')
            f.write('show grid\n')
            f.write('set key off\n')
            f.write('set yrange [-1:4]\n')
            f.write('show yrange\n')
            f.write('set xrange [-1:]\n')
            f.write('show xrange\n')
            f.write('set pointsize 2\n')
            f.write('set title "Win History" font "sans, 14"\n')
            f.write('show title\n')
            ytics_str = ""
            for name in restaurant_list:
                ytics_str += '"' + name + '" ' + str(restaurant_list.index(name)) + ", "
            f.write('set ytics (' + ytics_str + ')\n')
            f.write('plot "win_history_graph_data.txt" with points pointtype 5\n')
            f.close()

            system('gnuplot generate_win_history_graph.gnuplot')
            system('mv win_history_graph.png images')


            # Win Graph
            win = []
            for x in restaurant_list:
                win.append(0)

            for ballot in ballot_dates:
                win[restaurant_list.index(ballot.winner)] += 1

            f = open('win_graph_data.txt','w')
            for x in win:
                f.write(str(x) + '\n')
            f.close()

            f = open('generate_win_graph.gnuplot','w')
            f.write('set terminal png medium size 640,480\n')
            f.write('set output "win_graph.png"\n')
            f.write('set ylabel "Wins"\n')
            f.write('show ylabel\n')
            f.write('set grid\n')
            f.write('set grid noxtics\n')
            f.write('show grid\n')
            f.write('set yrange [0:' + str(max(win)+2)  + ']\n')
            f.write('show yrange\n')
            f.write('set key off\n')
            f.write('set boxwidth 1.5 relative\n')
            f.write('set style fill pattern 2\n')
            f.write('set title "Wins" font "sans, 14"\n')
            f.write('show title\n')
            xtics_str = ""
            for name in restaurant_list:
                xtics_str += '"' + name + '" ' + str(restaurant_list.index(name)) + ", "
            f.write('set xtics (' + xtics_str + ')\n')
            f.write('plot "win_graph_data.txt" with histogram\n')
            f.close()

            system('gnuplot generate_win_graph.gnuplot')
            system('mv win_graph.png images')


            # Linear Weighted Simple Moving Average Feedback Graph
            samples = 30
            f = open('feedback_lwsma_graph_data.txt','w')
            for name in Ranking.objects.all():
                f.write('# ' + str(name.restaurant) + '\n')
                for ballot in ballot_dates:
                    mark_lwsma = 0
                    sample_num = samples
                    for ballot_filt in ballot_dates.filter(date__lte=ballot.date).order_by('-date')[:samples]:
                        if ballot_filt.winner == name.restaurant:
                            for feedback in ballot_filt.feedback_set.all():
                                mark_lwsma += feedback.mark * sample_num / samples
                        sample_num -= 1
                    f.write(str(mark_lwsma) + '\n')
                f.write('\n\n')
                name.lwsma_feedback = mark_lwsma
                name.save()
            f.close()

            f = open('generate_feedback_lwsma_graph.gnuplot','w')
            f.write('set terminal png medium size 640,480\n')
            f.write('set output "feedback_lwsma_graph.png"\n')
            f.write('set xlabel "Days"\n')
            f.write('show xlabel\n')
            f.write('set ylabel "Mark"\n')
            f.write('show ylabel\n')
            f.write('set grid\n')
            f.write('show grid\n')
            f.write('set key left top\n')
            f.write('show key\n')
            f.write('set title "Linear Weighted Simple Moving Average Feedback History" font "sans, 14"\n')
            f.write('show title\n')
            plot_str = ""
            for name in Ranking.objects.all():
                plot_str += ' "feedback_lwsma_graph_data.txt" index "' + name.restaurant + '" with lines title "' + name.restaurant + '" linewidth 3,'
            f.write('plot' + plot_str + '\n')
            f.close()

            system('gnuplot generate_feedback_lwsma_graph.gnuplot')
            system('mv feedback_lwsma_graph.png images')


            # Simple Moving Average Feedback Graph
            samples = 30
            f = open('feedback_sma_graph_data.txt','w')
            for name in Ranking.objects.all():
                f.write('# ' + str(name.restaurant) + '\n')
                for ballot in ballot_dates:
                    mark_lwsma = 0
                    sample_num = samples
                    for ballot_filt in ballot_dates.filter(date__lte=ballot.date).order_by('-date')[:samples]:
                        if ballot_filt.winner == name.restaurant:
                            for feedback in ballot_filt.feedback_set.all():
                                mark_lwsma += feedback.mark
                        sample_num -= 1
                    f.write(str(mark_lwsma) + '\n')
                f.write('\n\n')
            f.close()

            f = open('generate_feedback_sma_graph.gnuplot','w')
            f.write('set terminal png medium size 640,480\n')
            f.write('set output "feedback_sma_graph.png"\n')
            f.write('set xlabel "Days"\n')
            f.write('show xlabel\n')
            f.write('set ylabel "Mark"\n')
            f.write('show ylabel\n')
            f.write('set grid\n')
            f.write('show grid\n')
            f.write('set key left top\n')
            f.write('show key\n')
            f.write('set title "Simple Moving Average Feedback History" font "sans, 14"\n')
            f.write('show title\n')
            plot_str = ""
            for name in Ranking.objects.all():
                plot_str += ' "feedback_sma_graph_data.txt" index "' + name.restaurant + '" with lines title "' + name.restaurant + '" linewidth 3,'
            f.write('plot' + plot_str + '\n')
            f.close()

            system('gnuplot generate_feedback_sma_graph.gnuplot')
            system('mv feedback_sma_graph.png images')


        chdir(old_wd)

        graphs = True

    else:

        graphs = False


    # View decision

    # Check whether we need to wait for todays' poll
    if now < poll_open_time:

        context = {'poll_waiting': True,
                   'poll_open_time': poll_open_time,
                   'poll_close_time': poll_close_time,
                   'graphs': graphs}

    # Check whether poll is open
    elif now < poll_close_time:

        for restaurant in poll_restaurant_list:
            if Ranking.objects.filter(restaurant=restaurant).count() == 0:
                Ranking.objects.create(restaurant=restaurant)

        if Ballot.objects.filter(date=now.date()).count() == 0:
            ballot = Ballot.objects.create(date = now.date())
            for ranking in Ranking.objects.all():
                Restaurant.objects.create(ballot=ballot,
                        name=ranking.restaurant)
        else:
            ballot = Ballot.objects.get(date=now.date())

        total_votes = 0
        for restaurant in ballot.restaurant_set.all():
            total_votes += restaurant.votes

        context = {'poll_open': True,
                   'ballot': ballot,
                   'total_votes': total_votes,
                   'poll_close_time': poll_close_time,
                   'graphs': graphs}

    # Otherwise the time for poll is over for today
    else:

        # Check if the ballot has been created
        if Ballot.objects.filter(date=now.date()).count() == 0:
            context = {'poll_void': True,
                       'graphs': graphs}
        else:
            ballot = Ballot.objects.get(date=now.date())


            # Winner decision

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
                        if len(selected) == 0:
                            selected = [name]
                            best_feedback = restaurant.lwsma_feedback
                        elif restaurant.lwsma_feedback > best_feedback:
                            selected = [name]
                            best_feedback = restaurant.lwsma_feedback
                        elif restaurant.lwsma_feedback == best_feedback:
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

            total_votes = 0
            for restaurant in ballot.restaurant_set.all():
                total_votes += restaurant.votes

            # Check if any vote has been cast in case delete the ballot
            if total_votes == 0:
                ballot.delete()
                return HttpResponseRedirect(reverse('polls:index'))

            total_marks = 0
            for feedback in ballot.feedback_set.all():
                total_marks +=  feedback.mark
            feedback_num = ballot.feedback_set.count()

            feedback_open_time = now.replace(microsecond=0, second=0,
                minute=feedback_time_frame['start']['minute'],
                hour=feedback_time_frame['start']['hour'])
            feedback_close_time = now.replace(microsecond=0, second=0,
                minute=feedback_time_frame['end']['minute'],
                hour=feedback_time_frame['end']['hour'])

            context = {'poll_closed': True,
                       'ballot': ballot,
                       'total_votes': total_votes,
                       'total_marks': total_marks,
                       'feedback_num': feedback_num,
                       'poll_open_time': poll_open_time,
                       'poll_close_time': poll_close_time,
                       'feedback_open_time': feedback_open_time,
                       'feedback_close_time': feedback_close_time,
                       'graphs': graphs}


    return render(request, 'polls/index.html', context)



#@login_required
def vote_detail(request):
    now = timezone.localtime(timezone.now())
    poll_open_time = now.replace(microsecond=0, second=0,
        minute=poll_time_frame['start']['minute'],
        hour=poll_time_frame['start']['hour'])
    poll_close_time = now.replace(microsecond=0, second=0,
        minute=poll_time_frame['end']['minute'],
        hour=poll_time_frame['end']['hour'])

    if poll_open_time < now < poll_close_time:

        if Ballot.objects.filter(date=now.date()).count() == 1:
            ballot = Ballot.objects.get(date=now.date())
            context = {'ballot': ballot,
                       'poll_close_time': poll_close_time}
            return render(request, 'polls/vote_detail.html', context)

    return HttpResponseRedirect(reverse('polls:index'))



#@login_required
def feedback_detail(request):
    now = timezone.localtime(timezone.now())
    feedback_open_time = now.replace(microsecond=0, second=0,
        minute=feedback_time_frame['start']['minute'],
        hour=feedback_time_frame['start']['hour'])
    feedback_close_time = now.replace(microsecond=0, second=0,
        minute=feedback_time_frame['end']['minute'],
        hour=feedback_time_frame['end']['hour'])

    if feedback_open_time < now < feedback_close_time:
        template_name = 'polls/feedback_detail.html'
        if Ballot.objects.filter(date=now.date()).count() == 0:
            context = {'error_message': 'No vote has been cast. Poll is over, no feedback can be submitted.'}
        else:
            context = {'feedback_marks': feedback_marks}
    else:
        template_name = 'polls/feedback_waiting.html'
        context = {'feedback_open_time': feedback_open_time,
                   'feedback_close_time': feedback_close_time}

    return render(request, template_name, context)



class VoteHistoryIndexView(generic.ListView):
    template_name = 'polls/vote_history_index.html'
    context_object_name = 'ballot_list'

    def get_queryset(self):
        now = timezone.localtime(timezone.now())
        poll_close_time = now.replace(microsecond=0, second=0,
            minute=poll_time_frame['end']['minute'],
            hour=poll_time_frame['end']['hour'])
        if now > poll_close_time:
            return Ballot.objects.filter(date__lte=now.date()).order_by('-date')
        else:
            return Ballot.objects.filter(date__lt=now.date()).order_by('-date')



def vote_result_history(request, ballot_id):
    ballot = get_object_or_404(Ballot, pk=ballot_id)
    result_detail = []
    total_votes = 0
    for restaurant in ballot.restaurant_set.all():
        result_detail.append({'name': restaurant.name, 'votes': restaurant.votes})
        total_votes += restaurant.votes
    template_name = 'polls/vote_result_history.html'
    result_detail.sort(key=lambda x: (x['votes'], x['name']), reverse=True)
    context = {
            'ballot': ballot,
            'result_detail': result_detail,
            'total_votes': total_votes
            }
    return render(request, template_name, context)



def vote_result_history_prev(request, ballot_id):
    ballot_id_list = []
    for ballot in Ballot.objects.all():
        ballot_id_list.append(ballot.id)
    curr_pos = ballot_id_list.index(int(ballot_id))
    if curr_pos == 0:
        new_ballot_id = ballot_id
    else:
        new_ballot_id = ballot_id_list[curr_pos  - 1]
    return HttpResponseRedirect(reverse('polls:vote_result_history',
        args=(new_ballot_id,)))



def vote_result_history_next(request, ballot_id):

    now = timezone.localtime(timezone.now())
    poll_open_time = now.replace(microsecond=0, second=0,
        minute=poll_time_frame['start']['minute'],
        hour=poll_time_frame['start']['hour'])
    poll_close_time = now.replace(microsecond=0, second=0,
        minute=poll_time_frame['end']['minute'],
        hour=poll_time_frame['end']['hour'])

    ballot_id_list = []
    for ballot in Ballot.objects.all():
        ballot_id_list.append(ballot.id)
    curr_pos = ballot_id_list.index(int(ballot_id))

    # Calculate last position avoiding security hole during voting
    if (poll_open_time < now < poll_close_time) and (Ballot.objects.filter(date=now.date()).count() == 1):
        last_pos = len(ballot_id_list) - 2
    else:
        last_pos = len(ballot_id_list) - 1

    if curr_pos == last_pos:
        new_ballot_id = ballot_id
    else:
        new_ballot_id = ballot_id_list[curr_pos  + 1]
    return HttpResponseRedirect(reverse('polls:vote_result_history',
        args=(new_ballot_id,)))



class FeedbackHistoryView(generic.ListView):
    template_name = 'polls/feedback_history.html'
    context_object_name = 'feedback_list'

    def get_queryset(self):
        return Feedback.objects.all().order_by('-id')



def statistics(request):
    stat = []
    stat_index = {}
    for name in Ranking.objects.all():
        stat.append( {
            'name': name.restaurant, 'win': 0, 'parity': 0, 'vote': 0,
            'majority': 0, 'feedback': 0, 'most_rated': 0, 'rand_feedback': 0,
            'rand_no_feedback': 0, 'mark': 0, 'feedback_num': 0
            } )
    for x in stat:
        stat_index[x['name']] = stat.index(x)

    now = timezone.localtime(timezone.now())
    poll_close_time = now.replace(microsecond=0, second=0,
        minute=poll_time_frame['end']['minute'],
        hour=poll_time_frame['end']['hour'])

    if now > poll_close_time:
        ballot_dates = Ballot.objects.filter(date__lte=now.date()).order_by('date')
    else:
        ballot_dates = Ballot.objects.filter(date__lt=now.date()).order_by('date')

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
    stat.sort(key=lambda x: (x['win'], x['mark'], x['feedback_num'],
        x['parity'], x['vote'], x['name']), reverse=True)

    if ballot_dates:
        context = {
                'stat': stat,
                'from_ballot_date' : ballot_dates[0],
                'to_ballot_date' : ballot_dates[len(ballot_dates)-1]
                }
    else:
        context = {}

    return render(request, 'polls/statistics.html', context)



#@login_required
def vote(request):
    now = timezone.localtime(timezone.now())
    poll_open_time = now.replace(microsecond=0, second=0,
        minute=poll_time_frame['start']['minute'],
        hour=poll_time_frame['start']['hour'])
    poll_close_time = now.replace(microsecond=0, second=0,
        minute=poll_time_frame['end']['minute'],
        hour=poll_time_frame['end']['hour'])

    if (poll_open_time < now < poll_close_time) and (Ballot.objects.all().count() != 0):

        ballot = Ballot.objects.get(date=timezone.localtime(timezone.now()).date())
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
            return HttpResponseRedirect(reverse('polls:index'))
    else:
        return HttpResponseRedirect(reverse('polls:index'))



#@login_required
def feedback(request):
    now = timezone.localtime(timezone.now())
    feedback_open_time = now.replace(microsecond=0, second=0,
        minute=feedback_time_frame['start']['minute'],
        hour=feedback_time_frame['start']['hour'])
    feedback_close_time = now.replace(microsecond=0, second=0,
        minute=feedback_time_frame['end']['minute'],
        hour=feedback_time_frame['end']['hour'])

    if feedback_open_time < now < feedback_close_time:
        if Ballot.objects.filter(date=now.date()).count() == 0:
            return render(request, 'polls/feedback_detail.html', {
                'error_message': 'No vote has been cast. Poll is over, no feedback can be submitted.'
            })
        else:
            ballot = Ballot.objects.get(date=timezone.localtime(timezone.now()).date())
            try:
                selected_mark = int(request.POST['mark'])
            except:
                return HttpResponseRedirect(reverse('polls:feedback_detail'))
            else:
                posted_comment = request.POST['comment']
                restaurant = Ranking.objects.get(restaurant=ballot.winner)
                Feedback.objects.create(ballot=ballot, restaurant=restaurant,
                    mark = selected_mark, comment = posted_comment
                )
                return HttpResponseRedirect(reverse('polls:index'))
    else:
        template_name = 'polls/feedback_waiting.html'
        context = {'feedback_open_time': feedback_open_time,
                   'feedback_close_time': feedback_close_time}
        return render(request, template_name, context)


# end of file
