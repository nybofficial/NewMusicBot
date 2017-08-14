import re
import traceback
import json

from tweepy.streaming import StreamListener


class EmailListener(StreamListener):

    pattern = re.compile(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+)')

    def __init__(self, api, blacklist_filename, results_filename, *args, **kwargs):
        super(StreamListener, self).__init__(*args, **kwargs)
        self.api = api
        self.blacklist_filename = blacklist_filename
        self.results_filename = results_filename
        self.results = set()
        self.cached_csv = None

    def on_status(self, status):
        try:
            match = self.pattern.search(status.text)
            if match:
                email = match.group(1)
                if not hasattr(status, 'retweeted_status') and not self.user_blacklisted(status):
                    self._log_to_csv(status.id, status.text, email)
                    self.api.retweet(status.id)
        except Exception as exc:
            # Trying to figure out what kind of exception this throws
            print('Exception[{}] in on_status: {}, text: {}'.format(type(exc), str(exc), status.text))
            traceback.print_stack()

    def on_error(self, status_code):
        print('Error: {}'.format(status_code))
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False

    def user_blacklisted(self, status):
        """Check if user is blacklisted.

        Load the file every time instead of caching it because it is small.
        """
        with open(self.blacklist_filename, 'r') as blacklist_file:
            if status.author.screen_name in json.loads(blacklist_file.read()):
                return True
            return False

    def _log_to_csv(self, tweet_id, tweet_text, email):
        """Save results to a csv logfile"""
        self._load_csv()
        if email in self.results or email in self.cached_csv:
            return
        with open(self.results_filename, 'a') as results_file:
            # Strip commas from the text to make this a valid 3 column csv file
            text_cleaned = tweet_text.replace(',', '').replace('\n', '')
            results_file.write('{},{},{}\n'.format(tweet_id, text_cleaned, email))
        self.results.add(email)

    def _load_csv(self):
        """Load csv file into memory"""
        if not self.cached_csv:
            with open(self.results_filename, 'r') as results_file:
                self.cached_csv = results_file.read()
