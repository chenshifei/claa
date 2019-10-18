'''
A crawler for crawling tweets written in both CHN & ENG
'''

import itertools
import tweepy
from timeline_langs import TimelimeLangs

CONSUMER_KET = 'R0zGyOFgnANK35tcDdBxQ'
CONSUMER_SECRET = 'CiWNSJxmNwscHwRLoPWmor2mLQ5bph2k6BeFXRcM'

ACCESS_TOKEN = '53377747-Ny62mvPdRYDZ7xVGWP3KF56p0g43d8InmSYv6XX5R'
ACCESS_SECRET = 'BvSz95GWagY3fT2TCLBxaL5ChFXlFDO2s1ZmJgWCt6VgE'

auth = tweepy.OAuthHandler(CONSUMER_KET, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

C = ['是', '好']
E = ['is', 'good']
Q = ' OR '.join(list(map(lambda x: '(' + ' '.join(x) + ')', itertools.product(C, E))))
LIST_OWNER = 'dark_chenshifei'
LIST_NAME = 'bilingual'

CRAWLED_USERS = []

api = tweepy.API(auth)

def search_tweets_with_keyword(keyword):
    result = tweepy.Cursor(
        api.search,
        keyword,
        result_type='recent',
        count=200,
        lang='zh').items(200 * 10)
    return result

def crawl_user_tweets(username):
    if not username in CRAWLED_USERS:
        result = api.user_timeline(username, count=200)
        CRAWLED_USERS.append(username)
        return result

def get_list_member_ids(owner_screen_name, list_name):
    users = api.list_members(list_name, owner_screen_name)
    result = map(lambda x: x.id, users)
    return result

def add_member_to_list(member_id, owner_screen_name, list_name):
    api.add_list_member(slug=list_name, user_id=member_id, owner_screen_name=owner_screen_name)

def remove_member_from_list(member_id, owner_screen_name, list_name):
    api.remove_list_member(slug=list_name, user_id=member_id, owner_screen_name=owner_screen_name)

if __name__ == "__main__":
    candidates = search_tweets_with_keyword(Q)
    for tweet in candidates:
        screen_name = tweet.user.screen_name
        user_tweets = crawl_user_tweets(screen_name)
        if user_tweets:
            print('Identifying ' + screen_name, end='...')
            tl_langs = TimelimeLangs(user_tweets, tweet.user.id)
            if tl_langs.is_bilingual_user():
                print('bilingual ratio = {}, overall ratio = {}'.format(
                    tl_langs.bilingual_ratio, tl_langs.overall_ratio))
                # add_member_to_list(tweet.user.id, LIST_OWNER, LIST_NAME)
            else:
                print('no')
