import json
import os
import pickle
import random

import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

# Download required NLTK data
def download_nltk_data():
    packages = ["punkt", "stopwords", "wordnet", "averaged_perceptron_tagger", "punkt_tab"]
    for package in packages:
        try:
            nltk.download(package, quiet=True)
        except Exception:
            pass

download_nltk_data()

INTENTS_PATH = os.path.join(os.path.dirname(__file__), "data", "intents.json")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
NB_MODEL_PATH = os.path.join(MODELS_DIR, "nb_model.pkl")
SVM_MODEL_PATH = os.path.join(MODELS_DIR, "svm_model.pkl")
ENCODER_PATH = os.path.join(MODELS_DIR, "label_encoder.pkl")
INTENTS_STORE_PATH = os.path.join(MODELS_DIR, "intents_store.pkl")

lemmatizer = WordNetLemmatizer()


def load_intents():
    with open(INTENTS_PATH, "r") as f:
        return json.load(f)


def preprocess_text(text: str) -> str:
    tokens = nltk.word_tokenize(text.lower())
    stop_words = set(stopwords.words("english"))
    tokens = [
        lemmatizer.lemmatize(t)
        for t in tokens
        if t.isalpha() and t not in stop_words
    ]
    return " ".join(tokens)


def build_dataset(intents_data):
    patterns = []
    labels = []
    for intent in intents_data["intents"]:
        for pattern in intent["patterns"]:
            patterns.append(preprocess_text(pattern))
            labels.append(intent["tag"])
    return patterns, labels


def train_models():
    os.makedirs(MODELS_DIR, exist_ok=True)

    intents_data = load_intents()
    patterns, labels = build_dataset(intents_data)

    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)

    X_train, X_test, y_train, y_test = train_test_split(
        patterns, encoded_labels, test_size=0.2, random_state=42, stratify=encoded_labels
    )

    # Naive Bayes pipeline
    nb_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", MultinomialNB()),
    ])
    nb_pipeline.fit(X_train, y_train)
    nb_preds = nb_pipeline.predict(X_test)
    nb_accuracy = accuracy_score(y_test, nb_preds)

    # SVM pipeline
    svm_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", LinearSVC(max_iter=1000)),
    ])
    svm_pipeline.fit(X_train, y_train)
    svm_preds = svm_pipeline.predict(X_test)
    svm_accuracy = accuracy_score(y_test, svm_preds)

    # Save models and encoder
    with open(NB_MODEL_PATH, "wb") as f:
        pickle.dump(nb_pipeline, f)
    with open(SVM_MODEL_PATH, "wb") as f:
        pickle.dump(svm_pipeline, f)
    with open(ENCODER_PATH, "wb") as f:
        pickle.dump(label_encoder, f)
    with open(INTENTS_STORE_PATH, "wb") as f:
        pickle.dump(intents_data, f)

    print(f"  Naive Bayes Accuracy : {nb_accuracy * 100:.2f}%")
    print(f"  SVM Accuracy         : {svm_accuracy * 100:.2f}%")

    return nb_accuracy, svm_accuracy


def load_model(model_type: str = "svm"):
    path = SVM_MODEL_PATH if model_type == "svm" else NB_MODEL_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Model not found at {path}. Please run train.py first."
        )
    with open(path, "rb") as f:
        model = pickle.load(f)
    with open(ENCODER_PATH, "rb") as f:
        label_encoder = pickle.load(f)
    with open(INTENTS_STORE_PATH, "rb") as f:
        intents_data = pickle.load(f)
    return model, label_encoder, intents_data


def predict_response(text: str, model_type: str = "svm"):
    model, label_encoder, intents_data = load_model(model_type)
    processed = preprocess_text(text)
    encoded_pred = model.predict([processed])[0]
    tag = label_encoder.inverse_transform([encoded_pred])[0]

    for intent in intents_data["intents"]:
        if intent["tag"] == tag:
            response = random.choice(intent["responses"])
            return response, tag

    return "I'm not sure how to help with that. Could you rephrase your question?", "unknown"


def models_exist() -> bool:
    return (
        os.path.exists(NB_MODEL_PATH)
        and os.path.exists(SVM_MODEL_PATH)
        and os.path.exists(ENCODER_PATH)
        and os.path.exists(INTENTS_STORE_PATH)
    )
