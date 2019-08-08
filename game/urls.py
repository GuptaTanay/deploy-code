from django.contrib import admin
from django.conf.urls import url

from game import views

app_name = 'game'

urlpatterns = [


    url(r'^api/v1/game/found/$', views.MatchFoundAPI.as_view(), name='game-found'),
    url(r'^api/v1/game/create/$', views.CreateGameAPI.as_view(), name='game-create'),
    url(r'^api/v1/game/check/$', views.CheckGameAPI.as_view(), name='game-create'),

]