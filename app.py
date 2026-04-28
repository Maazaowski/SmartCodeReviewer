import streamlit as st
import anthropic
import json

# --- Page config ---
st.set_page_config(
    page_title="Smart Code Reviewer",
    page_icon="🔍",
    layout="wide",
)

# --- Styles ---
st.markdown("""
<style>
    .review-card {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .card-readability  { border-color: #89b4fa; }
    .card-structure    { border-color: #a6e3a1; }
    .card-maintainability { border-color: #fab387; }
    .card-positive     { border-color: #f9e2af; }
    .card-score        { border-color: #cba6f7; }
    .score-badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- System prompt ---
SYSTEM_PROMPT = """You are an expert software engineer conducting a thorough pre-review of code before it reaches human reviewers.

Your task is to analyze the submitted code and return a JSON object — nothing else, no markdown fences — with this exact structure:

{
  "language_detected": "<language>",
  "overall_score": <integer 1-10>,
  "overall_summary": "<2-3 sentence executive summary>",
  "readability": {
    "score": <integer 1-10>,
    "summary": "<one concise sentence>",
    "issues": ["<issue 1>", "<issue 2>", ...],
    "suggestions": ["<suggestion 1>", "<suggestion 2>", ...]
  },
  "structure": {
    "score": <integer 1-10>,
    "summary": "<one concise sentence>",
    "issues": ["<issue 1>", ...],
    "suggestions": ["<suggestion 1>", ...]
  },
  "maintainability": {
    "score": <integer 1-10>,
    "summary": "<one concise sentence>",
    "issues": ["<issue 1>", ...],
    "suggestions": ["<suggestion 1>", ...]
  },
  "positive_note": "<one specific thing done well — be concrete, not generic>"
}

Scoring guide: 1-3 needs major work, 4-6 acceptable with improvements, 7-9 good, 10 excellent.
Be specific and actionable. Avoid vague advice like "use better names" — name the actual identifiers.
If the code is very short or trivial, still provide useful feedback based on what is present."""

def score_color(score: int) -> str:
    if score >= 8:
        return "#a6e3a1"
    elif score >= 5:
        return "#f9e2af"
    return "#f38ba8"

def render_category(title: str, icon: str, css_class: str, data: dict):
    color = score_color(data["score"])
    st.markdown(f"""
    <div class="review-card {css_class}">
        <h4 style="margin:0 0 0.4rem 0">{icon} {title}
            <span class="score-badge" style="background:{color}22; color:{color}; margin-left:0.5rem">
                {data['score']}/10
            </span>
        </h4>
        <p style="color:#cdd6f4; margin:0 0 0.6rem 0"><em>{data['summary']}</em></p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if data["issues"]:
            st.markdown("**Issues found**")
            for issue in data["issues"]:
                st.markdown(f"- {issue}")
        else:
            st.markdown("*No significant issues.*")
    with col2:
        if data["suggestions"]:
            st.markdown("**Suggestions**")
            for s in data["suggestions"]:
                st.markdown(f"- {s}")

# --- Header ---
st.title("🔍 Smart Code Reviewer")
st.markdown("Paste your code below for an AI-powered review covering **readability**, **structure**, and **maintainability** — before it hits human review.")
st.divider()

# --- Input ---
col_left, col_right = st.columns([3, 1])

with col_left:
    code_input = st.text_area(
        "Paste your code here",
        height=320,
        placeholder="def calculate_total(items):\n    t = 0\n    for i in items:\n        t += i['p'] * i['q']\n    return t",
        label_visibility="collapsed",
    )

with col_right:
    language_hint = st.selectbox(
        "Language hint (optional)",
        ["Auto-detect", "Python", "JavaScript", "TypeScript", "Java", "C#", "C++",
         "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "SQL", "Bash", "Other"],
    )
    api_key = st.text_input(
        "Anthropic API key",
        type="password",
        placeholder="sk-ant-...",
        help="Your key is never stored. Get one free at console.anthropic.com",
    )
    review_btn = st.button("Review Code", type="primary", use_container_width=True, disabled=not code_input.strip())

# --- Review logic ---
if review_btn:
    if not api_key.strip():
        st.error("Please enter your Anthropic API key.")
        st.stop()
    if len(code_input.strip()) < 10:
        st.warning("Please paste some code to review.")
        st.stop()

    lang_note = f" The language is {language_hint}." if language_hint != "Auto-detect" else ""
    user_message = f"Please review the following code.{lang_note}\n\n```\n{code_input}\n```"

    with st.spinner("Reviewing your code..."):
        try:
            client = anthropic.Anthropic(api_key=api_key.strip())
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
            raw = message.content[0].text.strip()
            # Strip markdown fences if model wraps anyway
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            result = json.loads(raw)
        except json.JSONDecodeError:
            st.error("The model returned an unexpected format. Please try again.")
            st.stop()
        except anthropic.AuthenticationError:
            st.error("Invalid API key. Please check and try again.")
            st.stop()
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()

    # --- Results ---
    st.divider()

    # Overall score banner
    overall_color = score_color(result["overall_score"])
    detected = result.get("language_detected", language_hint)
    st.markdown(f"""
    <div class="review-card card-score">
        <h3 style="margin:0 0 0.3rem 0">Overall Score
            <span class="score-badge" style="background:{overall_color}22; color:{overall_color}; margin-left:0.6rem">
                {result['overall_score']}/10
            </span>
            <span style="color:#6c7086; font-size:0.85rem; margin-left:0.8rem">
                {detected}
            </span>
        </h3>
        <p style="color:#cdd6f4; margin:0">{result['overall_summary']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Category cards
    render_category("Readability",      "📖", "card-readability",      result["readability"])
    st.divider()
    render_category("Structure",        "🏗️", "card-structure",        result["structure"])
    st.divider()
    render_category("Maintainability",  "🔧", "card-maintainability",  result["maintainability"])
    st.divider()

    # Positive note
    st.markdown(f"""
    <div class="review-card card-positive">
        <h4 style="margin:0 0 0.3rem 0">⭐ What's done well</h4>
        <p style="color:#f9e2af; margin:0">{result['positive_note']}</p>
    </div>
    """, unsafe_allow_html=True)

# --- Footer ---
st.divider()
st.markdown(
    "<p style='text-align:center; color:#6c7086; font-size:0.8rem'>"
    "Powered by Claude (Anthropic) · Smart Code Reviewer"
    "</p>",
    unsafe_allow_html=True,
)
