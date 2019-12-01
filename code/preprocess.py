import csv
import demoji
import pandas as pd
from opencc import OpenCC
import preprocessor as p
import regex

CHN_REGEX = r'[^\p{BasicLatin}]+[[:punct:]]?'
MEANINGLESS_REGEX = r'[\W\d\s\_]+$'
cc = OpenCC('s2t')
demoji.download_codes()

def clean_text(raw_text):
    detweeted_text = p.clean(raw_text)
    simplied_text = cc.convert(detweeted_text)
    return simplied_text

def seperate_langs(original_text):
    result = {'chn_text': '', 'eng_text': ''}
    chn_text = ''.join(regex.findall(CHN_REGEX, original_text))
    eng_text = regex.sub(CHN_REGEX, '', original_text)
    chn_text = demoji.replace(chn_text)
    eng_text = demoji.replace(eng_text)

    if is_valid_monolingual_str(chn_text, 'chn'):
        result['chn_text'] = chn_text
    if is_valid_monolingual_str(eng_text, 'eng'):
        result['eng_text'] = eng_text

    return result

def is_valid_monolingual_str(text, lang):
    if regex.match(MEANINGLESS_REGEX, text):
        return False
    elif lang == 'chn' and len(text) < 5:
        return False
    elif lang == 'eng' and len(text.split()) < 3:
        return False
    else:
        return True

df = pd.read_csv('../data/tweets_original.csv')

print('Read successful!, shape={}'.format(df.shape))

df['clean_text'] = df['raw_text'].apply(clean_text)
df = df.drop(df[df['clean_text'].str.len() <= 0].index)

monolingual_texts = df['clean_text'].apply(seperate_langs)
df = pd.concat([df, monolingual_texts.apply(pd.Series)], axis=1)
df = df.reset_index(drop=True)
df = df.drop(df[(df['chn_text'].str.len() <= 0) & (df['eng_text'].str.len() <= 0)].index)
df = df.drop('clean_text', axis=1)
df = df.reset_index(drop=True)

low_freq_users = df['screen_name'].value_counts()
to_remove = low_freq_users[low_freq_users < 30].index
df = df.drop(to_remove)
df = df.reset_index(drop=True)

print('Clean successful!, shape={}'.format(df.shape))

df.to_csv('../data/tweets.csv', quoting=csv.QUOTE_NONNUMERIC)
