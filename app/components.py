import streamlit as st


def render_message(sender: str, text: str):
    """
    Εμφανίζει μήνυμα χρήστη ή bot με τα CSS classes:
    .message-container, .avatar, .bubble
    """
    if sender == "user":
        st.markdown(
            f"""
            <div class="message-container user">
                <div class="bubble">{text}</div>
                <div class="avatar">🧑</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="message-container bot">
                <div class="avatar">🧠</div>
                <div class="bubble">{text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_exercise_card(text: str):
    """
    Κάρτα άσκησης (χρησιμοποιεί τα CSS:
    .message-container, .avatar, .exercise-card, .exercise-title, .exercise-text)
    """
    st.markdown(
        f"""
        <div class="message-container bot">
            <div class="avatar">🧠</div>
            <div class="exercise-card">
                <div class="exercise-title">🧘 Μικρή άσκηση για εσένα</div>
                <div class="exercise-text">{text}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_action_plan_card(text: str):
    """
    Κάρτα «μικρού πλάνου δράσης εβδομάδας».
    Οπτικά μοιάζει με την exercise-card, αλλά με άλλο icon & τίτλο.
    """
    st.markdown(
        f"""
        <div class="message-container bot">
            <div class="avatar">📅</div>
            <div class="exercise-card">
                <div class="exercise-title">📌 Μικρό πλάνο εβδομάδας</div>
                <div class="exercise-text">{text}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_emergency_block(html_block: str):
    """
    Το emergency_message() από το rules.py επιστρέφει έτοιμο HTML.
    Εδώ απλά το βάζουμε μέσα σε ένα container αν θέλουμε (ή το δείχνουμε όπως είναι).
    """
    st.markdown(html_block, unsafe_allow_html=True)
