import twitter
import config
import time
import csv

# initialize api instance
twitter_api = twitter.Api(consumer_key=config.consumer_key,
                          consumer_secret=config.consumer_secret,
                          access_token_key=config.access_token,
                          access_token_secret=config.access_secret)


def build_test_set(search_keyword):
    try:
        tweets_fetched = twitter_api.GetSearch(search_keyword, count=100)
        print("Fetched " + str(len(tweets_fetched)) + " tweets for the term " + search_keyword)
        return [{"text": status.text, "label": None} for status in tweets_fetched]
    except:
        print("Something went wrong in build_test_set()")
        return None


def build_training_set(corpus_file, tweet_data_file):
    return