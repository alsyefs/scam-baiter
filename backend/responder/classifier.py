from flair.data import Sentence
from flair.models import TextClassifier

from globals import CLASSIFIER_PATH


def classify(content) -> str:
    classifier = TextClassifier.load(CLASSIFIER_PATH) # <- './models/classifier/final-model.pt' not found
    # an empty file is created at './models/classifier/final-model.pt' when the classifier is loaded to avoid the error
    sentence = Sentence(content)
    classifier.predict(sentence)
    label = sentence.get_label("topic")
    print(f"Classifier result: {label.value} ({label.score})")
    return label.value.upper()