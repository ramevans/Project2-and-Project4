import requests
import json
import ast
import yaml
import urllib.parse
import tkinter as tk
import os
from google.oauth2 import service_account

# https://cloud.google.com/natural-language/docs/reference/libraries#windows
# $env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\username\Downloads\my-key.json"
# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

def process_yaml():
    try:
        with open("config.yaml") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        #use environment variable
        bearer_token = os.environ['TWITTER_BEARER_TOKEN']
        return {'search_tweets_api': {'bearer_token': bearer_token}}

def create_bearer_token(data):
    return data["search_tweets_api"]["bearer_token"]

def print_tweet(tweet):
    print('-----------------------------------------------------')
    print('Tweet ID: ', tweet['id'])
    print(tweet['text'])
    print(tweet['created_at'])
    print('Sentiment Score: ', tweet['sentiment'])
    print('-----------------------------------------------------')

class TwitterAPI:
    def __init__(self):
        data = process_yaml()
        self.bearer_token = create_bearer_token(data)

        if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
            self.google = language.LanguageServiceClient()
        else:
            service_account_info = json.loads(os.environ['GOOGLE_SECRET'])
            credentials = service_account.Credentials.from_service_account_info(service_account_info)
            self.google = language.LanguageServiceClient(credentials=credentials)

    def twitter_auth_and_connect(self, url):
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
        response = requests.request("GET", url, headers=headers)
        return response.json()

    def analyze_sentiment(self, tweet):
        document = types.Document(
            content=tweet,
            type=enums.Document.Type.PLAIN_TEXT)

        # Detects the sentiment of the text
        sentiment = self.google.analyze_sentiment(document=document).document_sentiment
        return sentiment.score

    def searchTweets(self, query, max_tweets=20):
        query = urllib.parse.quote(query)
        url = 'https://api.twitter.com/1.1/search/tweets.json?q={}&result_type=mixed&count={}'.format(query,max_tweets)
        res_json = self.twitter_auth_and_connect(url)
        tweets = []
        if 'statuses' in res_json:
            for tweet in res_json['statuses']:
                try:
                    tweet['sentiment'] = self.analyze_sentiment(tweet['text'])
                except:
                    # sometimes this doesn't work because of symbols, langauge etc.
                    tweet['sentiment'] = 0
                tweets.append(tweet)
        return tweets

def doSearch():
    print("Searching for tweets containing: ", keywords.get())
    twitter = TwitterAPI()
    tweets = twitter.searchTweets(keywords.get(), 100)
    for tweet in tweets:
        print_tweet(tweet)

    sentiments = []
    num_neg = 0
    num_pos = 0
    num_neu = 0
    for tweet in tweets:
        s = tweet['sentiment']
        sentiments.append(s)
        if s < -0.25:
            num_neg += 1
        elif s > 0.25:
            num_pos += 1
        else:
            num_neu += 1

    mean = sum(sentiments)/len(sentiments)
    print('Number of negative tweets:',num_neg)
    print('Number of positive tweets:',num_pos)
    print('Number of neutral tweets:',num_neu)
    print('mean sentiment score:',mean)

    # Make a graphic representation of sentiments
    TOTAL_LEN = 200
    red_len = int(TOTAL_LEN * num_neg/len(sentiments))
    green_len = int(TOTAL_LEN * num_pos/len(sentiments))
    tan_len = int(TOTAL_LEN * num_neu/len(sentiments))

    canvas.create_rectangle(50, 20, red_len+50, 50, fill="red")
    canvas.create_rectangle(red_len+50, 20, tan_len+red_len+50, 50, fill="#D2B48C")
    canvas.create_rectangle(tan_len+red_len+50, 20, green_len+tan_len+red_len+50, 50, fill="green")

    # Extract most negative and most positive tweets:
    # Order by Sentiment:
    tweets_sorted = sorted(tweets, key=lambda k: k['sentiment'])
    text.delete('1.0', tk.END)
    text.insert(tk.END, "Most negative tweet:\n")
    text.insert(tk.END, tweets_sorted[0]['text'] + '\n')
    text.insert(tk.END, 'Sentiment Score: ' + str(tweets_sorted[0]['sentiment']) + '\n')
    text.insert(tk.END, '\n')
    text.insert(tk.END, "Most positive tweet:\n")
    text.insert(tk.END, tweets_sorted[-1]['text'] + '\n')
    text.insert(tk.END, 'Sentiment Score: ' + str(tweets_sorted[-1]['sentiment']) + '\n')

if __name__ == "__main__":

    root = tk.Tk()
    tk.Label(root,
             text="Keywords: ").grid(row=0)
    keywords = tk.Entry(root)
    keywords.grid(row=0, column=1)
    canvas = tk.Canvas(root, width=800, height=60, borderwidth=0, highlightthickness=0, bg="white")
    canvas.grid(row=1,column=2)
    text = tk.Text(root, height=10, width=100)
    text.grid(row=2,column=2)
    tk.Button(root,
              text='Search', command=doSearch).grid(row=3,
                                                           column=1,
                                                           sticky=tk.W,
                                                           pady=4)
    tk.mainloop()
