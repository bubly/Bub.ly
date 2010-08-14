# -*- coding: utf-8 -*-

from django.conf import settings
import redis

class Client(object):
    def __init__(self, **kwargs):
        self.connection_settings = kwargs or {'host': settings.REDIS_HOST,
                'port': settings.REDIS_PORT, 'db': 0}

    def redis(self):
        return redis.Redis(**self.connection_settings)

    def update(self, d):
        self.connection_settings.update(d)

def connection_setup(**kwargs):
    global connection, client
    if client:
        client.update(kwargs)
    else:
        client = Client(**kwargs)
    connection = client.redis()

def get_client():
    global connection
    return connection

client = Client()
connection = client.redis()

__all__ = ['connection_setup', 'get_client']
