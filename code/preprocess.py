import pandas as pd
from opencc import OpenCC
import preprocessor as p
import regex

CHN_REGEX = r'[^\p{BasicLatin}]+[[:punct:]]?'
cc = OpenCC('s2t')

def clean_text(raw_text):
    detweeted_text = p.clean(raw_text)
    simplied_text = cc.convert(detweeted_text)
    return simplied_text

def seperate_langs(original_text):
    chn_text = ''.join(regex.findall(CHN_REGEX, original_text))
    eng_text = regex.sub(CHN_REGEX, '', original_text)

    return [chn_text, eng_text]

df = pd.read_csv('../data/tweets_original.csv')

df['clean_text'] = df['raw_text'].apply(clean_text)
df = df.drop(df[df['clean_text'].str.len() <= 0].index)

df['monolingual_text'] = df['clean_text'].apply(seperate_langs)
df = df.explode('monolingual_text')
df = df.reset_index(drop=True)
df = df.drop(df[df['monolingual_text'].str.len() < 5].index)

low_freq_users = df['screen_name'].value_counts()
to_remove = low_freq_users[low_freq_users < 30].index
df = df.drop(to_remove)

df = df.reset_index(drop=True)

df.to_csv('../data/tweets.csv')
