'''
A crawler for crawling tweets written in both CHN & ENG
'''

import csv
import itertools
import sys
import tweepy
from timeline_langs import TimelimeLangs

CONSUMER_KET = 'R0zGyOFgnANK35tcDdBxQ'
CONSUMER_SECRET = 'CiWNSJxmNwscHwRLoPWmor2mLQ5bph2k6BeFXRcM'

ACCESS_TOKEN = '53377747-Ny62mvPdRYDZ7xVGWP3KF56p0g43d8InmSYv6XX5R'
ACCESS_SECRET = 'BvSz95GWagY3fT2TCLBxaL5ChFXlFDO2s1ZmJgWCt6VgE'

auth = tweepy.OAuthHandler(CONSUMER_KET, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

C = ['在', '有']
E = ['at', 'have', 'has']
Q = ' OR '.join(list(map(lambda x: '(' + ' '.join(x) + ')', itertools.product(C, E))))
LIST_OWNER = 'dark_chenshifei'
LIST_NAME = 'bilingual'

CRAWLED_USERS = []

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

def search_tweets_with_keyword(keyword):
    result = tweepy.Cursor(
        api.search,
        keyword,
        result_type='recent',
        count=200,
        lang='zh').items(200 * 5)
    return result

def crawl_user_tweets(username, brief=True):
    if not username in CRAWLED_USERS:
        CRAWLED_USERS.append(username)
        result = []
        try:
            if brief:
                result = api.user_timeline(username, count=200, trim_user=True, include_rts=False)
            else:
                result = api.user_timeline(username, trim_user=True, include_rts=False)
        except tweepy.TweepError as exp:
            print('Error when cralwing ', username)
            print(exp)
        return result

def get_list_members(owner_screen_name, list_name):
    result = tweepy.Cursor(
        api.list_members, slug=list_name, 
        owner_screen_name=owner_screen_name).items()
    return result

def add_member_to_list(member_id, owner_screen_name, list_name):
    api.add_list_member(slug=list_name, user_id=member_id, owner_screen_name=owner_screen_name)

def remove_member_from_list(member_id, owner_screen_name, list_name):
    api.remove_list_member(slug=list_name, user_id=member_id, owner_screen_name=owner_screen_name)

def crawl_bilingual_users():
    candidates = search_tweets_with_keyword(Q)
    for tweet in candidates:
        screen_name = tweet.user.screen_name
        user_tweets = crawl_user_tweets(screen_name)
        if user_tweets:
            print('Identifying ' + screen_name + ' ...', end='')
            tl_langs = TimelimeLangs(user_tweets, tweet.user.id)
            if tl_langs.is_bilingual_user():
                print('bilingual ratio = {}, overall ratio = {}'.format(
                    tl_langs.bilingual_ratio, tl_langs.overall_ratio))
                add_member_to_list(tweet.user.id, LIST_OWNER, LIST_NAME)
            else:
                print('no')

def validate_bilingual_users():
    candidates = get_list_members(LIST_OWNER, LIST_NAME)
    for user in candidates:
        screen_name = user.screen_name
        user_tweets = crawl_user_tweets(screen_name,)
        if user_tweets:
            print('Identifying ' + screen_name + ' ...', end='')
            tl_langs = TimelimeLangs(user_tweets, user.id)
            if tl_langs.is_bilingual_user():
                print('bilingual ratio = {}, overall ratio = {}'.format(
                    tl_langs.bilingual_ratio, tl_langs.overall_ratio))
            else:
                print('no')
                remove_member_from_list(user.id, LIST_OWNER, LIST_NAME)

def crawl_user_timelines():
    candidates = get_list_members(LIST_OWNER, LIST_NAME)
    with open('../data/tweets_original.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['id_str', 'screen_name', 'raw_text'])
        for idx, user in enumerate(candidates):
            screen_name = user.screen_name
            print('crawling user {}, name = {}'.format(idx, screen_name))
            user_tweets = tweepy.Cursor(api.user_timeline, screen_name, trim_user=True, include_rts=False).items()
            for tweet in user_tweets:
                csvwriter.writerow([user.id_str, screen_name, tweet.text])

if __name__ == "__main__":
    act = None
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'search':
            act = crawl_bilingual_users
        elif cmd == 'validate':
            act = validate_bilingual_users
        elif cmd == 'crawl':
            act = crawl_user_timelines

    if act:
        act()
    else:
        print('Unknown command')
