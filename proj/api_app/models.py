from django.db import models


class Tweet(models.Model):
    tweet_id = models.CharField(max_length=50, unique=True)
    tweet_date = models.DateTimeField()
    tweet_source = models.TextField()
    tweet_favorite_cnt = models.CharField(max_length=50)
    tweet_retweet_cnt = models.CharField(max_length=50)
    tweet_text = models.TextField()

    def __str__(self):
        return str(self.tweet_id) + '  |  ' + str(self.tweet_date)
