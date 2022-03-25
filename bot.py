import json
import os
import random

import requests
import tweepy

hashtags = [
    "istandwithrussia",
    "istandwithputin",
]

answers = [
    "🇺🇦",
    "#istandwithukraine",
    "#putinzbrodniarzwojenny",
    "freeukraine",
    "nie strasz nie strasz, bo się zesrasz",
]


BEARER_TOKEN = os.environ["BEARER_TOKEN"]
CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]
EXCHANGE_URL = os.environ["EXCHANGE_API"]


class TwitterBot:
    exchange_url = f"http://api.exchangeratesapi.io/v1/latest?access_key={EXCHANGE_URL}&symbols=USD,RUB&format=1"

    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=BEARER_TOKEN,
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET,
        )

    def get_tweets(self):
        joined_hashtags = ",".join(hashtags)
        return self.client.search_recent_tweets(
            joined_hashtags,
            max_results=100,
            start_time="2022-03-23T00:00:00Z",
            end_time="2022-03-23T23:59:59Z",
        )

    def _check_exchange(self):
        response = requests.get(self.exchange_url)
        return float(response.json()['rates']['RUB'])

    def calculate_rub_weight(self):
        coins = self._check_exchange() // 10
        return coins * 5.63

    def reply_to_tweet(self, tweet_id):
        self.client.create_tweet(
            in_reply_to_tweet_id=tweet_id,
            text=random.choice(answers),
        )

    def answer(self, tweets):
        just_seen = {}

        with open("seen.json", "r+") as f:
            already_seen_tweets = json.loads(f.read())
            f.seek(0)

            for tweet in tweets.data:
                if tweet.id not in already_seen_tweets:
                    print(tweet)
                    self.reply_to_tweet(tweet.id)
                    just_seen[tweet.id] = "DONE"

            f.write(json.dumps(already_seen_tweets))


if __name__ == '__main__':
    bot = TwitterBot()
    tweets = bot.get_tweets()
    bot.answer(tweets)
    #bot.client.create_tweet(text=f"1 USD weights {bot.calculate_rub_weight()}g of RUB")
