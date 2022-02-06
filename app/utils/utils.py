import tweepy
import os
import json
from dotenv import load_dotenv
import random

load_dotenv("../../.env")

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
client = tweepy.Client(BEARER_TOKEN, wait_on_rate_limit=True)


class GiveawayFunc:
    def __init__(self, tweet_id, addtl_username=None):
        self.tweet_id = tweet_id
        self.addtl_id = None
        self.attempted_ids = 0
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
        


        if users.data != None:
            new_user_ids = [user.id for user in users.data]
            total = user_ids + new_user_ids
        else:
            total = user_ids
            
            
        print(users.meta, "next_token" in users.meta)
        if "next_token" in users.meta:
            return self.get_data(call, id_, users.meta["next_token"], total)

        setattr(self, call, total)

        return getattr(self, call)

    def is_follower(
        self, follower_id, user_id, user_ids=[], token=None, count_total=False
    ):
        assert follower_id != user_id
        
        follower = client.get_user(id=follower_id, user_fields="public_metrics")
        following_count = follower.data.public_metrics["following_count"]
        follower_count = self.follower_count[user_id]

        call = "is_following" if following_count < follower_count else "is_follower"

        calls = {
            "is_following": client.get_users_following,
            "is_follower": client.get_users_followers,
        }

        id_ = follower_id if call == "is_following" else user_id
        
        users = calls[call](id_, pagination_token=token, max_results=1000)

        if users.data != None:
            new_user_ids = [user.id for user in users.data]
            total = user_ids + new_user_ids
        else:
            total = user_ids

        if id_ == self.author_id:
            self.follow = total
        elif id_ == self.addtl_id:
            self.addtl_follow = total

        if call == "is_following" and user_id in total:
            return True
        elif call == "is_follower" and follower_id in total:
            return True

        if users.meta["result_count"] >= 900:
            return self.is_follower(call, id_, users.meta["next_token"], total)

        return False

    def __random_choice(self, conditions):
        # this function is to bypass all the possible combinations of conditions by trying all of the options]
        attributes = {
            "retweet": self.tweet_id,
            "likes_tweet": self.tweet_id,
            "follow": self.author_id,
            "addtl_follow": self.addtl_id,
        }
        for i in attributes:
            # turn existing data into sets
            if conditions[i] == True:
                try:
                    locals()[i] = set(getattr(self, i))
                except:
                    if i in ["retweet", "likes_tweet"]:
                        self.get_data(i, attributes[i])
                        locals()[i] = set(getattr(self, i))

        sets = [i for i in attributes if locals()[i] in locals()]
        participants = set.intersection(*sets)

        for attr in attributes:
            try:
                if attr in ["retweet", "likes_tweet"]:
                    random_choice = random.choice(participants)
                else:
                    ids = getattr(self, attr)
                    random_choice = random.choice(ids)
            except:
                pass
            
        return random_choice

    def get_random_id(self, conditions, random_id=None, attempts=[]):

        get_data = self.__get_data
        is_follower = self.__is_follower
        random_choice = self.__random_choice

        follow_attr = {
            "follow": self.author_id,
            "addtl_follow": self.addtl_id,
        }

        if random_id == None:
            random_id = random_choice(conditions)

        for condition in ["follow", "addtl_follow"]:
            if conditions[condition]:
                if random_id != None:
                    id_ = follow_attr[condition]
                    if is_follower(random_id, id_):
                        pass
                    else:
                        attempts.append(random_id)
                        new_random_id = random_choice(conditions)
                        while new_random_id in attempts:
                            new_random_id = random_choice(conditions)
                        return self.get_random_id(conditions, random_id, attempts)

                else:
                    get_data(condition, follow_attr[condition])
                    random_id = random_choice(conditions)

        return random_id

# +
# class GiveawayClass(GiveawayFunc):
    
#     def start_giveaway():
        
    
#     def choose_winner(self, conditions):
#         random_choice = self.__random_choice
#         is_follower = self.__is_follower  
#         get_random_id = self.get_random_id

#         random_id = get_random_id(conditions)

#         if conditions["addtl"] == True:
#             follow_bool, total_checked = is_follower(
#                 random_id, self.addtl_id,  count_total=True
#             )
#             if follow_bool:
#                 pass
#             else:
#                 self.attempted_ids += total_checked
#                 count = min(
#                     self.following_count[random_id], self.follower_count[self.addtl_id]
#                 )
#                 if self.attempted_ids >= count:
#                     message = (
#                         "There is no particpant that meets the required conditions"
#                     )
#                     return message
#                 else:
#                     return self.choose_winner(conditions)

#         self.winner = random_id
#         return self.winner
    
#     def end_giveaway():
        
