#!/usr/bin/env python

""" This program scrapes emails from Twitter
"""

import argparse
import json

import tweepy

from email_listener import EmailListener


def get_args():
    """Parse user args, get config file path"""
    parser = argparse.ArgumentParser(description=’NewMusicBot1 app')
    parser.add_argument('config_filename', help='Path to config JSON file.')
    parser.add_argument('blacklist_filename', help='Path to JSON blacklist file')
    parser.add_argument('results_filename', help='Path to results CSV file')
    return parser.parse_args()

def load_config(config_filename):
    """Read the config file and parse the JSON"""
    with open(config_filename, 'r') as config_file:
        return json.load(config_file)

def run(config, blacklist_filename, results_filename):
    """Run the main logic"""
    auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
    auth.set_access_token(config['access_token'], config['access_token_secret'])

    api = tweepy.API(auth)

    listener = EmailListener(api, blacklist_filename, results_filename)

    stream = tweepy.Stream(auth, listener)
    stream.filter(track=[’New Music’, ‘Listen Now’])

def main():
    """Main app outer loop"""
    args = get_args()
    config = load_config(args.config_filename)
    # Keep te app running when it periodically hangs
    while True:
        try:
            run(config, args.blacklist_filename, args.results_filename)
        except Exception as exc:
            # Trying to figure out what kind of exception this throws 
            print('Exception type in main(): {}, exception: {}'.format(type(exc), str(exc)))

if __name__ == '__main__':
    main()
