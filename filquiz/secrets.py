'''
Gets all the secrets required.
'''
from __future__ import unicode_literals

from decouple import config


def get_secret(secret_key, cast=str):
    '''
    To cast as a list, use the following lambda
    lambda v: [s.strip() for s in v.split(',')]
    Store lists in ENV as 'a,b,c'
    :param secret_key:
    :param cast:
    :return:
    '''
    return config(secret_key.upper(), default='', cast=cast)