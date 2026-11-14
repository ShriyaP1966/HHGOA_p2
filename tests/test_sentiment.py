import pytest

from app.sentiment import analyze_sentiment


@pytest.mark.parametrize(
    "text, label",
    [
        ("This is an excellent result", "positive"),
        ("I am so happy with this, great work!", "positive"),
        ("This is terrible and I am sad", "negative"),
        ("The service was bad.", "negative"),
        ("The meeting is at three o'clock", "neutral"),
    ],
)
def test_labels(text, label):
    assert analyze_sentiment(text)[0] == label


def test_negation_flips_polarity():
    # The old word-list classifier scored "not good" as positive.
    assert analyze_sentiment("This is not good")[0] == "negative"


def test_punctuation_does_not_hide_words():
    # The old classifier missed "good." because of the trailing period.
    assert analyze_sentiment("good.")[0] == "positive"


def test_score_is_bounded():
    _, score = analyze_sentiment("great great great excellent wonderful!!!")
    assert -1 <= score <= 1
