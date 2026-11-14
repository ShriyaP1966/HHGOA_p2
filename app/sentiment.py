"""Sentiment classification using VADER (handles negation, punctuation, intensity)."""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Thresholds recommended by the VADER authors for the compound score.
POSITIVE_THRESHOLD = 0.05
NEGATIVE_THRESHOLD = -0.05

_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> tuple[str, float]:
    """Return (label, compound score in [-1, 1]) for the given text."""
    compound = _analyzer.polarity_scores(text)["compound"]

    if compound >= POSITIVE_THRESHOLD:
        label = "positive"
    elif compound <= NEGATIVE_THRESHOLD:
        label = "negative"
    else:
        label = "neutral"

    return label, compound
