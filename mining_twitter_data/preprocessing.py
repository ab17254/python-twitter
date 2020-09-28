import itertools
import math
import operator
import sys
import json
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import bigrams
import string
from collections import defaultdict
import vincent
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

punctuation = list(string.punctuation)
stop = stopwords.words('english') + punctuation + ['rt', 'via']

emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""

regex_str = [
    emoticons_str,
    r'<[^>]+>',  # HTML tags
    r'(?:@[\w_]+)',  # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs

    r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
    r'(?:[\w_]+)',  # other words
    r'(?:\S)'  # anything else
]

tokens_re = re.compile(r'(' + '|'.join(regex_str) + ')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^' + emoticons_str + '$', re.VERBOSE | re.IGNORECASE)
"""
def tokenize(s):
    return tokens_re.findall(s)


def preprocess(s, lowercase=False):
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens
"""
positive_vocab = [
    'good', 'nice', 'great', 'awesome', 'outstanding',
    'fantastic', 'terrific', ':)', ':-)', 'like', 'love',
]
negative_vocab = [
    'bad', 'terrible', 'crap', 'useless', 'hate', ':(', ':-(',
]


def hashtag_extract(s):
    hashtags = []
    for i in s:
        ht = re.findall(r"#(\w+)", i)
        hashtags.append(ht)
    return hashtags


def remove_url(s):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    no_url = url_pattern.sub(r'', s)
    return no_url


def remove_emoji(s):
    emoji_pattern = re.compile(
        r'(\u00a9|\u00ae|[\u2000-\u3300]|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff]|(?:\U0001f92d))',
        re.UNICODE)
    return emoji_pattern.sub(r'', s)


def join_punct(s):
    return ''.join(ch for ch in s if ch not in punctuation)


def nltk_tokenize(s):
    return word_tokenize(join_punct(remove_emoji(remove_url(s))))


def tokens_nopunc(s):
    tokens = nltk_tokenize(s)
    tokens_nopunct = [word.lower() for word in tokens if re.search("\w", word)]
    return tokens_nopunct


def tokens_nostopwords(s):
    tokens = tokens_nopunc(s)
    nostopwords = [word for word in tokens if not word in stop]
    return nostopwords


def new_fname(s):
    s = s[:-5]
    return s + "_tokens.txt"


def vincent_fname(s):
    s = s[5:]
    s = s[:-5]
    return s + "_term_freq.json"


def common_word_plot(token_list):
    tweets = pd.DataFrame(token_list.most_common(50),
                          columns=['words', 'count'])
    fix, ax = plt.subplots(figsize=(8, 8))
    tweets.sort_values(by='count').plot.barh(x='words',
                                             y='count',
                                             ax=ax,
                                             color="purple")
    ax.set_title("Common Words Found in Tweets")
    plt.show()


def bigram_network(s):
    terms_bigrams = [list(bigrams(tweet)) for tweet in s]

    bigram = list(itertools.chain(*terms_bigrams))
    bigram_counts = Counter(bigram)

    bigram_df = pd.DataFrame(bigram_counts.most_common(20),
                             columns=['bigram', 'count'])
    print(bigram_df)

    d = bigram_df.set_index('bigram').T.to_dict('records')

    g = nx.Graph()
    for k, v in d[0].items():
        g.add_edge(k[0], k[1], weight=(v * 10))

    fig, ax = plt.subplots(figsize=(20, 16))
    pos = nx.spring_layout(g, k=2)
    nx.draw_networkx(g, pos,
                     font_size=16,
                     width=3,
                     edge_color='grey',
                     node_color='purple',
                     ax=ax)
    for key, value in pos.items():
        x, y = value[0] + .135, value[1] + .045
        ax.text(x, y,
                s=key,
                bbox=dict(facecolor='red', alpha=0.25),
                horizontalalignment='center', fontsize=13)
    plt.show()


def f_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
        return i + 1


def word_freq(c):
    word_freq = c.most_common(20)
    labels, freq = zip(*word_freq)
    data = {'data': freq, 'x': labels}
    bar = vincent.Bar(data, iter_idx='x')
    bar.to_json('term_freq.json')


def time_graph(td):
    ones = [1] * len(td)
    idx = pd.DatetimeIndex(td)
    dates_pd = pd.Series(ones, index=idx)
    per_minute = dates_pd.resample('1Min').sum().fillna(0)
    time_chart = vincent.Line(dates_pd)
    time_chart.axis_titles(x='Time', y='Freq')
    time_chart.to_json('time_chart.json')


if __name__ == '__main__':
    fname = sys.argv[1]
    search_word = sys.argv[2]
    count_search = Counter()
    com = defaultdict(lambda: defaultdict(int))
    tweet_dates = []
    bigram_list = []
    line_count = 0
    tweet_dataset = []
    hashtags = []

    with open(fname) as f:
        tweet_list = json.load(f)
        count_all = Counter()
        hash_count = Counter()
        geo_data = {
            "type": "FeatureCollection",
            "features": []
        }
        for line in tweet_list:
            if line['coordinates']:
                geo_json_feature = {
                    "type": "Feature",
                    "geometry": line['coordinates'],
                    "properties": {
                        "text": line['text'],
                        "created_at": line['created_at']
                    }
                }
                geo_data['features'].append(geo_json_feature)
            with open('geo_data.json', 'w') as fout:
                fout.write(json.dumps(geo_data, indent=4))

            if line['lang'] == 'en':
                bigram_list.append(line['text'])
                # print(line['created_at'])
                tweet_dates.append(line['created_at'])
                tweet_dataset.append(line['text'])
                tokens = (tokens_nostopwords(line['text']))
                count_all.update(tokens)
                tokens_list = [term for term in tokens_nostopwords(line['text'])]

                ht = re.findall(r"#(\w+)", line['text'])
                hashtags.append(ht)
                hash_count.update(ht)

                # Co-occurrences
                if search_word in tokens_list:
                    count_search.update(tokens_list)
                for i in range(len(tokens_list) - 1):
                    for j in range(i + 1, len(tokens_list)):
                        w1, w2 = sorted([tokens_list[i], tokens_list[j]])
                        if w1 != w2:
                            com[w1][w2] += 1
                com_max = []
                for t1 in com:
                    t1_max_terms = sorted(com[t1].items(), key=operator.itemgetter(1), reverse=True)[:5]
                    for t2, t2_count in t1_max_terms:
                        com_max.append(((t1, t2), t2_count))
                terms_max = sorted(com_max, key=operator.itemgetter(1), reverse=True)
        if search_word == "*":
            print(terms_max[:5])
        else:
            print("Co-occurance for %s:" % search_word)
            print(count_search.most_common(20))
        # print(count_all.most_common(10))

        # print(count_all)  # PRINT TOKENS

        print(hashtags)
        common_word_plot(hash_count)
        # Word freq graph JSON
        word_freq(count_all)
        # Time graph JSON
        time_graph(tweet_dates)
        # matplotlib common word graph
        # common_word_plot(count_all)
        # networkx bigram
        # bigram_network((count_all.most_common(50)))
