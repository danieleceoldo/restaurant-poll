from django.test import TestCase

# Create your tests here.

from django.urls import reverse
from .models import Ballot, Restaurant, Feedback, Ranking

from datetime import datetime, timedelta
from django.utils import timezone


from unittest.mock import patch

POLL_TIME = timezone.make_aware(datetime(2016, 10, 26))
POLL_DATE = POLL_TIME.date()

def MockedDateToday():
    return POLL_DATE

def MockedTimezoneNow_PollWait():
    return POLL_TIME.replace(hour=10)

def MockedTimezoneNow_PollOpen():
    return POLL_TIME.replace(hour=12, minute=15)

def MockedTimezoneNow_PollClosed():
    return POLL_TIME.replace(hour=13)

def MockedTimezoneNow_FeedbackWait():
    return POLL_TIME.replace(hour=10)

def MockedTimezoneNow_FeedbackOpen():
    return POLL_TIME.replace(hour=14)

def MockedTimezoneNow_FeedbackClosed():
    return POLL_TIME.replace(hour=17)



class IndexTests(TestCase):

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollWait)
    def test_index_poll_closed(self):
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, '<p>Waiting for poll.</p>', html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollOpen)
    def test_index_poll_open(self):
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, '<input type="submit" value="Vote" />', html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_index_poll_over_no_cast(self):
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, '<strong>No vote has been cast. Poll is over, no result is available.</strong>', html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_index_poll_over_winner(self):
        ballot = Ballot.objects.create(date=POLL_DATE,
                winner='test_restaurant', win_cause='Majority Vote')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant',
                votes=1)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, '<h2>The Winner is: test_restaurant</h2>', html=True)
        self.assertContains(response, '<h3>Total votes: 1</h3>', html=True)
        self.assertContains(response, '<p>Victory cause: <strong>Majority Vote</strong></p>', html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_index_poll_over_total_votes(self):
        ballot = Ballot.objects.create(date=POLL_DATE,
                winner='test_restaurant_1', win_cause='Majority Vote')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_1',
                votes=2)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_2',
                votes=1)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, '<h2>The Winner is: test_restaurant_1</h2>', html=True)
        self.assertContains(response, '<h3>Total votes: 3</h3>', html=True)
        self.assertContains(response, '<p>Victory cause: <strong>Majority Vote</strong></p>', html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_index_poll_over_win_alg_maj_vic(self):
        ballot = Ballot.objects.create(date=POLL_DATE)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant',
                votes=1)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, '<h2>The Winner is: test_restaurant</h2>', html=True)
        self.assertContains(response, '<h3>Total votes: 1</h3>', html=True)
        self.assertContains(response, '<p>Victory cause: <strong>Majority Vote</strong></p>', html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_index_poll_over_win_alg_maj_vic_2(self):
        ballot = Ballot.objects.create(date=POLL_DATE)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_1',
                votes=2)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_2',
                votes=1)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, '<h2>The Winner is: test_restaurant_1</h2>', html=True)
        self.assertContains(response, '<h3>Total votes: 3</h3>', html=True)
        self.assertContains(response, '<p>Victory cause: <strong>Majority Vote</strong></p>', html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_index_poll_over_win_alg_best_feedb(self):
        ballot = Ballot.objects.create(date=POLL_DATE)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_1',
                votes=1)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_2',
                votes=1)
        restaurant = Ranking.objects.create(restaurant='test_restaurant_1')
        Feedback.objects.create(ballot=ballot, restaurant=restaurant, mark=1)
        restaurant = Ranking.objects.create(restaurant='test_restaurant_2')
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, '<h2>The Winner is: test_restaurant_1</h2>', html=True)
        self.assertContains(response, '<h3>Total votes: 2</h3>', html=True)
        self.assertContains(response, '<p>Victory cause: <strong>Best Feedback</strong></p>', html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_index_poll_over_win_alg_best_feedb_2(self):
        ballot = Ballot.objects.create(date=POLL_DATE)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_1',
                votes=1)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_2',
                votes=1)
        restaurant = Ranking.objects.create(restaurant='test_restaurant_1')
        Feedback.objects.create(ballot=ballot, restaurant=restaurant, mark=2)
        restaurant = Ranking.objects.create(restaurant='test_restaurant_2')
        Feedback.objects.create(ballot=ballot, restaurant=restaurant, mark=1)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, '<h2>The Winner is: test_restaurant_1</h2>', html=True)
        self.assertContains(response, '<h3>Total votes: 2</h3>', html=True)
        self.assertContains(response, '<p>Victory cause: <strong>Best Feedback</strong></p>', html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_index_poll_over_win_alg_most_rated(self):
        ballot = Ballot.objects.create(date=POLL_DATE)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_1',
                votes=1)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_2',
                votes=1)
        restaurant = Ranking.objects.create(restaurant='test_restaurant_1')
        Feedback.objects.create(ballot=ballot, restaurant=restaurant, mark=1)
        Feedback.objects.create(ballot=ballot, restaurant=restaurant, mark=1)
        restaurant = Ranking.objects.create(restaurant='test_restaurant_2')
        Feedback.objects.create(ballot=ballot, restaurant=restaurant, mark=2)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, '<h2>The Winner is: test_restaurant_1</h2>', html=True)
        self.assertContains(response, '<h3>Total votes: 2</h3>', html=True)
        self.assertContains(response, '<p>Victory cause: <strong>Most Rated</strong></p>', html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_index_poll_over_win_alg_rand_no_f(self):
        ballot = Ballot.objects.create(date=POLL_DATE)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_1',
                votes=1)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_2',
                votes=1)
        restaurant = Ranking.objects.create(restaurant='test_restaurant_1')
        restaurant = Ranking.objects.create(restaurant='test_restaurant_2')
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, '<h3>Total votes: 2</h3>', html=True)
        self.assertContains(response, '<p>Victory cause: <strong>Random No Feedback</strong></p>', html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_index_poll_over_win_alg_rand_same_f(self):
        ballot = Ballot.objects.create(date=POLL_DATE)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_1',
                votes=1)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_2',
                votes=1)
        restaurant = Ranking.objects.create(restaurant='test_restaurant_1')
        Feedback.objects.create(ballot=ballot, restaurant=restaurant, mark=1)
        restaurant = Ranking.objects.create(restaurant='test_restaurant_2')
        Feedback.objects.create(ballot=ballot, restaurant=restaurant, mark=1)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, '<h3>Total votes: 2</h3>', html=True)
        self.assertContains(response, '<p>Victory cause: <strong>Random Same Feedback</strong></p>', html=True)



