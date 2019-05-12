# https://stackabuse.com/accessing-the-twitter-api-with-python/

import os
import sys
from sys import stdin, stdout
import argparse
import time
import datetime
import logging
import json
import csv
import twython as tw
from twython import Twython # pip install twython
from threading import Thread
from unidecode import unidecode # pip install unidecode

DEFAULT_CREDS_FILENAME = "twitter_credentials.json"

REQUIRED_FIELDS = ['CONSUMER_KEY',   
                   'CONSUMER_SECRET',
                   'ACCESS_TOKEN',
                   'ACCESS_SECRET']

# TODO: receive option from command line
LANGUAGES = ['en'] # languages to filter, or None if any

def process_tweet(tweet):
    d = {}
    d['hashtags'] = [hashtag['text'] for hashtag in tweet['entities']['hashtags']]
    d['text'] = tweet['text']
    d['user'] = tweet['user']['screen_name']
    d['user_loc'] = tweet['user']['location']
    return d

class TwitterStreamer(tw.TwythonStreamer):
    logger = logging.getLogger('TwitterStreamer')
    PRINT_DELTA = 100
    
    def __init__(self, creds, outfile, disconnect_on_failure=False):
        super(TwitterStreamer, self).__init__(
            app_key=creds['CONSUMER_KEY'],
            app_secret=creds['CONSUMER_SECRET'],  
            oauth_token=creds['ACCESS_TOKEN'],
            oauth_token_secret=creds['ACCESS_SECRET']
        )
        
        TwitterStreamer.logger.debug("credentials in costructor: %s", creds)
        TwitterStreamer.logger.debug("will disconnect on failure: %s", disconnect_on_failure)
        self.iteration = 0
        self.disconnect_on_failure = disconnect_on_failure
        self.outfile = outfile
        
        assert all([key in creds.keys() for key in REQUIRED_FIELDS]), "incomplete credentials, some fields are not defined ({})".format(", ".join(REQUIRED_FIELDS))
        

    # Received data
    def on_success(self, data):
        # Only collect tweets in English
        if self.iteration % TwitterStreamer.PRINT_DELTA == 0:
            TwitterStreamer.logger.info("iteration: %d", self.iteration)
        
        if LANGUAGES is None or data.get('lang', None) in LANGUAGES:
            self.iteration += 1
            self.save_raw(data, self.outfile)
            # tweet_data = process_tweet(data)
            # self.save_to_csv(tweet_data, self.outfile)

    # Problem with the API
    def on_error(self, status_code, data):
        TwitterStreamer.logger.error("status_code: %s; data: %s", status_code, data)
        # print(status_code, data)
        if self.disconnect_on_failure:
            TwitterStreamer.logger.error("disconnecting streamer ...")
            self.disconnect()

    def save_raw(self, tweet, outfile):
        TwitterStreamer.logger.debug("saving tweet to output file")
        json.dump(tweet, outfile)
        outfile.write("\n")
            
    # Save each tweet to csv file
    def save_to_csv(self, tweet, outfile):
        TwitterStreamer.logger.debug("saving to output file")
        writer = csv.writer(outfile)
        writer.writerow(list(tweet.values()))
        TwitterStreamer.logger.debug("tweets saved successfully")

def command_line_parser():
    """
    returns a dict with the options passed to the command line
    according with the options available
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--credentials_file", type=str,
                        help="json credentials file")

    parser.add_argument("-ck", "--consumer_key", type=str,
                        help="consumer key")

    parser.add_argument("-cs", "--consumer_secret", type=str,
                        help="consumer secret")

    parser.add_argument("-at", "--access_token", type=str,
                        help="access token")

    parser.add_argument("-as", "--access_secret", type=str,
                        help="access secret")

    parser.add_argument("-hf", "--hashtags_file", type=str, required=True,
                        help="hashtags file")

    parser.add_argument("-o", "--output", type=str, default="fetched.csv",
                        help="output file name")

    parser.add_argument("-v", "--verbose", action='store_true',
                        help="verbose output")

    parser.add_argument("--no_retry", action='store_false',
                        help="verbose output")

    args = parser.parse_args()

    return args

def main():
    options = command_line_parser()

    logging.basicConfig(level=logging.DEBUG if options.verbose else logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='./fetcher.log',
                        filemode='w')

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    ################ APPLICATION STARTS ################
    
    cred_file = options.credentials_file
    
    if cred_file is None:
        with open(DEFAULT_CREDS_FILENAME, "w") as f:
            credentials = {}
            credentials['CONSUMER_KEY']    = options.consumer_key
            credentials['CONSUMER_SECRET'] = options.consumer_secret
            credentials['ACCESS_TOKEN']    = options.access_token
            credentials['ACCESS_SECRET']   = options.access_secret

            assert all([i is not None for i in credentials.values()]), "some credential parameters are not defined"
            
            json.dump(credentials, f)
            cred_file = DEFAULT_CREDS_FILENAME

    with open(cred_file, "r") as f:
        creds = json.load(f)

    assert all([key in creds.keys() for key in REQUIRED_FIELDS]), "json incomplete, some fields are not defined ({})".format(", ".join(REQUIRED_FIELDS))

    with open(options.hashtags_file, "r") as hashtags_f:
        hashtags = list(set([i.strip() for i in hashtags_f.readlines()]))

    outfile = open(options.output, "a")
        
    stream = TwitterStreamer(creds, outfile)

    flag = True
    while flag:
        try:
            stream.statuses.filter(track=",".join(hashtags),
                                   language=",".join(LANGUAGES))
        except Exception as ex:
            console.error("error on stremer: %s", ex)
            flag = options.no_retry
    
    
if __name__ == "__main__":
    main()
