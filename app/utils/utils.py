import tweepy
import os
import json
from dotenv import load_dotenv

load_dotenv("../../.env")

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
client = tweepy.Client(BEARER_TOKEN, wait_on_rate_limit=True)

# +
# def is_follower(user_id, tweet_id, token=None):
#     followed_id = get_author_id(tweet_id)
#     user_following = client.get_users_following(
#         user_id, max_results=1000, pagination_token=token
#     )

#     if user_following.data != None:
#         following = [follow.id for follow in user_following.data]

#     if followed_id in following:
#         return True
#     elif "next_token" in user_following.meta:
#         next_token = user_following.meta["next_token"]
#         return is_follower(user_id, followed_id, next_token)
#     else:
#         return False


def likes_tweet(user_id, tweet_id, token=None, i=0):
    if i > 4:
        return False

    user_liked_tweets = client.get_liked_tweets(user_id, pagination_token=token)

    if user_liked_tweets.data is not None:
        liked_tweets = [tweet.id for tweet in user_liked_tweets.data]
        if int(tweet_id) in liked_tweets:
            return True

    elif "next_token" in user_liked_tweets.meta:
        next_token = user_liked_tweets.meta["next_token"]
        return likes_tweet(user_id, tweet_id, token=next_token, i=i + 1)

    else:
        return False


# -


class activeGiveaway:
    def __init__(self, tweet_id):
        self.tweet_id = tweet_id
        self.__get_metrics()

    def __get_metrics(self):

        tweet = client.get_tweet(
            self.tweet_id, expansions="author_id", tweet_fields="public_metrics"
        )

        self.author_id = tweet.includes["users"][0].id
        self.retweet_count = tweet.data.public_metrics["retweet_count"]
        self.like_count = tweet.data.public_metrics["like_count"]

        user = client.get_user(id=self.author_id, user_fields="public_metrics")
        self.follower_count = user.data.public_metrics["followers_count"]

    def get_data(self, call, token=None, user_ids=[]):
        calls = {
            "rts": client.get_retweeters,
            "likes": client.get_liking_users,
            "follows": client.get_users_followers,
        }
        id_, num_results = (
            (self.author_id, 1000) if call == "followers" else (self.tweet_id, 100)
        )

        users = calls[call](id_, pagination_token=token, max_results=num_results)

        if users.data != None:
            new_user_ids = [user.id for user in users.data]
            total = user_ids + new_user_ids
        else:
            total = user_ids

        if "next_token" in users.meta:
            return self.get_data(call, users.meta["next_token"], total)

        setattr(self, call, total)

        return getattr(self, call)


tst = activeGiveaway(1486266855228649476)
