from django.contrib import admin
from django.conf.urls import url

from frontend import views

app_name = 'frontend'
urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home-view'),
    url(r'^logout/$', views.LogOutView.as_view(), name='logout'),
    url(r'^username/$', views.UsernameView.as_view(), name='username-view'),
    url(r'^categories/$', views.CategoriesView.as_view(), name='categores-view'),

    url(r'^game/find/(?P<player>\d+)/$', views.MatchMaking.as_view(), name='game-find'),


    url(r'^game/(?P<game>\d+)/(?P<player>\d+)/$', views.GameView.as_view(), name='game-view'),
    url(r'^game/end/(?P<game>\d+)/(?P<player>\d+)/$', views.GameEndView.as_view(), name='game-end-view'),
]