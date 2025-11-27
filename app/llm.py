import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["general"]["openai_api_key"])


def llm_therapeutic_reply(mood: int, sleep: str, water: str, user_text: str, profile: dict | None):
    """
    Γεννάει ένα πιο ελεύθερο, ανθρώπινο κείμενο απάντησης.
    Αν κάτι πάει στραβά (API, όριο, κ.λπ.), επιστρέφει None.
    """
    try:
        profile_snippet = ""
        if profile:
            profile_snippet = (
                f"\n\n[Πληροφορίες προφίλ]\n"
                f"Ρόλος: {profile.get('role','-')}\n"
                f"Βασικό θέμα: {profile.get('main_issue','-')}\n"
                f"Εστίαση: {profile.get('focus','-')}\n"
            )

        user_prompt = (
            f"[Στοιχεία ημέρας]\n"
            f"- Διάθεση (0–100): {mood}\n"
            f"- Ύπνος (ώρες κατηγορία): {sleep}\n"
            f"- Νερό (ποτήρια κατηγορία): {water}\n"
            f"- Κείμενο χρήστη: {user_text}\n"
            f"{profile_snippet}\n"
            "Γράψε μία σύντομη, ζεστή, υποστηρικτική απάντηση 4–7 προτάσεων, "
            "σε απλά ελληνικά, χωρίς να δίνεις διαγνώσεις ή ιατρικές οδηγίες. "
            "Χρησιμοποίησε ψυχοεκπαιδευτικό ύφος (CBT/mindfulness), με έμφαση στην αποδοχή, "
            "στην οριοθέτηση και στα μικρά πρακτικά βήματα."
        )

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Είσαι ένας ζεστός, υποστηρικτικός ψηφιακός συνοδοιπόρος "
                        "για φοιτητές/νέους ενήλικες. Δεν κάνεις διαγνώσεις, "
                        "δεν υπόσχεσαι θεραπεία, δεν αντικαθιστάς ψυχολόγο. "
                        "Βοηθάς τον χρήστη να ονομάσει τα συναισθήματά του, "
                        "να τα κανονικοποιήσει και να σκεφτεί πολύ μικρά, ρεαλιστικά βήματα."
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
        )

        return resp.choices[0].message["content"]
    except Exception:
        return None
