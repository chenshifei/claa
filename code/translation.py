import os, requests, uuid, json, csv
import pandas as pd

def _get_azure_translations(text, src, dest):
    key_var_name = 'TRANSLATOR_TEXT_SUBSCRIPTION_KEY'
    if not key_var_name in os.environ:
        raise Exception('Please set/export the environment variable: {}'.format(key_var_name))
    subscription_key = os.environ[key_var_name]

    endpoint_var_name = 'TRANSLATOR_TEXT_ENDPOINT'
    if not endpoint_var_name in os.environ:
        raise Exception('Please set/export the environment variable: {}'.format(endpoint_var_name))
    endpoint = os.environ[endpoint_var_name]

    # If you encounter any issues with the base_url or path, make sure
    # that you are using the latest endpoint: https://docs.microsoft.com/azure/cognitive-services/translator/reference/v3-0-translate
    path = '/translate?api-version=3.0'
    params = '&from={}&to={}'.format(src, dest)
    constructed_url = endpoint + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text' : text
    }]
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()

    return response[0]['translations'][0]['text']

def translate(text, src='zh-tw', dest='en'):
    print('Translating dest=', dest, 'text=', text)
    return _get_azure_translations(text, src=src, dest=dest)

df = pd.read_csv('../data/tweets.csv')

# chn_texts = df['chn_text'].dropna().drop_duplicates()
# df['translated_eng'] = chn_texts.apply(translate)
# print('-----------')
# print('Translate ENG successful!, shape={}'.format(df.shape))
# df.to_csv('../data/tweets_translated_eng.csv', quoting=csv.QUOTE_NONNUMERIC)

eng_texts = df['eng_text'].dropna().drop_duplicates(keep='last')
df['translated_chn'] = eng_texts.apply(translate, src='en', dest='zh-tw')
print('-----------')
print('Translate CHN successful!, shape={}'.format(df.shape))

df.to_csv('../data/tweets_translated_chn.csv', quoting=csv.QUOTE_NONNUMERIC)
