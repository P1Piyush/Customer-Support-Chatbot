from chatbot import train_models

if __name__ == "__main__":
    print("=" * 45)
    print("  Training Customer Support Chatbot Models")
    print("=" * 45)
    nb_acc, svm_acc = train_models()
    print("=" * 45)
    print("  Training Complete! Models saved to ./models/")
    print("=" * 45)
