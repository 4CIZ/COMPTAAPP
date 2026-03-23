import streamlit as st
import pdfplumber
import re
import random
import time
from io import BytesIO

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Quiz Plan Comptable",
    page_icon="📊",
    layout="centered",
)

# ─────────────────────────────────────────────
#  CSS CUSTOM
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0f1117 !important;
}

[data-testid="stAppViewContainer"] > .main {
    background: #0f1117;
}

[data-testid="stSidebar"] { display: none; }

/* ── Hide streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Global font ── */
html, body, p, span, div, label {
    font-family: 'DM Sans', sans-serif;
    color: #e8e8e8;
}

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 300px;
    background: radial-gradient(ellipse at center, rgba(255,214,0,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #ffd600;
    margin-bottom: 0.75rem;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    font-weight: 400;
    color: #ffffff;
    line-height: 1.15;
    margin: 0 0 0.5rem;
}
.hero-sub {
    font-size: 0.95rem;
    color: #888;
    margin: 0;
}

/* ── Score bar ── */
.score-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2rem;
    background: #1a1d27;
    border: 1px solid #2a2d3a;
    border-radius: 16px;
    padding: 1.2rem 2rem;
    margin: 0 auto 2rem;
    max-width: 600px;
}
.score-item {
    text-align: center;
}
.score-num {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #ffd600;
    line-height: 1;
}
.score-num.green { color: #4ade80; }
.score-num.red   { color: #f87171; }
.score-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #555;
    margin-top: 0.25rem;
}
.score-divider {
    width: 1px;
    height: 40px;
    background: #2a2d3a;
}

/* ── Question card ── */
.q-card {
    background: #1a1d27;
    border: 1px solid #2a2d3a;
    border-radius: 20px;
    padding: 2.5rem 2.5rem 2rem;
    margin: 0 auto 1.5rem;
    max-width: 680px;
    position: relative;
    overflow: hidden;
}
.q-card::before {
    content: '';
    position: absolute;
    top: -1px; left: 2rem; right: 2rem;
    height: 3px;
    background: linear-gradient(90deg, transparent, #ffd600, transparent);
    border-radius: 0 0 4px 4px;
}
.q-number {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #ffd600;
    margin-bottom: 1rem;
}
.q-text {
    font-family: 'DM Serif Display', serif;
    font-size: 1.7rem;
    color: #ffffff;
    line-height: 1.3;
    margin: 0;
}

/* ── Choices ── */
.choices-wrapper {
    max-width: 680px;
    margin: 0 auto 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

/* Streamlit radio override */
[data-testid="stRadio"] > div {
    flex-direction: column;
    gap: 0.6rem;
}
[data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    gap: 1rem !important;
    background: #1a1d27 !important;
    border: 1px solid #2a2d3a !important;
    border-radius: 12px !important;
    padding: 1rem 1.4rem !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    font-size: 0.92rem !important;
    color: #ccc !important;
}
[data-testid="stRadio"] label:hover {
    border-color: #ffd600 !important;
    color: #fff !important;
    background: #1f2233 !important;
}
[data-testid="stRadio"] label[data-checked="true"] {
    border-color: #ffd600 !important;
    background: rgba(255,214,0,0.07) !important;
    color: #fff !important;
}

/* ── Feedback banners ── */
.feedback {
    max-width: 680px;
    margin: 0 auto 1.5rem;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    font-size: 0.9rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.feedback.correct {
    background: rgba(74,222,128,0.1);
    border: 1px solid rgba(74,222,128,0.3);
    color: #4ade80;
}
.feedback.wrong {
    background: rgba(248,113,113,0.1);
    border: 1px solid rgba(248,113,113,0.3);
    color: #f87171;
}

/* ── Buttons ── */
[data-testid="stButton"] > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    background: #ffd600 !important;
    color: #0f1117 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 2.5rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 0 0 rgba(255,214,0,0) !important;
}
[data-testid="stButton"] > button:hover {
    background: #ffe833 !important;
    box-shadow: 0 0 24px rgba(255,214,0,0.25) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}

/* ── Secondary button (Nouvelle question) ── */
.btn-secondary [data-testid="stButton"] > button {
    background: transparent !important;
    color: #888 !important;
    border: 1px solid #2a2d3a !important;
}
.btn-secondary [data-testid="stButton"] > button:hover {
    border-color: #555 !important;
    color: #ccc !important;
    box-shadow: none !important;
    background: #1a1d27 !important;
}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: #1a1d27 !important;
    border: 1.5px dashed #2a2d3a !important;
    border-radius: 16px !important;
    padding: 1rem !important;
    max-width: 600px;
    margin: 0 auto;
}
[data-testid="stFileUploader"]:hover {
    border-color: #ffd600 !important;
}

/* ── Progress bar ── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #ffd600, #ffaa00) !important;
    border-radius: 4px !important;
}
[data-testid="stProgress"] > div {
    background: #2a2d3a !important;
    border-radius: 4px !important;
}

/* ── Expander (détails) ── */
[data-testid="stExpander"] {
    background: #1a1d27 !important;
    border: 1px solid #2a2d3a !important;
    border-radius: 12px !important;
    max-width: 680px;
    margin: 0 auto;
}

/* ── End screen ── */
.end-card {
    text-align: center;
    background: #1a1d27;
    border: 1px solid #2a2d3a;
    border-radius: 20px;
    padding: 3rem 2rem;
    max-width: 500px;
    margin: 2rem auto;
}
.end-score {
    font-family: 'DM Serif Display', serif;
    font-size: 4rem;
    color: #ffd600;
    line-height: 1;
}
.end-label {
    font-size: 1rem;
    color: #888;
    margin: 0.5rem 0 2rem;
}
.end-grade {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #fff;
    margin-bottom: 0.5rem;
}

/* ── Divider ── */
hr { border-color: #2a2d3a !important; }

/* ── Info / warning ── */
[data-testid="stAlert"] {
    background: #1a1d27 !important;
    border-color: #2a2d3a !important;
    border-radius: 12px !important;
    color: #888 !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PARSING DU PDF
# ─────────────────────────────────────────────
def parse_accounts(pdf_file) -> dict[str, str]:
    """
    Extrait les couples (numéro → libellé) depuis le PDF ANC.
    Stratégie multi-passes pour gérer les différents formats de mise en page.
    """
    accounts = {}

    with pdfplumber.open(pdf_file) as pdf:
        all_lines = []
        for page in pdf.pages:
            # Extraction par mots avec positions X pour reconstruire les lignes
            words = page.extract_words(x_tolerance=4, y_tolerance=4)
            if not words:
                continue
            # Regrouper les mots par ligne (même y0 approx)
            lines_by_y = {}
            for w in words:
                y_key = round(w["top"] / 3) * 3  # tolérance verticale
                lines_by_y.setdefault(y_key, []).append(w)
            for y_key in sorted(lines_by_y.keys()):
                line_words = sorted(lines_by_y[y_key], key=lambda w: w["x0"])
                line_text = " ".join(w["text"] for w in line_words)
                all_lines.append(line_text)

    # ── Patterns de reconnaissance ──
    # Pattern 1 : "1011 Capital souscrit - non appelé"  (num en début de ligne)
    p1 = re.compile(r'^(\d{2,6})\s+(.{4,})')
    # Pattern 2 : lignes qui commencent par des espaces puis un nombre
    p2 = re.compile(r'^\s{0,6}(\d{2,6})\s+(.{4,})')

    BLACKLIST = {"page", "classe", "sous-", "même", "le cas", "compte à",
                 "comptes", "peuvent", "réservé", "utilisé", "disposition"}

    for line in all_lines:
        line = line.strip()
        if not line:
            continue

        m = p1.match(line) or p2.match(line)
        if not m:
            continue

        num   = m.group(1).strip()
        label = m.group(2).strip()

        # Nettoyage du libellé
        label = re.sub(r'\s+', ' ', label)
        label = label.rstrip('- ')

        # Filtres qualité
        if len(label) < 5:
            continue
        if any(bl in label.lower() for bl in BLACKLIST):
            continue
        if re.search(r'n°\s*\d', label.lower()):   # références réglementaires
            continue
        if label.startswith("("):
            continue

        # On garde le plus court numéro si doublon (comptes parents)
        if num not in accounts:
            accounts[num] = label
        # Si on a déjà ce numéro avec un libellé plus court, on garde le plus précis
        elif len(label) < len(accounts[num]):
            accounts[num] = label

    return accounts


def build_questions(accounts: dict[str, str]) -> list[dict]:
    """Crée une liste de questions QCM à partir des comptes."""
    items = list(accounts.items())
    questions = []
    all_labels = [v for _, v in items]

    for num, correct_label in items:
        # 3 distracteurs parmi les autres libellés
        distractors = random.sample(
            [l for l in all_labels if l != correct_label],
            k=min(3, len(all_labels) - 1)
        )
        choices = distractors + [correct_label]
        random.shuffle(choices)
        questions.append({
            "num": num,
            "correct": correct_label,
            "choices": choices,
        })

    random.shuffle(questions)
    return questions


# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "questions": [],
        "q_index": 0,
        "score": 0,
        "wrong": 0,
        "answered": False,
        "selected": None,
        "phase": "upload",   # upload | quiz | end
        "total": 0,
        "accounts": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
s = st.session_state


# ─────────────────────────────────────────────
#  HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <p class="hero-label">Règlement ANC n° 2014-03</p>
    <h1 class="hero-title">Quiz Plan Comptable</h1>
    <p class="hero-sub">Testez votre maîtrise des comptes du PCG</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PHASE : UPLOAD
# ─────────────────────────────────────────────
if s["phase"] == "upload":
    st.markdown("<br>", unsafe_allow_html=True)

    col_center = st.columns([1, 3, 1])[1]
    with col_center:
        uploaded = st.file_uploader(
            "Chargez le Plan de Comptes (PDF)",
            type="pdf",
            label_visibility="collapsed",
        )

        if uploaded:
            with st.spinner("Analyse du PDF en cours…"):
                accounts = parse_accounts(uploaded)

            if len(accounts) < 4:
                st.error("❌ Impossible d'extraire suffisamment de comptes. Vérifiez le PDF.")
                with st.expander("🔍 Debug — voir le texte brut extrait"):
                    with pdfplumber.open(uploaded) as pdf:
                        raw = pdf.pages[0].extract_text() or "(vide)"
                    st.code(raw[:2000])
            else:
                st.success(f"✅ **{len(accounts)} comptes** extraits avec succès !")
                st.markdown("<br>", unsafe_allow_html=True)

                nb = st.slider(
                    "Nombre de questions",
                    min_value=5,
                    max_value=min(50, len(accounts)),
                    value=min(20, len(accounts)),
                    step=5,
                )

                if st.button("🚀  Lancer le quiz", use_container_width=True):
                    questions = build_questions(accounts)[:nb]
                    s["questions"] = questions
                    s["accounts"] = accounts
                    s["total"] = nb
                    s["q_index"] = 0
                    s["score"] = 0
                    s["wrong"] = 0
                    s["answered"] = False
                    s["selected"] = None
                    s["phase"] = "quiz"
                    st.rerun()


# ─────────────────────────────────────────────
#  PHASE : QUIZ
# ─────────────────────────────────────────────
elif s["phase"] == "quiz":

    questions = s["questions"]
    idx       = s["q_index"]
    total     = s["total"]

    # ── Score bar ──
    pct = round(s["score"] / max(idx, 1) * 100) if idx > 0 else 0
    st.markdown(f"""
    <div class="score-bar">
        <div class="score-item">
            <div class="score-num">{idx}/{total}</div>
            <div class="score-label">Questions</div>
        </div>
        <div class="score-divider"></div>
        <div class="score-item">
            <div class="score-num green">{s['score']}</div>
            <div class="score-label">Correctes</div>
        </div>
        <div class="score-divider"></div>
        <div class="score-item">
            <div class="score-num red">{s['wrong']}</div>
            <div class="score-label">Erreurs</div>
        </div>
        <div class="score-divider"></div>
        <div class="score-item">
            <div class="score-num">{pct}%</div>
            <div class="score-label">Réussite</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Progress ──
    progress_val = idx / total if total > 0 else 0
    st.progress(progress_val)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Question courante ──
    if idx >= total:
        s["phase"] = "end"
        st.rerun()

    q = questions[idx]

    st.markdown(f"""
    <div class="q-card">
        <p class="q-number">Question {idx + 1} sur {total}</p>
        <p class="q-text">Quel est le libellé du compte <span style="color:#ffd600">N° {q['num']}</span> ?</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Choix (radio) ──
    # Clé unique par question pour reset le radio
    radio_key = f"radio_{idx}"
    selected = st.radio(
        "Choisissez une réponse :",
        q["choices"],
        key=radio_key,
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Bouton Valider ──
    if not s["answered"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✔  Valider ma réponse", use_container_width=True):
                s["answered"] = True
                s["selected"] = selected
                if selected == q["correct"]:
                    s["score"] += 1
                else:
                    s["wrong"] += 1
                st.rerun()

    # ── Feedback ──
    if s["answered"]:
        if s["selected"] == q["correct"]:
            st.markdown(f"""
            <div class="feedback correct">
                ✅ &nbsp;<strong>Bonne réponse !</strong> &nbsp;— {q['correct']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="feedback wrong">
                ❌ &nbsp;<strong>Incorrect.</strong> La bonne réponse était : <em>{q['correct']}</em>
            </div>
            """, unsafe_allow_html=True)

        # Bouton suivant
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            label = "→  Question suivante" if idx + 1 < total else "🏁  Voir mes résultats"
            if st.button(label, use_container_width=True):
                s["q_index"] += 1
                s["answered"] = False
                s["selected"] = None
                st.rerun()

    # ── Quitter ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("↩  Changer de PDF", use_container_width=True):
            for k in ["questions","q_index","score","wrong","answered","selected","accounts"]:
                s[k] = [] if k in ["questions"] else (0 if k in ["score","wrong","q_index"] else False if k == "answered" else None if k == "selected" else {})
            s["phase"] = "upload"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PHASE : END
# ─────────────────────────────────────────────
elif s["phase"] == "end":
    total  = s["total"]
    score  = s["score"]
    pct    = round(score / total * 100) if total else 0

    if pct >= 80:
        grade, emoji = "Excellent !", "🏆"
    elif pct >= 60:
        grade, emoji = "Bien joué !", "🎯"
    elif pct >= 40:
        grade, emoji = "Peut mieux faire.", "📚"
    else:
        grade, emoji = "À réviser…", "💪"

    st.markdown(f"""
    <div class="end-card">
        <div style="font-size:3rem;margin-bottom:1rem">{emoji}</div>
        <div class="end-score">{score}/{total}</div>
        <p class="end-label">{pct}% de bonnes réponses</p>
        <p class="end-grade">{grade}</p>
    </div>
    """, unsafe_allow_html=True)

    # Détail des réponses
    with st.expander("📋  Voir le détail des réponses"):
        for q in s["questions"][:total]:
            num, correct = q["num"], q["correct"]
            st.markdown(
                f"**{num}** — {correct}"
            )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄  Rejouer avec le même PDF", use_container_width=True):
            accounts  = s["accounts"]
            nb        = s["total"]
            questions = build_questions(accounts)[:nb]
            s["questions"] = questions
            s["q_index"]   = 0
            s["score"]     = 0
            s["wrong"]     = 0
            s["answered"]  = False
            s["selected"]  = None
            s["phase"]     = "quiz"
            st.rerun()

    st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("↩  Changer de PDF", use_container_width=True):
            s["phase"] = "upload"
            s["accounts"] = {}
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)