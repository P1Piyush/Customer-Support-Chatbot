# Customer Support ChatBot

A customer support chatbot built with NLTK, Scikit-learn, and Streamlit.
Trains two ML classifiers (Naive Bayes & SVM) on intent patterns and serves a clean chat UI.

## Project Structure

```
chatbot_project/
├── data/
│   └── intents.json        # Training intents & responses
├── models/                 # Auto-created after training
│   ├── nb_model.pkl
│   ├── svm_model.pkl
│   ├── label_encoder.pkl
│   ├── intents_store.pkl
│   └── accuracy.pkl
├── chatbot.py              # Core ML logic
├── train.py                # Standalone training script
├── app.py                  # Streamlit web app
├── requirements.txt
└── README.md
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the models

```bash
python train.py
```

### 3. Launch the app

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501** in your browser.

## Supported Intents

| Intent | Example Queries |
|---|---|
| greeting | "hi", "hello", "good morning" |
| goodbye | "bye", "see you later", "farewell" |
| thanks | "thank you", "appreciate it" |
| order_status | "where is my order", "track my order" |
| refund | "i want a refund", "return policy" |
| product_info | "what do you sell", "product details" |
| complaint | "i have a complaint", "bad experience" |
| human_agent | "talk to human", "connect me to agent" |

## Features

- **Two ML models**: Naive Bayes and LinearSVC with TF-IDF features
- **Preprocessing**: Tokenization, stopword removal, lemmatization via NLTK
- **Model selection**: Switch between models in the sidebar
- **Accuracy display**: See test-set accuracy for both models
- **Chat history**: Persistent within session with styled bubbles
- **Intent detection**: Shows detected intent below each bot reply
- **Auto-train**: App trains models automatically on first launch

## Tech Stack

- Python 3.8+
- NLTK (NLP preprocessing)
- Scikit-learn (TF-IDF + classifiers)
- Streamlit (web UI)
- Pickle (model persistence)
