# Smart Code Reviewer

An AI-powered code review assistant that analyzes code for **readability**, **structure**, and **maintainability** before it reaches human reviewers.

Built with [Streamlit](https://streamlit.io) and the [Anthropic Claude API](https://www.anthropic.com).

---

## Features

- Paste any code snippet (auto-detects language)
- Structured review across three dimensions with scores out of 10
- Specific, actionable issues and suggestions — not generic advice
- One highlighted positive note per review
- Overall summary score
- Runs entirely in the browser — API key never stored

## Live Demo

> Deploy to [Streamlit Community Cloud](https://share.streamlit.io) for a free public link.

## Local Setup

```bash
git clone https://github.com/<your-username>/SmartCodeReviewer
cd SmartCodeReviewer
pip install -r requirements.txt
streamlit run app.py
```

You will need a free Anthropic API key from [console.anthropic.com](https://console.anthropic.com).

## How It Works

1. User pastes code into the text area and optionally selects a language
2. The app sends the code to Claude (`claude-sonnet-4-6`) with a structured system prompt
3. Claude returns a JSON review covering readability, structure, and maintainability
4. Results are rendered as scored cards with issues and suggestions

## 100-Word Summary

Smart Code Reviewer is an AI assistant that performs a structured pre-review of code before it reaches human reviewers. Developers paste a snippet, and the app sends it to Claude with a carefully engineered prompt that enforces a JSON response covering three dimensions — readability, structure, and maintainability — each with a score, identified issues, and actionable suggestions. A fourth card highlights one concrete positive note to balance the feedback. Built in Streamlit for instant browser-based access with no backend required, it reduces the cognitive load on human reviewers by surfacing obvious issues automatically, letting reviewers focus on logic, architecture, and domain correctness.
