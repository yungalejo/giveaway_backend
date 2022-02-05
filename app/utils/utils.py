import tweepy
import os
import json
from dotenv import load_dotenv
import random

load_dotenv("../../.env")

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
client = tweepy.Client(BEARER_TOKEN, wait_on_rate_limit=True)


class GiveawayClass:
    def __init__(self, tweet_id, addtl_username=None):
        self.tweet_id = tweet_id
        self.addtl_id = None
        self.attempted_ids = 0
        self.following_count = {}
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

    def get_data(self, call, id_, token=None, user_ids=[]):
        calls = {
            "retweet": client.get_retweeters,
            "likes_tweet": client.get_liking_users,
            "follow": client.get_users_followers,
            "addtl_follow": client.get_users_followers,
        }

        num_results = 1000 if call == "follow" else 100

        users = calls[call](id_, pagination_token=token, max_results=num_results)
        print(users.meta)

        if users.data != None:
            new_user_ids = [user.id for user in users.data]
            total = user_ids + new_user_ids
        else:
            total = user_ids

        if users.meta["result_count"] >= 85:
            return self.get_data(call, id_, users.meta["next_token"], total)

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
            return True, len(total)
        elif any([call == "is_follower", call == "likes_tweet", call == "retweet"]):
            if follower_id in total:
                return True, len(total)

        if users.meta["result_count"] >= 85:
            return self.__check_conditions(call, id_, users.meta["next_token"], total)

        return False, len(total)

    def is_follower(self, user_id, follower_id, count_total=False):
        # this function determines if potential winners following count is less than
        # the giveaway hosts (or addtl accounts) follower count for efficiency
        ids = {"user_id": user_id, "follower_id": follower_id}
        check_condition = self.__check_conditions
        follower = client.get_user(id=follower_id, user_fields="public_metrics")
        following_count = follower.data.public_metrics["following_count"]
        self.following_count[follower_id] = following_count
        follower_count = self.follower_count[user_id]

        if following_count < follower_count:
            follow_bool, total_checked = check_condition("is_following", **ids)
        else:
            follow_bool, total_checked = check_condition("is_follower", **ids)

        if count_total == True:
            return follow_bool, total_checked
        else:
            return follow_bool

    def __random_choice(self, attributes, conditions):
        # this function is to bypass all the possible combinations of conditions by trying all of the options]
        tweet_conditions = ['retweet', 'likes_tweet']
        
        for i in tweet_conditions:
            if conditions[i]:
                self.get_data(i, attributes[i])
                locals()[i] = set(getattr(self, i))

        if conditions["retweet"] and conditions["likes_tweet"]:
            particpants = list(retweet & likes_tweet)
        elif conditions["retweet"]:
            particpants = retweet
        else:
            particpants = likes_tweet
            
            
        for attr in attributes:
            try:
                if attr in tweet_conditions:
                    return random.choice(particpants)
                else:    
                    ids = getattr(self, attr)
                    return random.choice(ids)
            except:
                pass

    def get_random_id(self, conditions, random_id=None, attempts=[]):

        get_data = self.__get_data
        check_condition = self.__check_conditions
        is_follower = self.is_follower
        random_choice = self.__random_choice
        
        attributes = {
            "retweet": self.tweet_id,
            "likes_tweet": self.tweet_id,
            "follow": self.author_id,
            "addtl_follow": self.addtl_id,
        }
        
        if random_id ==None:
            random_id = random_choice(attributes,conditions)
        
        for condition in ['follow','addtl_follow']:
            if conditions[condition]:
                if random_id != None:
                    id_ = attributes[condition]
                    if is_follower(id_, random_id):
                            pass
                    else:
                        attempts.append(random_id)
                        new_random_id = random_choice(attributes,conditions)
                        while new_random_id in attempts:
                            new_random_id = random_choice(attributes,conditions)
                        return self.get_random_id(conditions, random_id, attempts)

                else:
                    get_data(condition, attributes[condition])
                    random_id = random_choice(attributes)

        return random_id

    def choose_winner(self, conditions):
        random_choice = self.__random_choice
        is_follower = self.is_follower
        get_random_id = self.get_random_id

        random_id = get_random_id(conditions)

        if conditions["addtl"] == True:
            follow_bool, total_checked = is_follower(
                self.addtl_id, random_id, count_total=True
            )
            if follow_bool:
                pass
            else:
                self.attempted_ids += total_checked
                count = min(
                    self.following_count[random_id], self.follower_count[self.addtl_id]
                )
                if self.attempted_ids >= count:
                    message = (
                        "There is no particpant that meets the required conditions"
                    )
                    return message
                else:
                    return self.choose_winner(conditions)

        self.winner = random_id
        return self.winner

tst = GiveawayClass(1489647967699185667, "probablysymbio")

set_1 = set(tst.retweet)
set_2 = set(tst.likes_tweet)

len(set_1 & set_2)

len(tst.likes_tweet)

conditions = {"follow": True, "addtl": True, "retweet": True, "like": True}
tst.choose_winner(conditions)


