from project2 import *

# only test TwitterAPI class. GUI is hard to test
twitter = TwitterAPI()

def test_TwitterAPI_twitter_auth_and_connect():
    url = "https://api.twitter.com/2/tweets/search/stream/rules"
    twitter = TwitterAPI()
    res_json = twitter.twitter_auth_and_connect(url)
    assert 'meta' in res_json

def test_TwitterAPI_analyze_sentiment():
    text = "You are a very VERY bad person!!!"
    score = twitter.analyze_sentiment(text)
    assert score < -0.25 # negative sentiment

def assert_tweets_structure(tweets):
    for tweet in tweets:
        assert 'sentiment' in tweet
        assert tweet['sentiment'] < 10
        assert tweet['sentiment'] > -10
        assert 'text' in tweet

def test_TwitterAPI_searchTweets():
    tweets = twitter.searchTweets('happy') #pretty much guaranteed to give results
    assert_tweets_structure(tweets)

def test_TwitterAPI_searchTweets_uncommon_word_1():
    tweets = twitter.searchTweets('sakljvidosjvdi') #not a word
    # shouldn't crash
    assert_tweets_structure(tweets)

def test_TwitterAPI_searchTweets_uncommon_word_2():
    tweets = twitter.searchTweets('^*&VC') #not a word
    assert_tweets_structure(tweets)

def test_TwitterAPI_searchTweets_uncommon_word_3():
    tweets = twitter.searchTweets('') #not a word
    assert_tweets_structure(tweets)

def test_TwitterAPI_searchTweets_uncommon_word_4():
    tweets = twitter.searchTweets('\n43-|\n') #not a word
    assert_tweets_structure(tweets)

def test_TwitterAPI_searchTweets_uncommon_word_5():
    tweets = twitter.searchTweets('h g p') #not a word
    assert_tweets_structure(tweets)
