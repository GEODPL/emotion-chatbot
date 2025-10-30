from transformers import pipeline

# Δημιουργία sentiment pipeline με DistilBERT
analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Αγγλικό κείμενο για ανάλυση
text = "I'm feeling a bit tired but also really proud of what I achieved today."

# Ανάλυση συναισθήματος
result = analyzer(text)

# Εμφάνιση αποτελέσματος
print("Ανάλυση Συναισθήματος:")
print(result)