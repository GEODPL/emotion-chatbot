#  Research Log - Διπλωματική Εργασία

**Τίτλος:** Ανάλυση Συναισθήματος και Συνομιλιακά Συστήματα στην Υποστήριξη Ψυχικής Υγείας  
**Ημερομηνία Έναρξης:** 2025-10-24  
**Φοιτητής:** Γεωργία Μαρίαgit add research_log.md
git commit -m "Προσθήκη τεχνικού ημερολογίου"

---

##  2025-10-24

🔹 Ξεκίνησα τη διπλωματική με στόχο τη δημιουργία ενός συναισθηματικά ευφυούς chatbot.

✅ Ολοκληρώθηκαν:
- Δημιουργία φακέλου project (`emotion-chatbot`)
- Δημιουργία Git repository & `.gitignore`
- Εγκατάσταση Python virtual environment (`venv`)
- Εγκατάσταση βιβλιοθηκών: `transformers`, `torch`
- Δημιουργία της πρώτης συνάρτησης `analyze_sentiment(text)`
- Δοκιμή με script `test.py` – ✅ επιτυχής εκτέλεση

 Χρησιμοποιήθηκε το προεκπαιδευμένο μοντέλο:
- `distilbert-base-uncased-finetuned-sst-2-english` από Hugging Face

 Παρατηρήσεις:
- Το μοντέλο δουλεύει καλά στα αγγλικά.
- Επόμενος στόχος: fine-tuning σε ελληνικά δεδομένα (π.χ. Greek Sentiment Dataset)

---

## TODO - Επόμενα βήματα

- [ ] Δημιουργία παρουσίασης σε Jupyter Notebook
- [ ] Σύνδεση project με GitHub
- [ ] Εύρεση ελληνικού dataset (π.χ. Greek Twitter)
- [ ] Fine-tuning BERT μοντέλου στα ελληνικά
- [ ] Ενσωμάτωση με chatbot (Rasa ή custom)