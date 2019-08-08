from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


class SMS(models.Model):
    '''
    Logs all out bound SMS.
    '''
    to = models.TextField()
    message = models.TextField()
    sent_on = models.DateTimeField(auto_now_add=True)

    def get_customer_sms(user):
        return SMS.objects.filter(to=user.customer.country_code + user.customer.mobile)

    def __str__(self):
        return self.to


class SmsTemplate(models.Model):
    '''
    SMS Templates
    '''

    body = models.TextField()
    slug = models.SlugField(max_length=100, null=True, blank=True)
