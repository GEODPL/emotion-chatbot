import streamlit as st
from PIL import Image
import os
from data_logger import log_user_data   # από το ίδιο folder (app/)

st.set_page_config(page_title="Freud Chat", page_icon="🧠", layout="centered")

# ------------------ SESSION STATE ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ AVATARS ------------------
def load_avatar(name):
    path = os.path.join("app", "static", "avatars", f"{name}.png")
    return Image.open(path)

# (Δεν τα χρησιμοποιούμε άμεσα στο HTML, αλλά φορτώνονται αν τα χρειαστείς)
avatar_user = load_avatar("user")
avatar_bot = load_avatar("bot")

# ------------------ CSS & TITLE ------------------
st.markdown("""
    <style>
        body {
            background-color: #fff7f0;
        }
        .message-container {
            display: flex;
            margin-bottom: 1rem;
        }
        .avatar {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            margin-right: 1rem;
        }
        .bubble {
            background-color: #fffdfd;
            padding: 1rem;
            border-radius: 1rem;
            max-width: 70%;
            font-size: 1.1rem;
            color: #333;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .user .bubble {
            background-color: #ffe0b2;
        }
        .bot .bubble {
            background-color: #ffccbc;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🧡 Freud Chat</h1>", unsafe_allow_html=True)

# ------------------ PERSONALIZED RESPONSE LOGIC ------------------
def personal_reply(mood, sleep, water):
    reply = ""

    # Διάθεση
    if mood < 30:
        reply += "Δύσκολη μέρα η σημερινή... Σε καταλαβαίνω. "
    elif mood < 70:
        reply += "Φαίνεται πως ήταν μια μέρα με σκαμπανεβάσματα. Είσαι καλά;. "
    else:
        reply += "Βλέπω ότι είσαι καλά σήμερα. Πολύ καλά νέα αυτά."

    # Ύπνος
    if sleep == "0–2":
        reply += "Ξέρεις... Το να κοιμάσαι λίγο, μπορεί να σε επηρεάσει σοβαρά μέσα στην ημέρα. "
    elif sleep == "3–5":
        reply += "Κάποιος δεν ξεκουράστηκε χθές αρκετά. Γιατί; Σου συμβαίνει κάτι;. "
    elif sleep == "6–8":
        reply += "Μπράβο για την ποιότητα ύπνου που προσπαθείς να φτιάξεις. "
    else:
        reply += "Τα έχεις πάει εξαιρετικά με τον ύπνο σου. Οι προσπάθειες μας απέφεραν καρπούς και χαίρομαι πολύ για εσένα, διότι τώρα θα ηρεμήσεις. "

    # Νερό
    if water == "0":
        reply += "Η έλλειψη νερού βλέπω ότι σε κάνει να νιώθεις κουρασμένος/η. "
    elif water == "1–3":
        reply += "Λίγο νερό είναι καλύτερο από καθόλου! Χωρίς να σημαίνει ότι δεν προσπαθούμε για το παραπάνω. "
    elif water == "4–6":
        reply += "Μια καλή ενυδάτωση βοηθάει πολύ και εσύ είσαι σε καλό δρόμο. "
    else:
        reply += "Μπράβο για την καλή ενυδάτωση. Αυτό που θέλαμε, το καταφέραμε."

    return reply

# ------------------ ΦΟΡΜΑ (st.form) ------------------
with st.form("mood_form"):
    # EMOJI MOOD
    st.markdown("### 😊 Πώς είσαι σήμερα. Θες να μου μιλήσεις;")

    mood_emojis = {
        "😔": 10,
        "😕": 30,
        "😐": 50,
        "🙂": 70,
        "😄": 90
    }

    selected_mood = st.radio(
        "Επέλεξε διάθεση",
        options=list(mood_emojis.keys()),
        index=2,
        horizontal=True,
        label_visibility="collapsed"
    )

    mood = mood_emojis[selected_mood]

    # SLEEP
    st.markdown("### 😴 Πόσες ώρες κοιμήθηκες χθες;")
    sleep = st.radio(
        "Ύπνος",
        ["0–2", "3–5", "6–8", "9+"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # WATER
    st.markdown("### 💧 Πόσα ποτήρια νερό ήπιες σήμερα;")
    water = st.radio(
        "Νερό",
        ["0", "1–3", "4–6", "7+"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # USER TEXT INPUT
    st.markdown("### 📝 Πες μου ό,τι θέλεις. Είμαι εδώ για να σε ακούσω με προσοχή:")
    user_input = st.text_area(
        "Γράψε ελεύθερα...",
        label_visibility="collapsed",
        height=100
    )

    # Κουμπί υποβολής φόρμας
    submitted = st.form_submit_button("Αποστολή")

# ------------------ ΕΠΕΞΕΡΓΑΣΙΑ ΜΕΤΑ ΤΟ SUBMIT ------------------
if submitted and user_input.strip():
    # Μήνυμα χρήστη
    st.session_state.messages.append(("user", user_input.strip()))

    # Περίληψη βάσει επιλογών
    summary = personal_reply(mood, sleep, water)
    st.session_state.messages.append(("bot", summary))

    # Ψυχοθεραπευτική απάντηση bot
    response = "Σε ακούω με προσοχή. Θες να μου πεις περισσότερα;"
    st.session_state.messages.append(("bot", response))

    # Αποθήκευση δεδομένων σε CSV
    log_user_data(mood, sleep, water, user_input.strip())

# ------------------ CHAT DISPLAY ------------------
for sender, msg in st.session_state.messages:
    if sender == "user":
        st.markdown(f"""
            <div class="message-container user">
                <img src="app/static/avatars/user.png" class="avatar">
                <div class="bubble">{msg}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="message-container bot">
                <img src="app/static/avatars/bot.png" class="avatar">
                <div class="bubble">{msg}</div>
            </div>
        """, unsafe_allow_html=True)

