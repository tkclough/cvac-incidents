from sklearn.base import TransformerMixin
class RegexPreprocessor(TransformerMixin):
    """Do textual preprocessing with regex substitution."""
    def __init__(self, pat, sub=' ', to_lower=True):
        self.pat = pat
        self.sub = sub
        self.to_lower = to_lower
    
    def fit(self, X, y=None):
        """Does nothing."""
        return self
    
    def transform(self, X):
        """Transform X by textual substitution"""
        if self.to_lower:
            X = X.str.lower()
        return X.str.replace(self.pat, self.sub)