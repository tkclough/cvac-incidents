"""
Definitions for model that classifies dispatch messages into 24 categories.
"""
from functools import partial
import re
from autocorrect import spell, word
from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from xgboost import XGBClassifier
import nltk

def preprocess(msg, sub_dict, correct=True):
    """
    Preprocess dispatch message in the following order:
     1. Convert to lower case.
     2. Replace abbreviations in sub_dict.
     3. Select only the following sections of the message: comments, type, problem,
        and responder script.
     4. Remove non-alphabetic characters.
     5. Correct spelling of words.
    """
    msg = msg.lower()
    for k, v in sub_dict.items():
        msg = re.sub(r'(?:[^\w]|^){}(?:[^\w]|$)'.format(k), ' {} '.format(v), msg)
    msg = ' '.join(re.findall(r'(?:comments?):(?P<info>.*?)(?:(?:,[\w\s]*:))', msg) + \
                   re.findall(r'(?:type?):(?P<info>.*?)(?:(?:,[\w\s]*:))', msg) + \
                   re.findall(r'(?:problem?):(?P<info>.*?)(?:(?:,[\w\s]*:))', msg) + \
                   re.findall(r'(?:responder script?):(?P<info>.*?)(?:(?:,[\w\s]*:))', msg))
    msg = re.sub(r'[^a-z]', ' ', msg)
    msg = msg.split()
    if correct:
        return ' '.join([(w if w in word.KNOWN_WORDS else spell(w)) for w in msg])
    return ' '.join(msg)

class DispatchPreprocessor(BaseEstimator, TransformerMixin):
    """
    Mixin for transforming dispatch messages by preprocessing.
    """
    def __init__(self, sub_dict):
        self.sub_dict = sub_dict

    def fit(self, X, y=None):
        """
        Obligatory fit method.
        """
        return self

    def transform(self, X):
        """
        Apply preprocess function to input.
        """
        return X.apply(partial(preprocess, sub_dict=self.sub_dict))

class TextSelector(BaseEstimator, TransformerMixin):
    """
    Select a specific field in a dataframe.
    """
    def __init__(self, field):
        self.field = field
    def fit(self, X, y=None):
        """
        Obligatory fit method.
        """
        return self
    def transform(self, X):
        """
        Select the pre-specified field from the input.
        """
        return X[self.field]

def tokenizer(str_input):
    """
    Tokenizer for string input.
    """
    words = re.sub(r"[^A-Za-z0-9\-]", " ", str_input).lower().split()
    porter_stemmer = nltk.PorterStemmer()
    words = [porter_stemmer.stem(word) for word in words]
    return words

SUB_DICT = {
    'edp': 'emotionally disturbed person',
    'unk': 'unknown',
    'als': 'advanced life support',
    'bls': 'basic life support',
    'ams': 'altered mental state',
    'intox': 'intoxicated',
    'cath': 'catheter',
    'poss': 'possible'
}
class IncidentClassifier(BaseEstimator, TransformerMixin):
    """
    Definition for incident classifier. It consists of a pipeline: select
    message column, preprocess, vectorize tfidf, svd, XGBClassifier.
    """

    def __init__(self, stop_words=nltk.corpus.stopwords.words()):
        self.clf_ = Pipeline([
            ('colext', TextSelector('Message')),
            ('preprocessor', DispatchPreprocessor(SUB_DICT)),
            ('tfidf', TfidfVectorizer(tokenizer=tokenizer, stop_words=stop_words,
                                      min_df=.0025, max_df=0.25, ngram_range=(1, 3))),
            ('svd', TruncatedSVD(algorithm='randomized', n_components=300)),
            ('clf', XGBClassifier(max_depth=3, n_estimators=300, learning_rate=0.1))
        ])

    def fit(self, X, y=None):
        """
        Fit underlying pipeline.
        """
        self.clf_.fit(X, y)
        return self

    def predict(self, X):
        """
        Predict using underlying pipeline.
        """
        return self.clf_.predict(X)

    def predict_proba(self, X):
        """
        Use predict_proba with underlying pipeline.
        """
        return self.clf_.predict_proba(X)
