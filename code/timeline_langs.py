import itertools
import logging
import cld3
import preprocessor as p

MIN_BILINGUAL_RATIO = 0.5
MIN_OVERALL_PROP = 0.8
MIN_LANG_CONFIDENCE = 0.3
MIN_INTWEET_PROP = 0.3
MIN_LEN = 100

LANG_ID_1 = 'en'
LANG_ID_2 = 'zh'

logging.getLogger('polyglot').setLevel(logging.ERROR)

class TimelimeLangs:
    def __init__(self, tweets, user_id=0):
        self.langs = []
        self._meta_langs = []
        self.user_id = user_id
        self.bilingual_ratio = 0
        self.overall_ratio = 0
        self.detect(tweets)

    def detect(self, tweets):
        for tweet in tweets:
            self._detect_tweet(tweet)

        self.langs = list(itertools.chain(*self._meta_langs))

        num_lang1 = self.langs.count(LANG_ID_1)
        num_lang2 = self.langs.count(LANG_ID_2)

        if max(num_lang1, num_lang2):
            self.bilingual_ratio = min(num_lang1, num_lang2) / max(num_lang1, num_lang2)
        if self.langs:
            self.overall_ratio = (num_lang1 + num_lang2) / len(self.langs)

    def _detect_tweet(self, tweet):
        if hasattr(tweet, "retweeted_status"):
            return
        tweet_langs = []
        clean_text = p.clean(tweet.text)
        candidates = cld3.get_frequent_languages(clean_text, num_langs=3)
        for lang in candidates:
            if lang.probability > MIN_LANG_CONFIDENCE and lang.proportion > MIN_INTWEET_PROP:
                tweet_langs.append(lang.language[:2])
        self._meta_langs.append(tweet_langs)

    def is_bilingual_user(self):
        if self.bilingual_ratio > MIN_BILINGUAL_RATIO and \
            self.overall_ratio > MIN_OVERALL_PROP and \
            len(self._meta_langs) > MIN_LEN:
            return True
        return False
