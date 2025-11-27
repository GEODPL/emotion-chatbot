import os
import json
import streamlit as st
from PIL import Image
import pandas as pd
from datetime import datetime

from llm import llm_therapeutic_reply
from rules import (
    personal_reply,
    fallback_therapeutic_reply,
    exercise_suggestion,
    is_emergency,
    emergency_message,
)
from emotional_map import render_emotional_map
from components import (
    render_message,
    render_exercise_card,
    render_emergency_block,
    render_action_plan_card,
)
from data_logger import log_user_data

# Paths για αρχεία
BASE_DIR = os.path.dirname(__file__)
SUPPORT_PHRASES_CSV = os.path.join(BASE_DIR, "..", "support_phrases.csv")
EXERCISES_CSV = os.path.join(BASE_DIR, "..", "exercises_log.csv")
USER_HISTORY_JSON = os.path.join(BASE_DIR, "..", "user_history.json")


# ============================================================
#                LOAD CSS
# ============================================================

def load_css():
    css_path = os.path.join(BASE_DIR, "style.css")
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ============================================================
#          ΜΙΚΡΕΣ HELPER ΣΥΝΑΡΤΗΣΕΙΣ ΓΙΑ ACTION PLAN
# ============================================================

def detect_study_anxiety(text: str) -> bool:
    """
    Επιστρέφει True αν στο κείμενο συνυπάρχουν
    (α) άγχος και (β) σπουδές/εξετάσεις.
    """
    t = text.lower()
    anxiety_words = ["άγχ", "αγχος", "στρες", "στρες"]
    study_words = [
        "σπουδ", "σχολή", "σχολη", "πανεπιστ", "πανεπηστ", "εξετάσ", "εξετασ",
        "εργασία", "εργασια", "εργασι", "μάθημα", "μαθημα", "διάβασμα", "διαβασμα"
    ]
    has_anxiety = any(w in t for w in anxiety_words)
    has_study = any(w in t for w in study_words)
    return has_anxiety and has_study


def build_study_action_plan() -> str:
    """
    Μικρό πλάνο 3 βημάτων για άγχος σπουδών, σε απλή markdown μορφή.
    """
    return (
        "Απ’ όσα μου έχεις γράψει, φαίνεται πως το άγχος για τις σπουδές "
        "είναι κάτι που επανέρχεται. Ας δοκιμάσουμε ένα πολύ μικρό, ρεαλιστικό "
        "πλάνο για αυτή την εβδομάδα:\n\n"
        "1. **Μία άσκηση αναπνοής πριν το διάβασμα (4–2–6, για 5 γύρους)**  \n"
        "   Πριν ανοίξεις τα βιβλία, πάρε 1 λεπτό για αναπνοές ώστε να «μαλακώσει» λίγο η ένταση.\n\n"
        "2. **Μία πρόταση journaling το βράδυ**  \n"
        "   Γράψε κάθε βράδυ μία μόνο πρόταση που αρχίζει με: "
        "«Σήμερα στις σπουδές μου με ζόρισε περισσότερο…». Δεν το κρίνεις, απλώς το καταγράφεις.\n\n"
        "3. **Παρατήρηση μιας δύσκολης στιγμής άγχους**  \n"
        "   Διάλεξε μία στιγμή μέσα στην εβδομάδα (π.χ. πριν από διάβασμα ή εξετάσεις) "
        "και παρατήρησε: *τι σκέψεις πέρασαν από το μυαλό σου;* "
        "Απλώς σημείωσε 2–3 λέξεις, χωρίς να χρειάζεται να τα αναλύσεις εκείνη τη στιγμή.\n\n"
        "Στόχος δεν είναι να «λύσουμε» όλο το άγχος σε μία εβδομάδα, αλλά να αρχίσεις "
        "να το παρατηρείς με λίγο περισσότερη απόσταση και φροντίδα."
    )


def detect_sleep_difficulty(sleep: str, text: str) -> bool:
    """
    Επιστρέφει True αν:
    - ο χρήστης δηλώνει πολύ λίγο ύπνο (0–2 ή 3–5)
    ΚΑΙ/Ή
    - στο κείμενο αναφέρονται ξεκάθαρα δυσκολίες με τον ύπνο.
    """
    t = text.lower()
    bad_sleep_categories = ["0–2", "3–5"]
    sleep_words = [
        "ύπν", "υπν", "ξενύχτ", "ξενυχτ", "αϋπν", "αυπν",
        "δεν κοιμήθηκα", "δεν κοιμηθηκα",
        "δυσκολεύομαι να κοιμηθώ", "δυσκολευομαι να κοιμηθω",
    ]
    bad_category = sleep in bad_sleep_categories
    mentions_sleep = any(w in t for w in sleep_words)
    return bad_category or mentions_sleep


