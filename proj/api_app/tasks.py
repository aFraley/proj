"""Tasks for Celery to run."""
from celery import shared_task
from celery import subtask
import tweepy
from datetime import datetime, timedelta

from .models import Tweet
from django.db import IntegrityError

CONSUMER_KEY = 'Vp7FVQLSwESvE9oTQruw0TnhW'
CONSUMER_SECRET = 'miy6EsGklNYxAaVn37vTjAVGwP0c67IOyuY71AAyL1p2Ba4VPN'
ACCESS_TOKEN = '1952022900-5WAHk6l5d3GllFtqDPaucSpnraIokE6hU7aBxNJ'
ACCESS_TOKEN_SECRET = 'ekONOf6QxJG6Lq3k2kznfQ16x12BGm909wckYFcP8SlYZ'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


@shared_task(name='clean_tweetdb')
def clean_tweetdb():
    Tweet.objects.filter(tweet_date__lte=datetime.now()-timedelta(days=7)).delete()


@shared_task(name='get_tweets')
def get_tweets():
    """Get some tweets from the twitter api and store them to the db."""
    if not Tweet.objects.all():
        # If the db is empty, don't get max_id.
        tweets = api.search(
            q='#python',
            count=100
        )
    else:
        # If the db is not empty, get max_id.
        subtask(clean_tweetdb)
        max_id = min([tweet.tweet_id for tweet in Tweet.objects.all()])
        tweets = api.search(
            q='#python',
            max_id=max_id,
            count=100
        )

    # Store the tweet data in lists.
    tweets_id = [tweet.id for tweet in tweets]
    tweets_date = [tweet.created_at for tweet in tweets]
    tweets_source = [tweet.source for tweet in tweets]
    tweets_favorite_cnt = [tweet.favorite_count for tweet in tweets]
    tweets_retweet_cnt = [tweet.retweet_count for tweet in tweets]
    tweets_text = [tweet.text for tweet in tweets]

    # Iterate over these lists and add data to db.
    for i, j, k, l, m, n in zip(
            tweets_id,
            tweets_date,
            tweets_source,
            tweets_favorite_cnt,
            tweets_retweet_cnt,
            tweets_text,
    ):
        try:
            # Check that they are valid.
            Tweet.objects.create(
                tweet_id=i,
                tweet_date=j,
                tweet_source=k,
                tweet_favorite_cnt=l,
                tweet_retweet_cnt=m,
                tweet_text=n,
            )
        except IntegrityError:
            pass
