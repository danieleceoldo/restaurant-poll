from django.conf.urls import url

from . import views

app_name = 'polls'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<ballot_id>[0-9]+)/$', views.vote_detail, name='vote_detail'),
    url(r'^(?P<ballot_id>[0-9]+)/feedback_detail/$', views.feedback_detail, name='feedback_detail'),
    url(r'^(?P<ballot_id>[0-9]+)/vote_result/$', views.vote_result, name='vote_result'),
    url(r'^vote_history_index/$', views.VoteHistoryIndexView.as_view(), name='vote_history_index'),
    url(r'^feedback_history/$', views.FeedbackHistoryView.as_view(), name='feedback_history'),
    url(r'^(?P<pk>[0-9]+)/vote_result_history/$', views.VoteResultHistoryView.as_view(), name='vote_result_history'),
    url(r'^statistics/$', views.statistics, name='statistics'),
    url(r'^(?P<ballot_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^(?P<ballot_id>[0-9]+)/feedback/$', views.feedback, name='feedback'),
]
