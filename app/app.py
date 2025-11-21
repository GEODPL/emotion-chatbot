import streamlit as st
from PIL import Image
import os

st.set_page_config(page_title="Freud Chat", page_icon="🧠", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

def load_avatar(name):
    path = os.path.join("app", "static", "avatars", f"{name}.png")
    return Image.open(path)

avatar_user = load_avatar("user")
avatar_bot = load_avatar("bot")

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

# ------------------ EMOJI MOOD ------------------
st.markdown("### 😊 Πώς νιώθεις σήμερα;")

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

# ------------------ SLEEP ------------------
st.markdown("### 😴 Πόσες ώρες κοιμήθηκες χθες;")
sleep = st.radio("Ύπνος", ["0–2", "3–5", "6–8", "9+"], horizontal=True, label_visibility="collapsed")

# ------------------ WATER ------------------
st.markdown("### 💧 Πόσα ποτήρια νερό ήπιες σήμερα;")
water = st.radio("Νερό", ["0", "1–3", "4–6", "7+"], horizontal=True, label_visibility="collapsed")

# ------------------ PERSONALIZED RESPONSE ------------------
def personal_reply(mood, sleep, water):
    reply = ""

    if mood < 30:
        reply += "Μοιάζει να ήταν δύσκολη μέρα. "
    elif mood < 70:
        reply += "Φαίνεται πως ήταν μια μέρα με σκαμπανεβάσματα. "
    else:
        reply += "Χαίρομαι που νιώθεις καλά σήμερα. "

    if sleep == "0–2":
        reply += "Ο ελάχιστος ύπνος μπορεί να επηρεάσει τη διάθεσή σου. "
    elif sleep == "3–5":
        reply += "Ίσως να μην ξεκουράστηκες αρκετά χθες. "
    elif sleep == "6–8":
        reply += "Ο ύπνος σου φαίνεται ισορροπημένος. "
    else:
        reply += "Φαίνεται πως πήρες τον ύπνο που χρειαζόσουν. "

    if water == "0":
        reply += "Η έλλειψη νερού ίσως σε κάνει να νιώθεις κουρασμένος/η. "
    elif water == "1–3":
        reply += "Λίγο νερό είναι καλύτερο από καθόλου! "
    elif water == "4–6":
        reply += "Μια καλή ενυδάτωση βοηθάει πολύ. "
    else:
        reply += "Μπράβο για την καλή ενυδάτωση! "

    return reply

# ------------------ ΑΠΑΝΤΗΣΗ BOT ------------------
summary = personal_reply(mood, sleep, water)
st.session_state.messages.append(("bot", summary))

# ------------------ TEXT INPUT ------------------
st.markdown("### 📝 Πες μου ό,τι θέλεις:")
user_input = st.text_area("Γράψε ελεύθερα...", label_visibility="collapsed", height=100)

if st.button("Αποστολή") and user_input.strip():
    st.session_state.messages.append(("user", user_input.strip()))
    response = "Σε ακούω με προσοχή. Θες να μου πεις περισσότερα;"
    st.session_state.messages.append(("bot", response))

# ------------------ CHAT DISPLAY ------------------
for sender, msg in st.session_state.messages:
    with st.container():
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



