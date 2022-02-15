import tweepy
import os
import json
import random
import asyncio
from dotenv import load_dotenv

load_dotenv("../../.env")

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
client = tweepy.Client(BEARER_TOKEN, wait_on_rate_limit=True)


class GiveawayFunc:
    def __init__(self, giveaway):

        self.giveaway = giveaway
        self.tweet_id = giveaway["tweet_id"]
        self.conditions = giveaway["conditions"]
        self.attempted_ids = 0
        self.__get_metrics()
        self.data_retreival_status = {
            "retweet": None,
            "likes_tweet": None,
            "follow": None,
        }

    def __get_metrics(self):
        tweet = client.get_tweet(self.tweet_id, expansions="author_id")
        self.author_id = tweet.includes["users"][0].id

        if self.giveaway["addtl_username"] != None:
            user_name = self.giveaway["addtl_username"]
            user = client.get_user(
                username=user_name, user_fields="public_metrics"
            ).data
            self.addtl_count = user.public_metrics["followers_count"]
            self.addtl_id = user.id

    def get_data(self, call, id_, user_ids=[], token=None):
        calls = {
            "retweet": client.get_retweeters,
            "likes_tweet": client.get_liking_users,
            "follow": client.get_users_followers,
            "addtl_follow": client.get_users_followers,
        }

        num_results = 1000 if call == "follow" else 100

        try:
            users = calls[call](id_, pagination_token=token, max_results=num_results)
        except Exception as e:
            print(e)
            return

        if users.data != None:
            new_user_ids = [user.id for user in users.data]
            total = user_ids + new_user_ids
        else:
            total = user_ids

        print(users.meta)

        setattr(self, call, total)

        if "next_token" in users.meta:
            return self.get_data(call, id_, total, users.meta["next_token"])

        self.data_retreival_status[call] = "complete"
        return getattr(self, call)

    def __is_follower(self, participant_id, user_id, user_ids=[], token=None):
        # checks if potential winner follows additional account (neccesary due to twitter API rate limitations)
        assert participant_id != user_id
        participant = client.get_user(id=participant_id, user_fields="public_metrics")
        following_count = participant.data.public_metrics["following_count"]

        call = (
            "accounts_participant_follows"
            if following_count < self.follower_count
            else "users_followers"
        )

        calls = {
            "accounts_participant_follows": client.get_users_following,
            "users_followers": client.get_users_followers,
        }

        id_ = participant_id if call == "accounts_participant_follows" else user_id

        users = calls[call](id_, pagination_token=token, max_results=1000)

        if users.data != None:
            new_user_ids = [user.id for user in users.data]
            total = user_ids + new_user_ids
        else:
            total = user_ids

        if call == "users_followers":
            self.addtl_follow = total

        if participant_id in total:
            return True

        if users.meta["result_count"] >= 900:
            return self.__is_follower(
                participant_id, user_id, total, users.meta["next_token"]
            )

        return False

    def __random_choice(self):
        conditions = self.conditions
        for i in conditions:
            if conditions[i]:
                try:  # turn existing data into sets
                    locals()[i] = set(getattr(self, i))
                except:
                    if i in ["retweet", "likes_tweet"]:
                        id_ = self.tweet_id
                    if i == "follow":
                        id_ = self.author_id

                    self.get_data(i, id_)
                    locals()[i] = set(getattr(self, i))

        locals_ = locals()
        sets = [locals_[i] for i in conditions if i in locals_]
        participants = list(set.intersection(*sets)) if sets != [] else None

        try:
            return random.choice(participants)
        except:
            pass

    def get_random_id(self, random_id=None, attempts=[]):
        random_choice = self.__random_choice

        if random_id == None:
            random_id = random_choice()

        if self.conditions["addtl_follow"]:
            if random_id != None:
                if self.__is_follower(random_id, self.addtl_id):
                    pass
                else:
                    attempts.append(random_id)
                    new_random_id = random_choice()
                    while new_random_id in attempts:
                        new_random_id = random_choice()
                    return self.get_random_id(self.conditions, random_id, attempts)
            else:
                self.get_data("addtl_flow", self.addtl_id)
                random_id = random_choice()

        return random_id

    def get_follows(self):
        return print(self.follow)


class GiveawayClass(GiveawayFunc):
    def start_giveaway(self):
        print("starting...")
        # create giveaway and begin calling twitter API to accumulate all followers in database
        if self.conditions["follow"]:
            self.get_data("follow", self.author_id)
        self.giveaway["follow"] = self.follow
        return giveaway

    def choose_winner(self, num_winners=1):
        assert num_winners <= 5
        if self.data_retreival_status["follow"] == "complete":
            # add up to 1000 new followers since creation of giveaway if the API call was completed
            new_followers = client.get_users_followers(self.author_id, max_results=1000)
            new_followers = set([user.id for user in new_followers.data])
            current_followers = set(self.follow)
            self.follow = list(
                current_followers | new_followers
            )  # updated follower list
            self.data_retreival_status["follow"] == "updated"

        self.winners = []
        i = 0
        while len(self.winners) < num_winners:
            if i == 20:
                return "Program was not able to find winner(s) that meet the conditions requested"
            winner_id = self.get_random_id()
            winner = client.get_user(id=winner_id).data
            winner = {"id": winner.id, "username": winner.name}
            if winner not in self.winners:
                self.winners.append(winner)
            i += 1
        #             print(i)

        self.giveaway["winners"] = self.winners

        return self.winners

    def instant_winner():
        pass

    def end_giveaway():
        pass
