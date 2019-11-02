import os
from collections import Counter
import time
from pathlib import Path
import pickle
import io

import tweepy
import requests_cache


AS_MANY_AS_POSSIBLE=10_000


def get_api_client(api_token='', api_secret=''):
    token = api_token or os.environ['TWITTER_API_TOKEN']
    secret = api_secret or os.environ['TWITTER_API_SECRET']

    auth = tweepy.AppAuthHandler(token, secret)
    api = tweepy.API(auth)

    return api


import datetime as dt


class ScoreBoard:
    
    def __init__(self, items, display_top=5, contestants_name='Tweeters', decoration=''):
        self._items = items
        self.display_top = display_top
        self.contestants_name = contestants_name
        self.decoration = decoration
        
    @property
    def counts_by_name(self):
        return Counter(tweet.user.screen_name for tweet in self._items)
    
    @property
    def to_display(self):
        return self.counts_by_name.most_common(self.display_top)

    def _repr_markdown_(self):
        lines = [
            '---',
            f'# {self.decoration} [North Bay Python 2019](https://2019.northbaypython.org) Top {self.display_top} {self.contestants_name} {self.decoration}',
            '| name | # tweets |',
            '|-|-|',
        ]

        for name, count in self.to_display:
            lines.append(f'| {name} | {count} |')

        return '\n'.join(lines)


def get_nbpy_tweets_from_file(path_or_data):
    try:
        path = Path(path_or_data)
    except TypeError:

        data = [val['content'] for key, val in path_or_data.items()][0]
        file = io.BytesIO(data)
    else:
        file = path.read_bytes()
    return pickle.load(file)


def get_nbpy_tweets_from_api(timeout=0, result_type='recent', **kwargs):
    api = get_api_client(**kwargs)
    time.sleep(timeout)
    # return api.search('#nbpy', result_type=result_type, count=AS_MANY_AS_POSSIBLE)
    # tweepy.Cursor deals with pagination automatically
    return tweepy.Cursor(api.search, '#nbpy', result_type=result_type, count=AS_MANY_AS_POSSIBLE).items()


def get_scoreboard(api_token='',
                   api_secret='',
                   display_top=5,
                   result_type='last',
                   date='',
                   contestants_name='Tweeters',
                   api_timeout=1,
                   use_cache=True,
                   cache_file='',
                   decoration='',
                   ):

    # if cache_file:
        # tweets = get_nbpy_tweets_from_file(cache_file)
    # else:

    if use_cache:
        requests_cache.install_cache()

    tweets = get_nbpy_tweets_from_api(timeout=api_timeout, result_type=result_type, api_token=api_token, api_secret=api_secret)

    if date:
        if isinstance(date, str):
            date = dt.date.fromisoformat(date)
        tweets = [tweet for tweet in tweets if tweet.created_at.date() == date]

    return ScoreBoard(tweets,
                      display_top=display_top,
                      contestants_name=contestants_name,
                      decoration=decoration,
    )
