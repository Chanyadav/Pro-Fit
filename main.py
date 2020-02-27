import datetime

import tweepy as tw
import pandas as pd

import nltk
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
from flask import Flask, render_template, request, json
from pytz import timezone

app = Flask(__name__)


def read_article_list(lst):
    article = lst
    sentences = []

    for sentence in article:
        sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
    sentences.pop()

    return sentences


def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []

    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]

    all_words = list(set(sent1 + sent2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1

    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)


def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2:  # ignore if both are same sentences
                continue
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix


def generate_summary(original, lst, top_n, features):
    nltk.download("stopwords")
    stop_words = stopwords.words('english')
    summarize_text = []

    # Step 1 - Read text anc split it
    sentences = read_article_list(lst)

    # Step 2 - Generate Similary Martix across sentences
    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

    # Step 3 - Rank sentences in similarity martix
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)

    # Step 4 - Sort the rank and pick top sentences
    ranked_sentence = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    print("Generating...")
    for i in range(top_n):
        summarize_text.append(" ".join(ranked_sentence[i][1]))

    # Step 5 - Offcourse, output the summarize texr
    b = (summarize_text)
    final = ""

    splt = original.split(".")
    for sent in splt:
        found = False
        stp_words = []
        for temp in sent.split(" "):
            if temp not in stop_words:
                stp_words.append(temp)
        for each in features:
            print(each)
            print(stp_words)
            if each in stp_words:
                final += sent
                final += features[each]
                found = True
        if not found:
            final += sent
    return final


# let's begin
original = "A nice graphics scheme with better development process is needed. A high quality signal strength  is needed "

features = {}
features["graphics"] = " Another graphics version for  a simpler  will be added "

lst = []
'''lst.append("A more better version of the app could be released with updated game features for shooting")
lst.append(
    "This version of the game is arguably better than pc version in terms of portability but it could have better graphics.  I thought things like graphics could have been improved")
lst.append("Graphics Quality could be improved")'''

#print(original)
#print(generate_summary(original, lst, 2, features))


class ProFit():

    def __init__(self):
        self.consumer_key = 'yVH0IRkGKvjrtEKsGnpOdTcBB'
        self.consumer_secret = '0jirUzkOKPiKZXPdMEmRnJhsavAklze2cQGuByEw4OdWzM6LEq'
        self.access_token = '3033103218-7Mt5Uhb4QYtkKgWSFweMkZ1IOXDh3TB8OVq054Q'
        self.access_token_secret = 'QUneZ3BD2fBWorMdVqVqgrueIvBIZRB94GEInkAOjxJE1'
        self.searchTweetid = "1231435960639873025"

        auth = tw.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tw.API(auth, wait_on_rate_limit=True)
        self.post = "A nice graphics scheme with better development process is needed. A high quality signal strength  is needed "

    def reply_to_post(self, msg):
        print(msg)
        self.api.update_status(in_reply_to_status_id=self.searchTweetid, status=msg)
        print("Successfully posted tweet!!")

    def watch_post(self):
        # Define the search term and the date_since date as variables
        start_date = datetime.datetime(2020, 2, 1, 0, 0, 0)
        to_search = "to:srini_vasan23"
        while True:
            tweets = tw.Cursor(self.api.search,
                               q=to_search,
                               sinceId=self.searchTweetid,
                               lang="en").items(50)

            A = []
            # Iterate and print tweets
            print("Listening...")
            for tweet in tweets:
                if tweet.in_reply_to_status_id_str == self.searchTweetid and tweet.created_at > start_date:
                    A.append(tweet.text)
            print("Printing A...")
            print(A)
            if len(A) >= 3:
                print("Calling generate function...")
                msg = generate_summary(self.post, A, 2, features)
                self.reply_to_post(msg)
                start_date = datetime.datetime.utcnow()


pro_fit = ProFit()
pro_fit.watch_post()
