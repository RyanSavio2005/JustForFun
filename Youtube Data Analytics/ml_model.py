from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

TRAIN_TEXTS = [
    "funny cats animals pets comedy",
    "football match highlights goals sports",
    "python tutorial programming code development",
    "cooking recipe kitchen food meal",
    "travel vlog holiday tourism adventure",
    "makeup tutorial beauty fashion",
    "movie trailer official trailer entertainment"
]
TRAIN_LABELS = ["Entertainment", "Sports", "Education", "Food", "Travel", "Lifestyle", "Entertainment"]

_model = None
_vectorizer = None

def get_trained_model_and_vectorizer():
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        _vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=5000)
        X = _vectorizer.fit_transform(TRAIN_TEXTS)
        _model = MultinomialNB()
        _model.fit(X, TRAIN_LABELS)
    return _model, _vectorizer

def predict_category_from_text(text, model, vectorizer):
    if not text:
        return "Unknown"
    X = vectorizer.transform([text])
    return model.predict(X)[0]