import argparse
import datetime
import json
import os
import random
from datetime import datetime as dt

import requests
import tweepy

troll_hashtags = [
    "istandwithrussia",
    "istandwithputin",
]

love_hashtags = [
    "istandwithukraine",
    "fuckputin",
]

love_answers = [
    "💙💛",
    "🇺🇦",
    "I ❤️ 🇺🇦",
    "#IStandWithUkraine",
    "#FuckPutin ❤️ 🇺🇦",
    "слава Україні",
]

troll_answers = [
    "🇺🇦",
    "#istandwithukraine",
    "#putinzbrodniarzwojenny",
    "free Ukraine",
    "#UkraineWillRemainFree",
    "#BlueYellowFreedom 🇺🇦",
    "nie strasz nie strasz, bo się zesrasz",
    "#putinwarcriminal",
    "#russiaIsTheOnlyNazi",
    "#Srussia",
    "#handsOffUkraine",
    "#fuckPutin",
    "#ZisTheNewSvastika",
    "слава Україні",
]


BEARER_TOKEN = os.environ["BEARER_TOKEN"]
CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]
EXCHANGE_URL = os.environ["EXCHANGE_URL"]


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

    def get_tweets(self, hashtags):
        joined_hashtags = "(" + " OR ".join(hashtags) + ")" + " -from:FuckPutinBot"
        print(joined_hashtags)
        return self.client.search_recent_tweets(
            joined_hashtags,
            max_results=100,
            start_time=dt.utcnow() - datetime.timedelta(hours=1),
            end_time=dt.utcnow() - datetime.timedelta(minutes=10),
        )

    def _check_exchange(self):
        response = requests.get(self.exchange_url)
        return float(response.json()['rates']['RUB'])

    def calculate_rub_weight(self):
        coins = self._check_exchange() / 10
        return round(coins * 5.63, 2)

    def reply_to_tweet(self, tweet_id, answers):
        try:
            self.client.create_tweet(
                in_reply_to_tweet_id=tweet_id,
                text=random.choice(answers),
            )
        except tweepy.errors.Forbidden:
            print(f"Couldn't reply to tweet {tweet_id}, forbidden")

    def answer(self, tweets, answers):
        if tweets.data:
            with open("seen.json", "r+") as f:
                already_seen_tweets = json.loads(f.read())
                f.seek(0)

                for tweet in tweets.data:
                    if tweet.id not in already_seen_tweets:
                        print(tweet)
                        self.reply_to_tweet(tweet.id, answers)
                        already_seen_tweets[tweet.id] = "DONE"

                f.write(json.dumps(already_seen_tweets))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--troll', help='Start trolling', action=argparse.BooleanOptionalAction)
    parser.add_argument('--love', help='Start trolling', action=argparse.BooleanOptionalAction)
    parser.add_argument('--tweet-exchange-weight',
                        help='Tweet how many grams of rubles is worth 1$',
                        action=argparse.BooleanOptionalAction)

    args = parser.parse_args()
    bot = TwitterBot()

    if args.troll:
        tweets = bot.get_tweets(troll_hashtags)
        bot.answer(tweets, troll_answers)

    if args.love:
        tweets = bot.get_tweets(love_hashtags)
        bot.answer(tweets, love_answers)

    if args.tweet_exchange_weight:
        bot.client.create_tweet(
            text=f"1 USD weights {bot.calculate_rub_weight()}g of RUB, on {dt.now().isoformat()}"
        )
