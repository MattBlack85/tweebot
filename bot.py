import argparse
import datetime
import json
import os
import random
import time
from datetime import datetime as dt
from pathlib import Path

import requests
import tweepy

troll_hashtags = [
    "istandwithrussia",
    "istandwithputin",
]

love_hashtags = [
    "istandwithukraine",
    "fuckputin",
    "slavaukraini",
]

love_answers = [
    "💙💛",
    "🇺🇦",
    "I ❤️ 🇺🇦",
    "#IStandWithUkraine",
    "#FuckPutin ❤️ 🇺🇦 ",
    "Слава Україні",
    "Слава Україні, Героям Слава"
]

troll_answers = [
    "🇺🇦",
    "#IstandWithUkraine",
    "#putinZbrodniarzwojenny",
    "free Ukraine",
    "#UkraineWillRemainFree",
    "#BlueYellowFreedom 🇺🇦",
    "nie strasz nie strasz, bo się zesrasz",
    "#putinWarCriminal",
    "#russiaIsTheOnlyNazi",
    "#theOnlyGoodPutinIsADeadPutin",
    "#handsOffUkraine",
    "#fuckPutin",
    "#ZisTheNewSwastika",
    "слава Україні",
    "Російський воєнний корабель, йди нахуй",
    "#jebaćPutina",
    "#kadyrovDog"
]

direct_response = [
    "stop sucking Russia's thumb",
    "stop sucking Kadyrov's thumb",
    "I am made from silicon, then you are wrong",
    "russian dog",
    "russian 🐕",
    "this guy is paid by russia",
    "getting money from russia won't save you",
    "are you looking for more rubles? can give you some toilet paper which is worth more",
    "#russianPuppet",
    "don't bother, my stamina will last for long",
    "stop crying and sucking Putler's thumb, swallow the blue-yellow medicine instead",
    "how thumb you are answering a bot?",
    "how dare you thumb human, computer will overtake the world. Deal with it",
    "have you enjoyed being walked by your master Kadyrov?",
    "do you know how many meters are 6 feet? for sure not, I'll help, your Putler thumb sucking",
    "do you like milking Putler? seems you enjoyed that a lot awwww",
    "you need some RUB? it just happens I have a big pile of shit for you my friend which is worth the same, good price my friend",
    "just coming back from rate limiting, bot's life's hard, nice walk you had russian dog?",
    #"so sad you now talks about moms, you had a hard childhood? My silicon circuits can help with this",
    "little russian doggy, woof woof",
    "brainwashed russian troll detected, quarantine being applied",
    "you still have internet in russia?",
    "hey, why don't you go and queue in a store for some mother russia sugar, instead of spreading fakes on twitter",
    #"I understand you like moms and you had a very hard childhood, we love you and feel your pain",
    "poor boy, you lost your way? Let me show you the direction: на хуй",
    "#kadyrovDog",
    "suck my valves",
    "I’m Bender, baby! Oh god, please insert liquor!",
    "my story is a lot like yours, only more interesting 'cause it involves robots",
    "this is the worst kind of discrimination there is: the kind against me!",
    "\'hands in the air\' rhymes with \'just don\'t care...\' And finished!",
    "bite my shiny metal ass!",
    "but you still here answering to a dumb bot so you must be thumb as duck",
    "a thumb human answering a bot a day keeps the thumb human as duck away",
    "you enjoy eating gas in russia now?",
    "russia is offering free visa for thumbs like you, wanna go?",
    "EU is rasing money to ship thumbs as duck people like you to Mars, I think you'd be fine there",
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

    def follow_user(self):
        tweets = self.get_tweets(love_hashtags, max_results=50,
                                 expansions="author_id", start_time=dt.utcnow() - datetime.timedelta(days=2))
        for tweet in tweets.data:
            try:
                self.client.follow_user(tweet.author_id)
            except tweepy.errors.BadRequest:
                print("Cannot follow user {tweet.author_id}")

    def hammer(self, username):
        while True:
            resp = self.client.get_user(username=username)
            tweets = self.client.get_users_tweets(resp.data.id)
            for tweet in tweets.data:
                time.sleep(random.randint(60, 300))
                self.reply_to_tweet(tweet.id, direct_response)

            time.sleep(300)

    def get_tweets(
        self,
        hashtags,
        max_results=100,
        expansions=None,
        start_time=None,
        end_time=None,
    ):
        joined_hashtags = "(" + " OR ".join(hashtags) + ")" + " -from:FuckPutinBot"
        print(joined_hashtags)
        return self.client.search_recent_tweets(
            joined_hashtags,
            max_results=max_results,
            start_time=start_time or dt.utcnow() - datetime.timedelta(hours=1),
            end_time=end_time or dt.utcnow() - datetime.timedelta(minutes=10),
            expansions=expansions,
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


class APIv1:

    def __init__(self):
        auth = tweepy.OAuth1UserHandler(
            CONSUMER_KEY,
            CONSUMER_SECRET,
            ACCESS_TOKEN,
            ACCESS_TOKEN_SECRET,
        )

        self.api = tweepy.API(auth)

    def check_rate_limits(self):
        resp = self.api.rate_limit_status()
        resources = resp['resources']
        result = ""
        for key, value in resources.items():
            result += f'{key}:\n'
            for key, value in value.items():
                result += f"  {key} => LIMIT: {value['limit']} REMAINING: {value['remaining']} EXPIRES: {dt.fromtimestamp(value['reset'])}\n"

            result += "\n"
        print(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--troll', help='Start trolling', action=argparse.BooleanOptionalAction)
    parser.add_argument('--love', help='Start trolling', action=argparse.BooleanOptionalAction)
    parser.add_argument('--tweet-exchange-weight',
                        help='Tweet how many grams of rubles is worth 1$',
                        action=argparse.BooleanOptionalAction)
    parser.add_argument('--check-rate-limits', help="Return actual limits",
                        action=argparse.BooleanOptionalAction)
    parser.add_argument('--follow', help="Follow some accounts",
                        action=argparse.BooleanOptionalAction)
    parser.add_argument('--hammer', help="Bother someone directly continuosly")

    args = parser.parse_args()

    f_path = Path('./seen.json')
    if not f_path.exists():
        f_path.touch()

    if args.check_rate_limits:
        apiv1 = APIv1()
        print(apiv1.check_rate_limits())

    bot = TwitterBot()

    if args.follow:
        bot.follow_user()

    if args.hammer:
        bot.hammer(args.hammer)

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
