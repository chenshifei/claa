'''
A crawler for crawling tweets written in both CHN & ENG
'''

import tweepy
import itertools

CONSUMER_KET = 'R0zGyOFgnANK35tcDdBxQ'
CONSUMER_SECRET = 'CiWNSJxmNwscHwRLoPWmor2mLQ5bph2k6BeFXRcM'

ACCESS_TOKEN = '53377747-Ny62mvPdRYDZ7xVGWP3KF56p0g43d8InmSYv6XX5R'
ACCESS_SECRET = 'BvSz95GWagY3fT2TCLBxaL5ChFXlFDO2s1ZmJgWCt6VgE'

auth = tweepy.OAuthHandler(CONSUMER_KET, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

C = ['的', '一']
E = ['the', 'of']

Q = ' OR '.join(list(map(lambda x: '(' + ' '.join(x) + ')', itertools.product(C, E))))
print(Q)
LANG_SET = set(['en', 'zh'])
RATIO = 0.2
LIST_OWNER = 'dark_chenshifei'
LIST_NAME = 'bilingual'

api = tweepy.API(auth)

def search_tweets_with_keyword(keyword):
    result = tweepy.Cursor(
        api.search,
        keyword,
        result_type='recent',
        count=200,
        lang='en').items(200 * 10)
    return result

def crawl_user_tweets(username):
    result = api.user_timeline(username, count=200)
    return result

def is_bilingual_user(tweets, ratio):
    langs = set()
    for tweet in tweets:
        langs.add(tweet.lang)

    ratio = calculate_lang_ratio(tweets)

    if len(langs & LANG_SET) >= 2 and ratio > RATIO:
        return True

    return False

def calculate_lang_ratio(tweets):
    langs = []
    for tweet in tweets:
        langs.append(tweet.lang)

    num_en = langs.count('en')
    num_zh = langs.count('zh')
    result = min(num_en, num_zh) / max(num_en, num_zh)
    return result

def get_list_member_ids(owner_screen_name, list_name):
    users = api.list_members(list_name, owner_screen_name)
    result = map(lambda x: x.id, users)
    return result

def add_member_to_list(member_id, owner_screen_name, list_name):
    api.add_list_member(slug=list_name, user_id=member_id, owner_screen_name=owner_screen_name)

if __name__ == "__main__":
    candidates = search_tweets_with_keyword(Q)
    for tweet in candidates:
        screen_name = tweet.user.screen_name
        user_tweets = crawl_user_tweets(screen_name)
        ratio = calculate_lang_ratio(user_tweets)
        if is_bilingual_user(user_tweets, ratio):
            print('Potential user = {}, ratio = {}'.format(screen_name, ratio))
            add_member_to_list(tweet.user.id, LIST_OWNER, LIST_NAME)