class VotingTests(TestCase):

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollWait)
    def test_voting_poll_wait(self):
        response = self.client.get(reverse('polls:voting'))
        self.assertRedirects(response, reverse('polls:index'))

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollOpen)
    def test_voting_poll_open(self):
        response = self.client.get(reverse('polls:voting'))
        self.assertContains(response, '<h2>Total votes: 0</h2>', html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_voting_poll_closed(self):
        response = self.client.get(reverse('polls:voting'))
        self.assertRedirects(response, reverse('polls:index'))



class FeedbackDetailTests(TestCase):

    @patch('polls.views.timezone.now', MockedTimezoneNow_FeedbackWait)
    def test_feedback_detail_wait(self):
        response = self.client.get(reverse('polls:feedback_detail'))
        self.assertContains(response, 'Feedback can only be submitted from')
        self.assertTemplateUsed(response, 'polls/feedback_waiting.html')

    @patch('polls.views.timezone.now', MockedTimezoneNow_FeedbackOpen)
    def test_feedback_detail_open(self):
        response = self.client.get(reverse('polls:feedback_detail'))
        self.assertTemplateUsed(response, 'polls/feedback_detail.html')
        self.assertContains(response, '<p><strong>No vote has been cast. Poll is over, no feedback can be submitted.</strong></p>', html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_FeedbackOpen)
    def test_feedback_detail_open_2(self):
        ballot = Ballot.objects.create(date=POLL_DATE,
                winner='test_restaurant', win_cause='Majority Vote')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant',
                votes=1)
        response = self.client.get(reverse('polls:feedback_detail'))
        self.assertTemplateUsed(response, 'polls/feedback_detail.html')
        self.assertContains(response, '<p>Please leave a comment (optional):</p>', html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_FeedbackClosed)
    def test_feedback_detail_closed(self):
        response = self.client.get(reverse('polls:feedback_detail'))
        self.assertTemplateUsed(response, 'polls/feedback_waiting.html')
        self.assertContains(response, 'Feedback can only be submitted from')


