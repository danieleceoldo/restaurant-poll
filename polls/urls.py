from django.conf.urls import url
from . import views

app_name = 'polls'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^vote_detail/$', views.vote_detail, name='vote_detail'),
    url(r'^feedback_detail/$', views.feedback_detail, name='feedback_detail'),
    url(r'^vote_history_index/$', views.VoteHistoryIndexView.as_view(), name='vote_history_index'),
    url(r'^feedback_history/$', views.FeedbackHistoryView.as_view(), name='feedback_history'),
    url(r'^(?P<ballot_id>[0-9]+)/vote_result_history/$', views.vote_result_history, name='vote_result_history'),
    url(r'^(?P<ballot_id>[0-9]+)/vote_result_history_prev/$', views.vote_result_history_prev, name='vote_result_history_prev'),
    url(r'^(?P<ballot_id>[0-9]+)/vote_result_history_next/$', views.vote_result_history_next, name='vote_result_history_next'),
    url(r'^statistics/$', views.statistics, name='statistics'),
    url(r'^vote/$', views.vote, name='vote'),
    url(r'^feedback/$', views.feedback, name='feedback'),
]
