from flask import Flask, json, request
import tweepy
from tweepy import OAuthHandler

ckey = 'QnxYONDqyBGXUQOPhSCRVixFu'
csecret = 'UJ5IjcQAWWIqtHFA9gsEgFZiSJtsN1rfY5jeAZUJDL3992CbvL'
atoken = '1029968149595267074-YXQ8C3GHHWKMsb6iftSDlKoi1rNLJz'
asecret = 'CUSbmCkyKclGnBpQciRiIWZz3U2UOMr7JYoA4KGmnOtMm'

app = Flask(__name__)

auth = OAuthHandler(ckey,csecret)
auth.set_access_token(atoken, asecret)

api = tweepy.API(auth)


results = api.search(q="")

for result in results:
	tweet=result.text
	savefile = open('positive.csv', 'a')
	savefile.write(tweet)
	savefile.write('\n\n')
	savefile.close()
	print (tweet)