class StatisticsTests(TestCase):

    def test_statistics_empty_view(self):
        response = self.client.get(reverse('polls:statistics'))
        self.assertContains(response, '<p>No statistics are available.</p>',
                html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_statistics_maj_vic(self):
        ballot = Ballot.objects.create(date=POLL_DATE,
                winner='test_restaurant', win_cause='Majority Vote')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant',
                votes=1)
        Ranking.objects.create(restaurant='test_restaurant')
        response = self.client.get(reverse('polls:statistics'))
        self.assertContains(response, '<h1>Statistics</h1>', html=True)
        self.assertContains(response, '<h2>General Statistics</h2>', html=True)
        self.assertEqual(response.context['stat'][0]['name'], 'test_restaurant')
        self.assertEqual(response.context['stat'][0]['win'], 1)
        self.assertEqual(response.context['stat'][0]['majority'], 1)
        self.assertEqual(response.context['stat'][0]['vote'], 1)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_statistics_maj_vic_2(self):
        ballot = Ballot.objects.create(date=POLL_DATE,
                winner='test_restaurant', win_cause='Majority Vote')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant',
                votes=1)
        ballot = Ballot.objects.create(date=POLL_DATE-timedelta(days=1),
                winner='test_restaurant', win_cause='Majority Vote')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant',
                votes=1)
        Ranking.objects.create(restaurant='test_restaurant')
        response = self.client.get(reverse('polls:statistics'))
        self.assertContains(response, '<h1>Statistics</h1>', html=True)
        self.assertContains(response, '<h2>General Statistics</h2>', html=True)
        self.assertEqual(response.context['stat'][0]['name'], 'test_restaurant')
        self.assertEqual(response.context['stat'][0]['win'], 2)
        self.assertEqual(response.context['stat'][0]['majority'], 2)
        self.assertEqual(response.context['stat'][0]['vote'], 2)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_statistics_parity_best_feedback(self):
        ballot = Ballot.objects.create(date=POLL_DATE,
                winner='test_restaurant_1', win_cause='Best Feedback')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_1',
                votes=1)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_2',
                votes=1)
        Ranking.objects.create(restaurant='test_restaurant_1')
        Ranking.objects.create(restaurant='test_restaurant_2')
        response = self.client.get(reverse('polls:statistics'))
        self.assertContains(response, '<h1>Statistics</h1>', html=True)
        self.assertContains(response, '<h2>General Statistics</h2>', html=True)
        self.assertEqual(response.context['stat'][0]['name'], 'test_restaurant_1')
        self.assertEqual(response.context['stat'][0]['win'], 1)
        self.assertEqual(response.context['stat'][0]['parity'], 1)
        self.assertEqual(response.context['stat'][0]['feedback'], 1)
        self.assertEqual(response.context['stat'][0]['vote'], 1)
        self.assertEqual(response.context['stat'][1]['name'], 'test_restaurant_2')
        self.assertEqual(response.context['stat'][1]['win'], 0)
        self.assertEqual(response.context['stat'][1]['parity'], 1)
        self.assertEqual(response.context['stat'][1]['feedback'], 0)
        self.assertEqual(response.context['stat'][1]['vote'], 1)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_statistics_parity_most_rated(self):
        ballot = Ballot.objects.create(date=POLL_DATE,
                winner='test_restaurant_1', win_cause='Most Rated')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_1',
                votes=1)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_2',
                votes=1)
        Ranking.objects.create(restaurant='test_restaurant_1')
        Ranking.objects.create(restaurant='test_restaurant_2')
        response = self.client.get(reverse('polls:statistics'))
        self.assertContains(response, '<h1>Statistics</h1>', html=True)
        self.assertContains(response, '<h2>General Statistics</h2>', html=True)
        self.assertEqual(response.context['stat'][0]['name'], 'test_restaurant_1')
        self.assertEqual(response.context['stat'][0]['win'], 1)
        self.assertEqual(response.context['stat'][0]['parity'], 1)
        self.assertEqual(response.context['stat'][0]['most_rated'], 1)
        self.assertEqual(response.context['stat'][0]['vote'], 1)
        self.assertEqual(response.context['stat'][1]['name'], 'test_restaurant_2')
        self.assertEqual(response.context['stat'][1]['win'], 0)
        self.assertEqual(response.context['stat'][1]['parity'], 1)
        self.assertEqual(response.context['stat'][1]['most_rated'], 0)
        self.assertEqual(response.context['stat'][1]['vote'], 1)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_statistics_parity_rand_feedback(self):
        ballot = Ballot.objects.create(date=POLL_DATE,
                winner='test_restaurant_1', win_cause='Random Same Feedback')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_1',
                votes=1)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_2',
                votes=1)
        Ranking.objects.create(restaurant='test_restaurant_1')
        Ranking.objects.create(restaurant='test_restaurant_2')
        response = self.client.get(reverse('polls:statistics'))
        self.assertContains(response, '<h1>Statistics</h1>', html=True)
        self.assertContains(response, '<h2>General Statistics</h2>', html=True)
        self.assertEqual(response.context['stat'][0]['name'], 'test_restaurant_1')
        self.assertEqual(response.context['stat'][0]['win'], 1)
        self.assertEqual(response.context['stat'][0]['parity'], 1)
        self.assertEqual(response.context['stat'][0]['rand_feedback'], 1)
        self.assertEqual(response.context['stat'][0]['vote'], 1)
        self.assertEqual(response.context['stat'][1]['name'], 'test_restaurant_2')
        self.assertEqual(response.context['stat'][1]['win'], 0)
        self.assertEqual(response.context['stat'][1]['parity'], 1)
        self.assertEqual(response.context['stat'][1]['rand_feedback'], 0)
        self.assertEqual(response.context['stat'][1]['vote'], 1)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_statistics_parity_rand_no_feedback(self):
        ballot = Ballot.objects.create(date=POLL_DATE,
                winner='test_restaurant_1', win_cause='Random No Feedback')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_1',
                votes=1)
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_2',
                votes=1)
        Ranking.objects.create(restaurant='test_restaurant_1')
        Ranking.objects.create(restaurant='test_restaurant_2')
        response = self.client.get(reverse('polls:statistics'))
        self.assertContains(response, '<h1>Statistics</h1>', html=True)
        self.assertContains(response, '<h2>General Statistics</h2>', html=True)
        self.assertEqual(response.context['stat'][0]['name'], 'test_restaurant_1')
        self.assertEqual(response.context['stat'][0]['win'], 1)
        self.assertEqual(response.context['stat'][0]['parity'], 1)
        self.assertEqual(response.context['stat'][0]['rand_no_feedback'], 1)
        self.assertEqual(response.context['stat'][0]['vote'], 1)
        self.assertEqual(response.context['stat'][1]['name'], 'test_restaurant_2')
        self.assertEqual(response.context['stat'][1]['win'], 0)
        self.assertEqual(response.context['stat'][1]['parity'], 1)
        self.assertEqual(response.context['stat'][1]['rand_no_feedback'], 0)
        self.assertEqual(response.context['stat'][1]['vote'], 1)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_statistics_feedback(self):
        ballot = Ballot.objects.create(date=POLL_DATE,
                winner='test_restaurant', win_cause='Majority Vote')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant',
                votes=1)
        restaurant = Ranking.objects.create(restaurant='test_restaurant')
        Feedback.objects.create(ballot=ballot, restaurant=restaurant, mark=1)
        response = self.client.get(reverse('polls:statistics'))
        self.assertContains(response, '<h1>Statistics</h1>', html=True)
        self.assertContains(response, '<h2>General Statistics</h2>', html=True)
        self.assertEqual(response.context['stat'][0]['name'], 'test_restaurant')
        self.assertEqual(response.context['stat'][0]['win'], 1)
        self.assertEqual(response.context['stat'][0]['majority'], 1)
        self.assertEqual(response.context['stat'][0]['vote'], 1)
        self.assertEqual(response.context['stat'][0]['mark'], 1)
        self.assertEqual(response.context['stat'][0]['feedback_num'], 1)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_statistics_feedback_2(self):
        ballot = Ballot.objects.create(date=POLL_DATE,
                winner='test_restaurant', win_cause='Majority Vote')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant',
                votes=1)
        restaurant = Ranking.objects.create(restaurant='test_restaurant')
        Feedback.objects.create(ballot=ballot, restaurant=restaurant, mark=1)
        ballot = Ballot.objects.create(date=POLL_DATE-timedelta(days=1),
                winner='test_restaurant', win_cause='Majority Vote')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant',
                votes=1)
        Feedback.objects.create(ballot=ballot, restaurant=restaurant, mark=2)
        response = self.client.get(reverse('polls:statistics'))
        self.assertContains(response, '<h1>Statistics</h1>', html=True)
        self.assertContains(response, '<h2>General Statistics</h2>', html=True)
        self.assertEqual(response.context['stat'][0]['name'], 'test_restaurant')
        self.assertEqual(response.context['stat'][0]['win'], 2)
        self.assertEqual(response.context['stat'][0]['majority'], 2)
        self.assertEqual(response.context['stat'][0]['vote'], 2)
        self.assertEqual(response.context['stat'][0]['mark'], 3)
        self.assertEqual(response.context['stat'][0]['feedback_num'], 2)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_statistics_feedback_3(self):
        ballot = Ballot.objects.create(date=POLL_DATE,
                winner='test_restaurant_1', win_cause='Majority Vote')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_1',
                votes=1)
        restaurant = Ranking.objects.create(restaurant='test_restaurant_1')
        Feedback.objects.create(ballot=ballot, restaurant=restaurant, mark=1)
        ballot = Ballot.objects.create(date=POLL_DATE-timedelta(days=1),
                winner='test_restaurant_2', win_cause='Majority Vote')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant_2',
                votes=2)
        restaurant = Ranking.objects.create(restaurant='test_restaurant_2')
        Feedback.objects.create(ballot=ballot, restaurant=restaurant, mark=2)
        response = self.client.get(reverse('polls:statistics'))
        self.assertContains(response, '<h1>Statistics</h1>', html=True)
        self.assertContains(response, '<h2>General Statistics</h2>', html=True)
        self.assertEqual(response.context['stat'][1]['name'], 'test_restaurant_1')
        self.assertEqual(response.context['stat'][1]['win'], 1)
        self.assertEqual(response.context['stat'][1]['majority'], 1)
        self.assertEqual(response.context['stat'][1]['vote'], 1)
        self.assertEqual(response.context['stat'][1]['mark'], 1)
        self.assertEqual(response.context['stat'][1]['feedback_num'], 1)
        self.assertEqual(response.context['stat'][0]['name'], 'test_restaurant_2')
        self.assertEqual(response.context['stat'][0]['win'], 1)
        self.assertEqual(response.context['stat'][0]['majority'], 1)
        self.assertEqual(response.context['stat'][0]['vote'], 2)
        self.assertEqual(response.context['stat'][0]['mark'], 2)
        self.assertEqual(response.context['stat'][0]['feedback_num'], 1)



