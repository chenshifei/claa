import itertools
import logging
from polyglot.detect import Detector

BILINGUAL_RATIO = 0.2
MIN_OVERALL_RATIO = 0.7
MIN_LANG_CONFIDENCE = 30

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
            tweet_langs = []
            detector = Detector(tweet.text, quiet=True)
            for lang in detector.languages:
                if lang.confidence > MIN_LANG_CONFIDENCE:
                    tweet_langs.append(lang.code[:2])
            self._meta_langs.append(tweet_langs)

        self.langs = list(itertools.chain(*self._meta_langs))

        num_lang1 = self.langs.count(LANG_ID_1)
        num_lang2 = self.langs.count(LANG_ID_2)

        if max(num_lang1, num_lang2):
            self.bilingual_ratio = min(num_lang1, num_lang2) / max(num_lang1, num_lang2)
        if self.langs:
            self.overall_ratio = (num_lang1 + num_lang2) / len(self.langs)

    def is_bilingual_user(self):
        if self.bilingual_ratio > BILINGUAL_RATIO and \
            self.overall_ratio > MIN_OVERALL_RATIO:
            return True
        return False
