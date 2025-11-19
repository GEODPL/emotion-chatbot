from transformers import pipeline

# Φόρτωση μοντέλου
analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

print("👋 Γεια σου! Πες μου πώς αισθάνεσαι σήμερα. (Γράψε 'exit' για έξοδο)\n")

while True:
    user_input = input("🧠 Εσύ: ")

    if user_input.lower() == 'exit':
        print("👋 Καλή συνέχεια! 😊")
        break

    result = analyzer(user_input)[0]
    label = result['label']
    score = result['score']

    print(f"\n📊 Ανάλυση: {label} ({score:.2f})")

    if label == 'POSITIVE':
        print("🤖 Chatbot: Χαίρομαι που νιώθεις καλά! 😄\n")
    elif label == 'NEGATIVE':
        print("🤖 Chatbot: Λυπάμαι που νιώθεις έτσι. Είμαι εδώ για σένα. 😔\n")
    else:
        print("🤖 Chatbot: Ευχαριστώ που το μοιράστηκες μαζί μου.\n")