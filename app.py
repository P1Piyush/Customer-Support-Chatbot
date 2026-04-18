import os
import pickle

import streamlit as st

from chatbot import models_exist, predict_response, train_models

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Customer Support ChatBot",
    page_icon="💬",
    layout="centered",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* General body */
    body { font-family: 'Segoe UI', sans-serif; }

    /* Header */
    .main-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: #1a73e8;
        margin-bottom: 0;
    }
    .sub-title {
        text-align: center;
        font-size: 0.95rem;
        color: #888;
        margin-top: 2px;
        margin-bottom: 20px;
    }

    /* Chat bubbles */
    .chat-wrapper {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 10px 0;
    }
    .user-row {
        display: flex;
        justify-content: flex-end;
    }
    .bot-row {
        display: flex;
        justify-content: flex-start;
        flex-direction: column;
        align-items: flex-start;
    }
    .user-bubble {
        background: #1a73e8;
        color: white;
        padding: 10px 16px;
        border-radius: 18px 18px 4px 18px;
        max-width: 72%;
        font-size: 0.95rem;
        line-height: 1.5;
        word-wrap: break-word;
    }
    .bot-bubble {
        background: #f1f3f4;
        color: #202124;
        padding: 10px 16px;
        border-radius: 18px 18px 18px 4px;
        max-width: 72%;
        font-size: 0.95rem;
        line-height: 1.5;
        word-wrap: break-word;
    }
    .intent-tag {
        font-size: 0.72rem;
        color: #aaa;
        margin-top: 4px;
        margin-left: 4px;
    }

    /* Footer */
    .footer {
        text-align: center;
        font-size: 0.78rem;
        color: #aaa;
        margin-top: 30px;
        padding-top: 12px;
        border-top: 1px solid #e0e0e0;
    }

    /* Hide default streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Auto-train if models missing ──────────────────────────────────────────────
if not models_exist():
    with st.spinner("First run: training models... (takes ~10 seconds)"):
        train_models()

# ── Load accuracy from models dir (after training) ───────────────────────────
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
ACC_PATH = os.path.join(MODELS_DIR, "accuracy.pkl")

# Compute and cache accuracy on first load
if not os.path.exists(ACC_PATH):
    nb_acc, svm_acc = train_models()
    with open(ACC_PATH, "wb") as f:
        pickle.dump({"nb": nb_acc, "svm": svm_acc}, f)
else:
    with open(ACC_PATH, "rb") as f:
        acc = pickle.load(f)
    nb_acc, svm_acc = acc["nb"], acc["svm"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    model_choice = st.selectbox(
        "Select Model",
        options=["SVM (LinearSVC)", "Naive Bayes"],
        index=0,
        help="SVM generally performs better for intent classification.",
    )
    model_key = "svm" if model_choice.startswith("SVM") else "nb"

    st.markdown("---")
    st.markdown("### 📊 Model Accuracy")
    st.metric("Naive Bayes", f"{nb_acc * 100:.1f}%")
    st.metric("SVM (LinearSVC)", f"{svm_acc * 100:.1f}%")

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown(
        """
        This chatbot handles:
        - Greetings & Goodbyes
        - Order Tracking
        - Refunds & Returns
        - Product Info
        - Complaints
        - Human Agent Requests
        """
    )
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Welcome message
    st.session_state.messages.append(
        {
            "role": "bot",
            "text": "Hello! I'm your Customer Support Assistant. How can I help you today?",
            "intent": "greeting",
        }
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">💬 Customer Support ChatBot</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Powered by NLP & Machine Learning</div>',
    unsafe_allow_html=True,
)

# ── Chat history ──────────────────────────────────────────────────────────────
chat_html = '<div class="chat-wrapper">'
for msg in st.session_state.messages:
    if msg["role"] == "user":
        chat_html += f"""
        <div class="user-row">
            <div class="user-bubble">{msg["text"]}</div>
        </div>"""
    else:
        tag_display = msg.get("intent", "")
        chat_html += f"""
        <div class="bot-row">
            <div class="bot-bubble">{msg["text"]}</div>
            <div class="intent-tag">🏷️ Intent: {tag_display}</div>
        </div>"""
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# ── Input area ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        label="message",
        placeholder="Type your message here...",
        label_visibility="collapsed",
        key="user_input",
    )
with col2:
    send_clicked = st.button("Send", use_container_width=True, type="primary")

# ── Handle send ───────────────────────────────────────────────────────────────
if send_clicked and user_input.strip():
    user_text = user_input.strip()
    st.session_state.messages.append({"role": "user", "text": user_text})

    response, intent = predict_response(user_text, model_type=model_key)
    st.session_state.messages.append(
        {"role": "bot", "text": response, "intent": intent}
    )
    st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">Built with NLTK + Scikit-learn &nbsp;|&nbsp; Sharda University Final Year Project</div>',
    unsafe_allow_html=True,
)
