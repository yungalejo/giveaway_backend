import tweepy
import os
import json
from dotenv import load_dotenv
import random

load_dotenv("../../.env")

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
client = tweepy.Client(BEARER_TOKEN, wait_on_rate_limit=True)


class activeGiveaway:
    def __init__(self, tweet_id, addtl_username=None):

        self.tweet_id = tweet_id
        self.addtl_id = None
        self.__get_metrics(addtl_username)

    def __get_metrics(self, addtl=None):

        tweet = client.get_tweet(
            self.tweet_id, expansions="author_id", tweet_fields="public_metrics"
        )

        self.author_id = tweet.includes["users"][0].id
        self.retweet_count = tweet.data.public_metrics["retweet_count"]
        self.like_count = tweet.data.public_metrics["like_count"]

        user = client.get_user(id=self.author_id, user_fields="public_metrics")
        self.follower_count = {
            self.author_id: user.data.public_metrics["followers_count"]
        }

        if addtl != None:
            user = client.get_user(username=addtl, user_fields="public_metrics").data
            self.follower_count[user.id] = user.public_metrics["followers_count"]
            self.addtl_id = user.id

    def __get_data(self, call, id_, token=None, user_ids=[]):
        calls = {
            "retweet": client.get_retweeters,
            "likes_tweet": client.get_liking_users,
            "follow": client.get_users_followers,
            "addtl_follow": client.get_users_followers,
        }

        num_results = 1000 if call == "follow" else 100

        users = calls[call](id_, pagination_token=token, max_results=num_results)

        if users.data != None:
            new_user_ids = [user.id for user in users.data]
            total = user_ids + new_user_ids
        else:
            total = user_ids

        if "next_token" in users.meta:
            return self.__get_data(call, id_, users.meta["next_token"], total)

        setattr(self, call, total)

        return getattr(self, call)

    def __check_conditions(
        self, call, follower_id, user_id=None, user_ids=[], token=None
    ):
        calls = {
            "is_following": client.get_users_following,
            "is_follower": client.get_users_followers,
            "likes_tweet": client.get_liking_users,
            "retweet": client.get_retweeters,
        }

        if call == "is_following":
            id_ = follower_id
            num_results = 1000
        elif call == "is_follower":
            id_ = user_id
            num_results = 1000
        else:
            id_ = self.tweet_id
            num_results = 100

        users = calls[call](id_, pagination_token=token, max_results=num_results)

        if users.data != None:
            new_user_ids = [user.id for user in users.data]
            total = user_ids + new_user_ids
        else:
            total = user_ids

        if call == "is_following" and user_id in total:
            return True
        elif any([call == "is_follower", call == "likes_tweet", call == "retweet"]):
            if follower_id in total:
                return True

        if "next_token" in users.meta:
            return self.__check_conditions(call, id_, users.meta["next_token"], total)

        return False

    def is_follower(self, user_id, follower_id):
        # this function determines if potential winners following count is less than the Giveaway hosts follower count for efficiency

        ids = {"user_id": user_id, "follower_id": follower_id}
        following_count = client.get_user(
            id=follower_id, user_fields="public_metrics"
        ).data.public_metrics["following_count"]
        follower_count = self.follower_count[user_id]
        check_condition = self.__check_conditions

        following_bool = (
            check_condition("is_following", **ids)
            if following_count < follower_count
            else check_condition("is_follower", **ids)
        )

        return following_bool

    def choose_winner(self, conditions):

        get_data = self.__get_data
        check_condition = self.__check_conditions

        attributes = {
            "retweet": self.tweet_id,
            "likes_tweet": self.tweet_id,
            "follow": self.author_id,
            "addtl_follow": self.addtl_id,
        }

        def random_choice(attributes):
            for attr in attributes:
                try:
                    ids = getattr(self, attr)
                    return random.choice(ids)
                except:
                    pass

        for condition in attributes:
            try:
                if conditions[condition] == True:
                    if "random_id" in locals():
                        if any([condition == "follow", condition == "addtl_follow"]):
                            id_ = attributes[condition]
                            if self.is_follower(id_, random_id):
                                # condition met, continue to check remaining conditions
                                pass
                            else:
                                # random_id does not meet condition, choose new random_id
                                random_id = random_choice(attributes)

                        else:
                            if check_condition(condition, random_id):
                                pass
                            else:
                                random_id = random_choice(attributes)
                    else:
                        get_data(condition, attributes[condition])
                        random_id = random_choice(attributes)
            except:
                pass

        self.winner = random_id
        return self.winner