class VoteHistoryIndexTests(TestCase):

    def test_vote_history_index_empty_view(self):
        response = self.client.get(reverse('polls:vote_history_index'))
        self.assertContains(response, '<h1>Vote History Index</h1>', html=True)
        self.assertContains(response, '<p>No polls are available.</p>', html=True)

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_vote_history_index_view(self):
        ballot = Ballot.objects.create(date=POLL_DATE,
                winner='test_restaurant', win_cause='Majority Vote')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant',
                votes=1)
        response = self.client.get(reverse('polls:vote_history_index'))
        self.assertContains(response, '<h1>Vote History Index</h1>', html=True)
        self.assertContains(response, '<a href="/polls/1/vote_result_history/">Oct. 26, 2016</a>', html=True)
        self.assertContains(response, '<td style="padding-right:5em">test_restaurant</td>', html=True)
        self.assertContains(response, '<td style="padding-right:5em">Majority Vote</td>', html=True)



class VoteResultHistoryTests(TestCase):

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_vote_result_history_view(self):
        ballot = Ballot.objects.create(date=POLL_DATE,
                winner='test_restaurant', win_cause='Majority Vote')
        Restaurant.objects.create(ballot=ballot, name='test_restaurant',
                votes=1)
        response = self.client.get(reverse('polls:vote_result_history', args=('1')))
        self.assertContains(response, '<h1>Oct. 26, 2016</h1>', html=True)
        self.assertContains(response, '<h2>The Winner is: test_restaurant</h2>', html=True)
        self.assertContains(response, '<h3>Total votes: 1</h3>', html=True)
        self.assertContains(response, '<p>Victory cause: <strong>Majority Vote</strong></p>', html=True)



class FeedbackHistoryTests(TestCase):

    def test_feedback_history_empty_view(self):
        response = self.client.get(reverse('polls:feedback_history'))
        self.assertContains(response, 'No feedback available.')

    @patch('polls.views.timezone.now', MockedTimezoneNow_PollClosed)
    def test_feedback_history_entry(self):
        ballot = Ballot.objects.create(date=POLL_DATE,
                winner='test_restaurant', win_cause='Majority Vote')
        restaurant = Ranking.objects.create(restaurant='test_restaurant')
        Feedback.objects.create(ballot=ballot, restaurant=restaurant, mark=1, comment="test comment")
        response = self.client.get(reverse('polls:feedback_history'))
        self.assertContains(response, '<h1>Feedback History</h1>', html=True)
        self.assertContains(response, '<strong>Oct. 26, 2016</strong>', html=True)
        self.assertContains(response, '<td class="statistics">test_restaurant</td>', html=True)
        self.assertContains(response, '<td class="statistics">1</td>', html=True)
        self.assertContains(response, '<em>test comment</em>', html=True)

