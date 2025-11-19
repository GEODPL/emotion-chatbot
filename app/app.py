import streamlit as st

st.set_page_config(page_title="Emotion Chat", page_icon="💬", layout="centered")

# Αρχικοποίηση ιστορικού
if "messages" not in st.session_state:
    st.session_state.messages = []

# Εμφάνιση ιστορικού
st.write("## 💬 Mental Health Chat")
for sender, text in st.session_state.messages:
    if sender == "Εσύ":
        st.markdown(f"<div style='background-color:#dbeafe;padding:10px;border-radius:10px;margin:5px 0;text-align:right'>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background-color:#e0f2f1;padding:10px;border-radius:10px;margin:5px 0'>{text}</div>", unsafe_allow_html=True)

# Input
user_input = st.text_area("✍️ Πες μου ό,τι θέλεις:", placeholder="Γράψε ελεύθερα...")

if st.button("Αποστολή") and user_input.strip():
    st.session_state.messages.append(("Εσύ", user_input.strip()))
    st.session_state.messages.append(("Bot", "Σε ευχαριστώ που το μοιράστηκες. Είμαι εδώ να σε ακούσω."))
    st.rerun()



