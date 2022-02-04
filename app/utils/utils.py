import tweepy
import os
import json
from dotenv import load_dotenv
import random

load_dotenv("../../.env")

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
client = tweepy.Client(BEARER_TOKEN, wait_on_rate_limit=True)


# +
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
            "like": client.get_liking_users,
            "follow": client.get_users_followers,
        }

        num_results = 1000 if call == "followers" else 100

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

    def __check_conditions(self, call, follower_id, user_id=None, user_ids=[], token=None):
        calls = {
            "is_following": client.get_users_following,
            "is_follower": client.get_users_followers,
            "likes_tweet": client.get_liking_users,
        }

        if call == "is_following":
            id_ = follower_id
            num_results = 1000
        elif call == "is_follower":
            id_ = user_id
            num_results = 1000
        elif call == "likes_tweet":
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
        elif call == "is_follower" or calls == "likes_tweet":
            if follower_id in total:
                return True

        if "next_token" in users.meta:
            return self.__following_TF(call, id_, users.meta["next_token"], total)

        return False

    def is_follower(self, follower_id, user_id):
        # this function determines if potential winners following count is less than the Giveaway hosts follower count for efficiency
        
        ids = {"follower_id": follower_id, "user_id": user_id}
        following_count = client.get_user(
            id=follower_id, user_fields="public_metrics"
        ).data.public_metrics["following_count"]
        follower_count = self.follower_count[user_id]
        is_following = self.__check_conditions

        following_bool = (
            is_following("is_following", **ids)
            if following_count < follower_count
            else is_following("is_follower", **ids)
        )

        return following_bool

#     def choose_winner(self, conditions):
#         get_data = self.__get_data
#         check_conditions = self.__check_conditions

#         if all(conditions.values()):
#             get_data("rts", self.tweet_id)
#             random_id = random.choice(self.retweet)
#             if check_conditions("likes_tweet", random_id):
#                 if follow_condition = is_follower(random_id, self.author_id):
#                     if addtl_condition = is_follower(random_id, self.addtl_id):
#                         winner = random_id
#                         return winner 
                    
    
        
        

#         if conditions["retweet"] == True:
#             get_data("retweet", self.tweet_id)
#             random_id = random.choice(self.retweet)
#             if conditions["like"] == True and check_conditions("likes_tweet", random_id):
#                 if conditions["follow"]==True and is_follower(random_id, self.author_id):
#                     if conditions['addtl'] and is_follower(random_id, self.addtl_id):
#                         winner = random_id
#                         return winner 
#                     elif conditions['addtl']==False:
                        
                 
            
            
#         elif conditions["like"]==True:
#             get_data("like", self.tweet_id)
        
#         elif conditions["follow"]==True:
#             get_data("follow", self.author_id)
        
#         elif conditions["addtl"] == True:
#             get_data("follow", self.addtl_id)
            

 
            
            
            

# +
# tst = activeGiveaway(1489339336554332162, 'probablysymbio')