def build_sleep_action_plan() -> str:
    """
    Μικρό πλάνο 3 βημάτων για πιο φροντισμένο ύπνο, σε markdown.
    """
    return (
        "Βλέπω ότι ο ύπνος σου σε δυσκολεύει αρκετά το τελευταίο διάστημα. "
        "Δεν χρειάζεται να το λύσουμε τέλεια· ας δοκιμάσουμε ένα μικρό, ήπιο πλάνο:\n\n"
        "1. **Μικρή «τελετουργία κλεισίματος» 15′ πριν τον ύπνο**  \n"
        "   Για ένα τέταρτο πριν ξαπλώσεις, απόφυγε οθόνες/scroll και κάνε κάτι ήρεμο "
        "(λίγη μουσική, ελαφρύ τέντωμα, ζεστό ρόφημα χωρίς καφεΐνη).\n\n"
        "2. **Καταγραφή σκέψεων σε ένα χαρτί**  \n"
        "   Αν πριν τον ύπνο «τρέχει» το μυαλό σου, γράψε σε ένα χαρτί 3 φράσεις: "
        "«Αυτό με απασχολεί τώρα…». Δεν χρειάζεται λύση, μόνο να το βγάλεις από το κεφάλι.\n\n"
        "3. **Μία άσκηση αναπνοής 4–2–6 στο κρεβάτι**  \n"
        "   Πριν κλείσεις τα μάτια, κάνε 5 γύρους: εισπνοή 4'', κράτημα 2'', εκπνοή 6''. "
        "Αν βαριέσαι να μετράς, χρησιμοποίησε τον ρυθμό της αναπνοής σαν «νανούρισμα».\n\n"
        "Στόχος δεν είναι να κοιμάσαι τέλεια κάθε βράδυ, αλλά να στείλεις στο σώμα σου το μήνυμα "
        "ότι δικαιούται λίγη ηρεμία πριν το τέλος της μέρας."
    )


# ============================================================
#      HELPERS ΓΙΑ ΑΠΟΘΗΚΕΥΣΕΙΣ (ΦΡΑΣΕΙΣ / ΑΣΚΗΣΕΙΣ / ΑΝΑΜΝΗΣΗ)
# ============================================================

def save_support_phrase(text: str, source: str = "bot") -> None:
    """
    Αποθηκεύει μία φράση στήριξης σε CSV (support_phrases.csv).
    """
    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source": source,
        "text": str(text).replace("\n", " ").strip(),
    }

    if os.path.exists(SUPPORT_PHRASES_CSV):
        df = pd.read_csv(SUPPORT_PHRASES_CSV)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_csv(SUPPORT_PHRASES_CSV, index=False)


def save_exercise_completion(ex_id: str, label: str) -> None:
    """
    Καταγράφει μια ολοκληρωμένη άσκηση σε exercises_log.csv.
    """
    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "exercise_id": ex_id,
        "label": label,
    }

    if os.path.exists(EXERCISES_CSV):
        df = pd.read_csv(EXERCISES_CSV)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_csv(EXERCISES_CSV, index=False)


