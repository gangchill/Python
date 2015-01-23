from sklearn.feature_extraction.text import CountVectorizer

def load_newsgroups(from_file='/home/ortmann/bds/a07/data'):
    with open(from_file) as f:
        text=f.read()
    articles=dict()
    for a in text.split('\n'):
        p=a.find('\t')
        articles[a[0:p]]=a[(p+1):]
    if '' in articles:
        del articles['']
    return articles
#cv=CountVectorizer(stop_words='english')
#tokenizer=cv.build_tokenizer()
load_newsgroups()
