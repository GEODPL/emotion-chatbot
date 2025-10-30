from app.lexicon_sentiment import analyze_lexicon_sentiment

keimeno = "Είμαι πολύ χαρούμενος σήμερα αλλά νιώθω λίγο κουρασμένος."
apotelesma = analyze_lexicon_sentiment(keimeno)

print("Ανάλυση συναισθήματος με λεξικό:")
print(apotelesma)