def load_wellness_history() -> dict:
    """
    Φορτώνει το ιστορικό ευεξίας από JSON, αν υπάρχει.
    """
    if os.path.exists(USER_HISTORY_JSON):
        try:
            with open(USER_HISTORY_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_wellness_history(data: dict) -> None:
    """
    Αποθηκεύει το ιστορικό ευεξίας σε JSON.
    """
    with open(USER_HISTORY_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
#                 APP CONFIG
# ============================================================

st.set_page_config(
    page_title="Project Wellness",
    page_icon="🧠",
    layout="wide",
)

load_css()

# Session state
if "messages" not in st.session_state:
    # κάθε στοιχείο: (sender, content) όπου sender ∈ {"user","bot","exercise","map","emergency","plan"}
    st.session_state.messages = []

if "exercise_followup" not in st.session_state:
    st.session_state.exercise_followup = False

# για το άγχος σπουδών
if "study_anxiety_count" not in st.session_state:
    st.session_state.study_anxiety_count = 0

if "study_anxiety_plan_given" not in st.session_state:
    st.session_state.study_anxiety_plan_given = False

# για το πλάνο ύπνου
if "sleep_plan_count" not in st.session_state:
    st.session_state.sleep_plan_count = 0

if "sleep_plan_given" not in st.session_state:
    st.session_state.sleep_plan_given = False


# ============================================================
#               AVATARS (αν ποτέ τα χρειαστείς)
# ============================================================

def load_avatar(name: str):
    path = os.path.join(BASE_DIR, "static", "avatars", f"{name}.png")
    if os.path.exists(path):
        return Image.open(path)
    return None


avatar_user = load_avatar("user")
avatar_bot = load_avatar("bot")


# ============================================================
#               SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:
    st.markdown("### 🧠 Project Wellness")
    st.markdown(
        "<div class='sidebar-subtitle'>Μικρές κουβέντες, μικρά βήματα φροντίδας.</div>",
        unsafe_allow_html=True,
    )
    page = st.radio(
        "Πλοήγηση",
        [
            "💬 Chat",
            "⭐ Φράσεις Στήριξης",
            "📁 Ιστορικό",
            "📊 Στατιστικά",
            "🧘 Ασκήσεις",
            "📜 Ιστορικό Ευεξίας",
            "👤 Προφίλ",
            "ℹ️ Σχετικά & Ασφάλεια",
        ],
    )


# ============================================================
#                     CHAT PAGE
# ============================================================

if page == "💬 Chat":
    # Φέρνουμε το προφίλ χρήστη για να το περάσουμε στο LLM
    from user_profile import load_profile
    profile = load_profile()

    st.markdown(
        """
        <div class="page-header">
            <h1>🧡 Wellness Edition</h1>
            <p>Μίλησέ μου λίγο για τη μέρα σου – θα προσπαθήσω να τη χαρτογραφήσω μαζί σου.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 😊 Πώς είσαι σήμερα;")

    # Μικρό disclaimer ασφαλείας στο βασικό chat
    st.markdown(
        """
        <div class="disclaimer-box">
            <strong>⚠️ Σημαντική υπενθύμιση</strong><br>
            Το Project Wellness είναι εργαλείο αυτοβοήθειας και ψυχοεκπαιδευτικού χαρακτήρα. 
            Δεν αντικαθιστά ψυχολόγο, ψυχίατρο ή υπηρεσίες έκτακτης ανάγκης.<br>
            Αν νιώθεις ότι κινδυνεύεις εσύ ή κάποιος άλλος, κάλεσε άμεσα το <strong>112</strong> 
            ή τη Γραμμή Παρέμβασης για την Αυτοκτονία <strong>1018</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    mood_map = {"😔": 10, "😕": 30, "😐": 50, "🙂": 70, "😄": 90}
    mood_emoji = st.radio("Διάθεση:", list(mood_map.keys()), horizontal=True)
    mood_value = mood_map[mood_emoji]

    # Mood bar
    mood_percent = mood_value / 100
    st.markdown(
        f"""
        <div class="mood-bar">
            <div class="mood-indicator" style="width:{mood_percent*100}%;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        sleep = st.radio("Ύπνος", ["0–2", "3–5", "6–8", "9+"], horizontal=True)
    with col2:
        water = st.radio("Νερό", ["0", "1–3", "4–6", "7+"], horizontal=True)

    user_text = st.text_area("📝 Γράψε μου ό,τι θέλεις για τη μέρα σου:", height=120)

    if st.button("Αποστολή"):
        text = user_text.strip()

        if not text:
            st.warning("Γράψε κάτι μικρό πριν πατήσεις αποστολή 🙂")
        else:
            # 1. Έλεγχος για επείγουσα κατάσταση
            if is_emergency(text):
                emergency_html = emergency_message()
                st.session_state.messages.append(("emergency", emergency_html))
                log_user_data("EMERGENCY", "-", "-", text)
                st.rerun()

            # 2. Μήνυμα χρήστη
            st.session_state.messages.append(("user", text))

            # 3. Προσωπική σύνοψη (rule-based)
            summary = personal_reply(mood_value, sleep, water)
            st.session_state.messages.append(("bot", summary))

            # 4. Θεραπευτικού τύπου απάντηση (LLM + fallback)
            llm_output = llm_therapeutic_reply(
                mood_value,
                sleep,
                water,
                text,
                profile,   # <-- περνάμε και το προφίλ εδώ
            )

            if llm_output is not None:
                st.session_state.messages.append(("bot", llm_output))
            else:
                rb = fallback_therapeutic_reply(mood_value, sleep, water, text)
                st.session_state.messages.append(("bot", rb))

            # 5. Άσκηση
            ex = exercise_suggestion(mood_value, sleep, water, text)
            st.session_state.messages.append(("exercise", ex))

            # 6. Συναισθηματικός χάρτης ημέρας
            map_html = render_emotional_map(mood_value, sleep, water, text)
            st.session_state.messages.append(("map", map_html))

            # 7. Ανίχνευση «άγχους σπουδών» για πλάνο δράσης
            if (
                detect_study_anxiety(text)
                and not st.session_state.study_anxiety_plan_given
            ):
                st.session_state.study_anxiety_count += 1
                # Μετά από 2 φορές που αναφέρεται το ίδιο θέμα → δίνουμε πλάνο
                if st.session_state.study_anxiety_count >= 2:
                    plan_text = build_study_action_plan()
                    st.session_state.messages.append(("plan", plan_text))
                    st.session_state.study_anxiety_plan_given = True

            # 7β. Ανίχνευση δυσκολιών ύπνου για δεύτερο πλάνο δράσης
            if (
                detect_sleep_difficulty(sleep, text)
                and not st.session_state.sleep_plan_given
            ):
                st.session_state.sleep_plan_count += 1
                # Μετά από 2 καταγραφές με έντονο θέμα ύπνου → δίνουμε πλάνο
                if st.session_state.sleep_plan_count >= 2:
                    sleep_plan = build_sleep_action_plan()
                    st.session_state.messages.append(("plan", sleep_plan))
                    st.session_state.sleep_plan_given = True

            # 8. Log σε CSV (ο data_logger σου γράφει σε user_data.csv)
            log_user_data(mood_value, sleep, water, text)

            st.rerun()

    st.markdown("---")

    # Render ιστορικού συζήτησης + κουμπιά αποθήκευσης φράσεων
    for idx, (sender, content) in enumerate(st.session_state.messages):
        if sender == "user":
            render_message("user", content)

        elif sender == "bot":
            render_message("bot", content)
            if st.button("⭐ Αποθήκευση φράσης στήριξης", key=f"save_bot_{idx}"):
                save_support_phrase(content, source="bot")
                st.success("Η φράση αποθηκεύτηκε στις «Φράσεις Στήριξης» ✨")

        elif sender == "exercise":
            render_exercise_card(content)

        elif sender == "map":
            st.markdown(content, unsafe_allow_html=True)

        elif sender == "emergency":
            render_emergency_block(content)

        elif sender == "plan":
            render_action_plan_card(content)
            if st.button("⭐ Αποθήκευση αυτού του πλάνου", key=f"save_plan_{idx}"):
                save_support_phrase(content, source="plan")
                st.success("Το πλάνο αποθηκεύτηκε στις «Φράσεις Στήριξης» ✨")


# ============================================================
#              ΦΡΑΣΕΙΣ ΣΤΗΡΙΞΗΣ PAGE
# ============================================================

elif page == "⭐ Φράσεις Στήριξης":
    st.markdown(
        """
        <div class="page-header">
            <h1>⭐ Φράσεις Στήριξης</h1>
            <p>Μικρή προσωπική συλλογή από λόγια που σου μίλησαν.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if os.path.exists(SUPPORT_PHRASES_CSV):
        df = pd.read_csv(SUPPORT_PHRASES_CSV)

        if not df.empty:
            st.markdown("### Πρόσφατες φράσεις (τελευταίες 10)")

            for _, row in df.tail(10).iterrows():
                ts = row.get("timestamp", "-")
                src_raw = row.get("source", "bot")
                if src_raw == "plan":
                    src = "πλάνο δράσης"
                else:
                    src = "μήνυμα bot"
                text = str(row.get("text", "")).strip()
                st.markdown(
                    f"- *{ts}* – **({src})**  \n"
                    f"  “{text}”"
                )

            st.markdown("---")
            st.markdown("### Πλήρης λίστα")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Δεν έχεις αποθηκεύσει ακόμη κάποια φράση στήριξης.")
    else:
        st.info("Δεν έχεις αποθηκεύσει ακόμη κάποια φράση στήριξης.")


# ============================================================
#                     ΙΣΤΟΡΙΚΟ PAGE
# ============================================================

elif page == "📁 Ιστορικό":
    st.markdown(
        """
        <div class="page-header">
            <h1>📁 Ιστορικό Καταγραφών</h1>
            <p>Γενική λίστα με τις καταγραφές σου, όπως αποθηκεύονται στο CSV.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    csv_path = os.path.join(BASE_DIR, "..", "user_data.csv")

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        st.dataframe(df, use_container_width=True)
    else:
        st.info(
            "Δεν βρέθηκε αρχείο user_data.csv. "
            "Μίλησε λίγο με το bot στην καρτέλα Chat για να δημιουργηθεί."
        )


# ============================================================
#                     ΣΤΑΤΙΣΤΙΚΑ PAGE
# ============================================================

elif page == "📊 Στατιστικά":
    st.markdown(
        """
        <div class="page-header">
            <h1>📊 Μικρό ταμπλό ευεξίας</h1>
            <p>Γράφημα διάθεσης και μικρές συγκεντρωτικές πληροφορίες για ύπνο & νερό.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    csv_path = os.path.join(BASE_DIR, "..", "user_data.csv")

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="ignore")

        if "mood" in df.columns and "timestamp" in df.columns:
            st.markdown("### Διάθεση στο χρόνο")
            mood_chart = df[["timestamp", "mood"]].set_index("timestamp")
            st.line_chart(mood_chart)

        col1, col2 = st.columns(2)
        with col1:
            if "sleep" in df.columns:
                st.markdown("#### Συχνότητες κατηγοριών ύπνου")
                sleep_counts = df["sleep"].value_counts()
                st.bar_chart(sleep_counts)
        with col2:
            if "water" in df.columns:
                st.markdown("#### Συχνότητες κατηγοριών νερού")
                water_counts = df["water"].value_counts()
                st.bar_chart(water_counts)

        if "message" in df.columns:
            st.markdown("### Τελευταίες 5 καταγραφές (σύντομη ματιά)")
            for _, row in df.tail(5).iterrows():
                ts = row["timestamp"] if "timestamp" in row else "-"
                st.write(
                    f"- **{ts}** – διάθεση: {row.get('mood', '?')} – "
                    f"*{str(row['message'])[:80]}*..."
                )
    else:
        st.info(
            "Δεν υπάρχουν ακόμη δεδομένα για στατιστικά. "
            "Χρειάζεται πρώτα να κάνεις μερικά check-ins στην καρτέλα «Chat»."
        )


# ============================================================
#                     ΑΣΚΗΣΕΙΣ PAGE
# ============================================================

elif page == "🧘 Ασκήσεις":
    st.markdown(
        """
        <div class="page-header">
            <h1>🧘 Μικρή Βιβλιοθήκη Ασκήσεων</h1>
            <p>Βασικές μικρο-ασκήσεις που σου προτείνει και το ίδιο το bot.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="breathing-container">
            <div class="breathing-circle"></div>
            <p>Ακολούθησε τον ρυθμό: εισπνοή όταν ο κύκλος μεγαλώνει, εκπνοή όταν μικραίνει.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Άσκηση 1
    st.markdown("### 1. Άσκηση αναπνοής 4–2–6")
    st.write(
        "Κατάλληλη όταν νιώθεις έντονο άγχος, πανικό ή σωματική ένταση.\n\n"
        "• Εισπνοή από τη μύτη για 4''\n"
        "• Κράτημα της αναπνοής για 2''\n"
        "• Αργή εκπνοή από το στόμα για 6''\n"
        "↳ Επανάλαβε 5 φορές."
    )
    if st.button("✅ Το έκανα τώρα", key="ex_breathing"):
        save_exercise_completion("breathing_4_2_6", "Άσκηση αναπνοής 4–2–6")
        st.success("Μπράβο σου που δοκίμασες την άσκηση αναπνοής ✨")

    st.markdown("---")

    # Άσκηση 2
    st.markdown("### 2. Μικρή άσκηση αποφόρτισης σκέψεων")
    st.write(
        "Γράψε μία πρόταση που αρχίζει με: «Αυτό που με βαραίνει περισσότερο είναι…» "
        "χωρίς να τη φιλτράρεις. Το πρώτο πράγμα που θα σου βγει είναι συνήθως και το πιο σημαντικό."
    )
    if st.button("✅ Την έκανα / θα την κάνω τώρα", key="ex_thought_dump"):
        save_exercise_completion("thought_dump", "Άσκηση αποφόρτισης σκέψεων")
        st.success("Κατέγραψες/θα καταγράψεις αυτό που σε βαραίνει — μικρό αλλά σημαντικό βήμα 💛")

    st.markdown("---")

    # Άσκηση 3
    st.markdown("### 3. Άσκηση ηρεμίας για θλίψη / μοναξιά")
    st.write(
        "Βάλε το χέρι στο στήθος σου, πάρε μία αργή ανάσα και πες από μέσα σου:\n\n"
        "_«Είναι εντάξει να νιώθω έτσι. Δεν είμαι μόνος/η σε αυτό που ζω.»_"
    )
    if st.button("✅ Το δοκίμασα", key="ex_soothing_phrase"):
        save_exercise_completion("soothing_phrase", "Άσκηση ηρεμίας για θλίψη / μοναξιά")
        st.success("Χάρισες μια στιγμή καλοσύνης στον εαυτό σου 🧡")

    st.markdown("---")

    # Άσκηση 4
    st.markdown("### 4. Μικρή άσκηση φροντίδας σώματος")
    st.write(
        "Αν δεν έχεις πιει νερό όλη μέρα, ένα απλό ποτήρι είναι πράξη φροντίδας "
        "για το σώμα και το μυαλό σου."
    )
    if st.button("✅ Ήπια / θα πιω ένα ποτήρι νερό", key="ex_water"):
        save_exercise_completion("body_care_water", "Άσκηση φροντίδας σώματος (νερό)")
        st.success("Ένα ποτήρι νερό είναι μικρή αλλά πραγματική πράξη αυτοφροντίδας 💧")

    # Μικρό ταμπλό προόδου ασκήσεων (dominant pastel κάρτα)
    if os.path.exists(EXERCISES_CSV):
        df = pd.read_csv(EXERCISES_CSV)
        if not df.empty:
            st.markdown('<div class="exercise-progress-card">', unsafe_allow_html=True)

            st.markdown("### Μικρή εικόνα προόδου με τις ασκήσεις")

            counts = df["label"].value_counts()

            st.markdown('<div class="chart-holder">', unsafe_allow_html=True)
            st.bar_chart(counts)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("#### Τελευταίες 5 ολοκληρώσεις")
            st.markdown('<div class="exercise-table-holder">', unsafe_allow_html=True)
            for _, row in df.tail(5).iterrows():
                ts = row.get("timestamp", "-")
                label = row.get("label", "")
                st.write(f"- **{ts}** – {label}")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info(
            "Δεν υπάρχουν ακόμη καταγραφές ολοκληρωμένων ασκήσεων. "
            "Μπορείς να ξεκινήσεις πατώντας «Το έκανα τώρα» σε όποια άσκηση δοκιμάσεις."
        )


# ============================================================
#               WELLNESS ANAMNESIS PAGE
# ============================================================

elif page == "📜 Ιστορικό Ευεξίας":
    st.markdown(
        """
        <div class="page-header">
            <h1>📜 Ιστορικό Ευεξίας (Wellness Anamnesis)</h1>
            <p>Ένας πιο «βαθύς» καμβάς για το πώς σε δυσκολεύουν τα πράγματα μέσα στον χρόνο.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    history = load_wellness_history()

    st.markdown(
        """
        Στόχος αυτής της σελίδας δεν είναι η διάγνωση, αλλά να έχεις κάπου συγκεντρωμένα
        όσα θα έλεγες ίσως σε έναν θεραπευτή ή σε ένα πιο μεγάλο check–in.
        Μπορείς να το συμπληρώνεις και να το αλλάζεις όποτε θέλεις.
        """
    )

    since_when = st.text_input(
        "Από πότε νιώθεις ότι σε απασχολούν περισσότερο αυτά που περιγράφεις;",
        value=history.get("since_when", ""),
        placeholder="π.χ. Από το λύκειο, τα τελευταία 2 χρόνια, από την αρχή της σχολής…",
    )

    main_concerns = st.text_area(
        "Τι σε δυσκολεύει περισσότερο σε συναισθηματικό επίπεδο αυτή την περίοδο;",
        value=history.get("main_concerns", ""),
        height=120,
    )

    desired_changes = st.text_area(
        "Αν μπορούσες να αλλάξεις 1–2 πράγματα στην καθημερινότητά σου, τι θα ήταν;",
        value=history.get("desired_changes", ""),
        height=120,
    )

    tried_before = st.text_area(
        "Τι έχεις δοκιμάσει μέχρι τώρα (μόνος/η σου ή με βοήθεια); Τι βοήθησε / τι όχι;",
        value=history.get("tried_before", ""),
        height=120,
    )

    stressors = st.text_area(
        "Ποιοι είναι οι βασικοί στρεσογόνοι παράγοντες στη ζωή σου;",
        value=history.get("stressors", ""),
        height=120,
        placeholder="π.χ. σπουδές, οικονομικά, οικογένεια, σχέσεις, υγεία…",
    )

    emotional_patterns = st.text_area(
        "Υπάρχουν συναισθηματικά μοτίβα που βλέπεις να επαναλαμβάνονται; (π.χ. αυτοκριτική, αναβλητικότητα, φόβος αποτυχίας)",
        value=history.get("emotional_patterns", ""),
        height=120,
    )

    notes_for_therapist = st.text_area(
        "Οτιδήποτε νιώθεις πως θα ήταν χρήσιμο να ξέρει ένας μελλοντικός θεραπευτής για εσένα.",
        value=history.get("notes_for_therapist", ""),
        height=120,
    )

    if st.button("💾 Αποθήκευση ιστορικού ευεξίας"):
        new_history = {
            "since_when": since_when,
            "main_concerns": main_concerns,
            "desired_changes": desired_changes,
            "tried_before": tried_before,
            "stressors": stressors,
            "emotional_patterns": emotional_patterns,
            "notes_for_therapist": notes_for_therapist,
            "last_updated": datetime.now().isoformat(timespec="seconds"),
        }
        save_wellness_history(new_history)
        st.success("Το ιστορικό ευεξίας αποθηκεύτηκε. Μπορείς να το τροποποιείς όποτε θέλεις 🙂")

    if history.get("last_updated"):
        st.markdown(
            f"<p style='font-size:0.85rem;color:#666;'>Τελευταία ενημέρωση: {history.get('last_updated')}</p>",
            unsafe_allow_html=True,
        )


# ============================================================
#                     ΠΡΟΦΙΛ PAGE
# ============================================================

elif page == "👤 Προφίλ":
    from user_profile import load_profile, save_profile

    st.markdown(
        """
        <div class="page-header">
            <h1>👤 Προφίλ Χρήστη</h1>
            <p>Μερικές βασικές πληροφορίες που βοηθούν την εφαρμογή να καταλαβαίνει καλύτερα το πλαίσιο σου.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    profile = load_profile()

    st.markdown("### 📝 Βασικά στοιχεία")

    name = st.text_input("Όνομα ή ψευδώνυμο", value=profile.get("name", ""))
    age_range_options = ["", "18–24", "25–34", "35–44", "45+"]
    current_age_range = profile.get("age_range", "")
    if current_age_range not in age_range_options:
        current_age_range = ""
    age_range = st.selectbox(
        "Ηλικιακή ομάδα",
        age_range_options,
        index=age_range_options.index(current_age_range),
    )
    context = st.text_input(
        "Πλαίσιο ζωής / ρόλος (π.χ. φοιτητής, εργαζόμενος)",
        value=profile.get("context", "")
    )

    st.markdown("---")
    st.markdown("### 🎯 Στόχοι")

    main_goals = st.text_area(
        "Ποιοι είναι οι βασικοί σου στόχοι ευεξίας αυτή την περίοδο;",
        value=profile.get("main_goals", "")
    )

    st.markdown("---")
    st.markdown("### 😕 Δυσκολίες & ανάγκες")

    main_struggles = st.text_area(
        "Τι σε δυσκολεύει περισσότερο τον τελευταίο καιρό;",
        value=profile.get("main_struggles", "")
    )

    helpful_things = st.text_area(
        "Τι σε βοηθά συνήθως (ακόμη κι αν είναι μικρό);",
        value=profile.get("helpful_things", "")
    )

    st.markdown("---")

    if st.button("💾 Αποθήκευση προφίλ"):
        new_profile = {
            "name": name,
            "age_range": age_range,
            "context": context,
            "main_goals": main_goals,
            "main_struggles": main_struggles,
            "helpful_things": helpful_things,
        }
        save_profile(new_profile)
        st.success("Το προφίλ σου αποθηκεύτηκε επιτυχώς 🙂")


# ============================================================
#                 ΣΧΕΤΙΚΑ & ΑΣΦΑΛΕΙΑ PAGE
# ============================================================

elif page == "ℹ️ Σχετικά & Ασφάλεια":
    st.markdown(
        """
        <div class="page-header">
            <h1>ℹ️ Σχετικά με το Project Wellness</h1>
            <p>Ένα υβριδικό (rule-based + LLM) εργαλείο συναισθηματικού check-in και ήπιας υποστήριξης.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Τι κάνει η εφαρμογή;")
    st.markdown(
        """
        - Καταγράφει **διάθεση**, **ύπνο** και **ενυδάτωση** καθημερινά.  
        - Δημιουργεί **προσωπική, rule-based περίληψη** της κατάστασης.  
        - Παράγει **θεραπευτικού τύπου απαντήσεις** με τη βοήθεια LLM, 
          χωρίς να δίνει διαγνώσεις ή ιατρικές οδηγίες.  
        - Προτείνει **μικρές ασκήσεις αυτοφροντίδας** (αναπνοές, journaling κτλ.).  
        - Δημιουργεί έναν **mini “Συναισθηματικό Χάρτη Ημέρας”** με 3–4 λέξεις-κλειδιά.  
        - Καταγράφει ανώνυμα τα δεδομένα σε CSV, ώστε να φαίνονται **στατιστικά ευεξίας**.
        """
    )

    st.markdown("### Αρχιτεκτονική (για τη διπλωματική)")
    st.markdown(
        """
        - **Υβριδικό σύστημα**:  
          - Κανόνες (rule-based) → βασική περίληψη, ασκήσεις, ανίχνευση «red flags».  
          - LLM (OpenAI) → πιο φυσικές, ανθρώπινες απαντήσεις, με ψυχοεκπαιδευτικό ύφος.  
        - Διαχωρισμός σε modules:  
          - `app.py` → ροή εφαρμογής & UI σε Streamlit  
          - `rules.py` → κανόνες για διάθεση/ύπνο/νερό, ασκήσεις, emergency handling  
          - `llm.py` → κλήσεις στο μοντέλο (LLM) + fallback  
          - `emotional_map.py` → εξαγωγή tags για τον «Συναισθηματικό Χάρτη Ημέρας»  
          - `components.py` → UI components (μηνύματα, κάρτες, action plans)  
          - `data_logger.py` → καταγραφή σε CSV  
        - Το API key περνάει **μέσω `st.secrets`** (`.streamlit/secrets.toml`) 
          και δεν εμφανίζεται στον κώδικα.
        """
    )

    st.markdown("### Μέτρα Ασφαλείας")
    st.markdown(
        """
        - Ανίχνευση συγκεκριμένων φράσεων που μπορεί να σχετίζονται με:  
          αυτοκτονικό ιδεασμό, σοβαρή αυτοβλάβη ή έντονη κρίση.  
        - Σε αυτές τις περιπτώσεις:  
          - Δεν συνεχίζει σε «θεραπευτική» συζήτηση.  
          - Εμφανίζει **ειδικό emergency μήνυμα** με γραμμές βοήθειας.  
          - Υπενθυμίζει ότι **δεν** υποκαθιστά ψυχολόγο ή υπηρεσίες έκτακτης ανάγκης.
        """
    )

    st.markdown("### 📞 Γραμμές Βοήθειας (Ελλάδα)")
    st.markdown(
        """
        - **1018** – Γραμμή Παρέμβασης για την Αυτοκτονία (24/7)  
        - **112** – Ευρωπαϊκός αριθμός έκτακτης ανάγκης  
        - **10306** – Γραμμή Ψυχοκοινωνικής Υποστήριξης  
        - **1056** – «Χαμόγελο του Παιδιού» (για ανηλίκους)
        """
    )

    st.markdown("### Disclaimer")
    st.markdown(
        """
        > Το Project Wellness είναι εργαλείο αυτοβοήθειας και ψυχοεκπαιδευτικού χαρακτήρα.  
        > Δεν αποτελεί μέσο διάγνωσης, ψυχοθεραπείας ή άμεσης παρέμβασης σε κρίση.  
        > Σε περίπτωση κινδύνου για εσένα ή άλλους, κάλεσε το **112** ή τη Γραμμή Παρέμβασης **1018**.
        """
    )
