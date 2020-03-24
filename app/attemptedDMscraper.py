import tweepy


from tweepy import Stream
from tweepy import OAuthHandler
from tweepy import API

from tweepy.streaming import StreamListener
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''


def set_up_twitter():  # Initial setup of the Twitter bot
    global auth
    global api
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

class StdOutListener(tweepy.StreamListener):

    def __init__( self ):
        self.tweetCount = 0

    def on_connect( self ):
        print("Connection established!!")

    def on_disconnect( self, notice ):
        print("Connection lost!! : ", notice)

    def on_data(self, status):
        print("Entered on_data()")
        print(status, flush = True)
        return True

    def on_direct_message(self, status):
        print("Entered on_direct_message()")
        try:
            print(status, flush = True)
            return True
        except BaseException as e:
            print("Failed on_direct_message()", str(e))

    def on_error( self, status ):
        print(status)

set_up_twitter()
myStreamListener = StdOutListener()
myStream = tweepy.Stream(auth=api.auth, listener=StdOutListener())
myStream.userstream()

#
# This was intended to be a direct message listener, intended to allow users to have full encryption process in private
# The part of the Tweepy Library tha controls this is dep however.
#
