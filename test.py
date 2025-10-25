from app.sentiment import analyze_sentiment

# Μερικά παραδείγματα φράσεων
texts = [
    "I am very happy today!",
    "This is the worst day ever.",
    "I'm feeling a bit anxious and confused.",
    "Life is beautiful.",
    "Nothing makes sense anymore..."
]

# Κάνουμε ανάλυση σε κάθε πρόταση
for text in texts:
    result = analyze_sentiment(text)
    print(f"{text} => {result['label']} (confidence: {result['score']})")