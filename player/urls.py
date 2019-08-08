from django.contrib import admin
from django.conf.urls import url

from player import views

app_name = 'player'
urlpatterns = [
    url(r'^api/v1/otp/$', views.SendOTPView.as_view(), name='send-otp'),
    url(r'^api/v1/otp/verify/$', views.VerifyOTPView.as_view(), name='verify-otp'),
    url(r'^api/v1/update/$', views.UpdatePlayerName.as_view(), name='verify-otp'),

    url(r'^api/v1/player/add-queue/$', views.AddToQueueAPI.as_view(), name='add-queue'),
    url(r'^api/v1/player/delete-queue/$', views.DeleteFromQueue.as_view(), name='delete-queue')

]
