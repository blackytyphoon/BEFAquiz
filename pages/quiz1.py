import streamlit as st
import google.generativeai as genai
import re
import json
import time
import os
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Secure API key handling (replace with your actual method of API key management)
GENAI_API_KEY = "AIzaSyBTcMy5sUwBuD1IJqLtyJVptD7Fdm4sOkI"

# Predefined set of ratio analysis questions to ensure reliability
PREDEFINED_QUESTIONS = [
    {
        "question": "Which ratio measures a company's ability to pay short-term obligations?",
        "options": {
            "a": "Debt-to-Equity Ratio",
            "b": "Current Ratio",
            "c": "Return on Assets",
            "d": "Inventory Turnover Ratio"
        },
        "correct_answer": "b",
        "hint": "This ratio compares current assets to current liabilities."
    },
    {
        "question": "What does the Profit Margin Ratio indicate about a company?",
        "options": {
            "a": "Asset efficiency",
            "b": "Debt levels",
            "c": "Profitability of sales",
            "d": "Inventory management"
        },
        "correct_answer": "c",
        "hint": "It shows how much profit is generated from each dollar of sales."
    },
    {
        "question": "The Asset Turnover Ratio measures:",
        "options": {
            "a": "How quickly a company pays its debts",
            "b": "How efficiently a company uses its assets to generate sales",
            "c": "The company's liquidity",
            "d": "Profit per share"
        },
        "correct_answer": "b",
        "hint": "This ratio relates total sales to total assets."
    },
    {
        "question": "Which ratio helps in assessing a company's long-term solvency?",
        "options": {
            "a": "Quick Ratio",
            "b": "Operating Margin",
            "c": "Debt-to-Equity Ratio",
            "d": "Gross Profit Margin"
        },
        "correct_answer": "c",
        "hint": "This ratio compares total liabilities to shareholders' equity."
    },
    {
        "question": "Return on Equity (ROE) indicates:",
        "options": {
            "a": "Sales efficiency",
            "b": "Inventory management",
            "c": "Profitability for shareholders",
            "d": "Short-term liquidity"
        },
        "correct_answer": "c",
        "hint": "It measures profit generated from shareholders' invested capital."
    },
    {
        "question": "The Inventory Turnover Ratio shows:",
        "options": {
            "a": "How quickly inventory is sold",
            "b": "Total inventory value",
            "c": "Profit from inventory sales",
            "d": "Inventory storage costs"
        },
        "correct_answer": "a",
        "hint": "It calculates how many times inventory is sold and replaced in a period."
    },
    {
        "question": "What does the Current Ratio below 1 typically indicate?",
        "options": {
            "a": "Strong financial health",
            "b": "Potential liquidity problems",
            "c": "High profitability",
            "d": "Excellent asset management"
        },
        "correct_answer": "b",
        "hint": "A ratio below 1 suggests difficulty paying short-term obligations."
    },
    {
        "question": "The Debt Ratio measures:",
        "options": {
            "a": "Profitability",
            "b": "Sales efficiency",
            "c": "Proportion of assets financed by debt",
            "d": "Inventory management"
        },
        "correct_answer": "c",
        "hint": "It shows the percentage of total assets funded by creditors."
    },
    {
        "question": "Which ratio helps evaluate operational efficiency?",
        "options": {
            "a": "Current Ratio",
            "b": "Debt-to-Equity Ratio",
            "c": "Operating Expense Ratio",
            "d": "Return on Investment"
        },
        "correct_answer": "c",
        "hint": "This ratio compares operating expenses to total revenue."
    },
    {
        "question": "The Quick Ratio differs from the Current Ratio by excluding:",
        "options": {
            "a": "Cash",
            "b": "Accounts Payable",
            "c": "Inventory",
            "d": "Accounts Receivable"
        },
        "correct_answer": "c",
        "hint": "It's a more conservative liquidity measure that removes inventory."
    }
]

def get_default_animation():
    """Return a simple default animation if loading fails"""
    return {
        "v": "5.5.7",
        "fr": 30,
        "ip": 0,
        "op": 60,
        "w": 100,
        "h": 100,
        "nm": "Default Animation",
        "ddd": 0,
        "assets": [],
        "layers": [{
            "ddd": 0,
            "ind": 1,
            "ty": 4,
            "nm": "Circle",
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [50, 50, 0]},
                "a": {"a": 0, "k": [0, 0, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "shapes": [{
                "ty": "el",
                "p": {"a": 0, "k": [0, 0]},
                "s": {"a": 0, "k": [50, 50]}
            }]
        }]
    }

def load_confetti_animation():
    """Load confetti celebration animation"""
    url = "https://lottie.host/5668398c-cca3-4a30-8c24-74120a644df8/o972OlRDG0.json"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        return get_default_animation()
    except:
        return get_default_animation()

def display_celebration():
    """Display confetti celebration for perfect score"""
    animation = load_confetti_animation()
    
    st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1 style="color: #4CAF50; font-size: 2.5em;">🎉 PERFECT SCORE! 🎉</h1>
        </div>
    """, unsafe_allow_html=True)
    
    st_lottie(
        animation,
        key="celebration_confetti",
        height=300
    )

def generate_questions(num_questions=10):
    """Generate quiz questions from predefined set"""
    import random
    
    # Shuffle and select questions
    selected_questions = random.sample(PREDEFINED_QUESTIONS, min(num_questions, len(PREDEFINED_QUESTIONS)))
    
    return [
        (
            q['question'], 
            q['options'], 
            q['correct_answer'], 
            q['hint']
        ) for q in selected_questions
    ]

def display_questions(questions):
    """Display all questions in the quiz"""
    for i, (question, options, _, hint) in enumerate(questions, 1):
        with st.container():
            st.markdown(f"""
                <div class="question-card">
                    <h3>Question {i}:</h3>
                    <p>{question}</p>
                </div>
            """, unsafe_allow_html=True)
            
            answer = st.radio(
                "Select your answer:",
                options=[
                    f"A) {options['a']}",
                    f"B) {options['b']}",
                    f"C) {options['c']}",
                    f"D) {options['d']}",
                ],
                key=f"question_{i}"
            )
            
            if st.button(f"Show Hint 💡", key=f"hint_{i}"):
                st.markdown(f"""
                    <div class="hint-box">
                        <p><strong>Hint:</strong> {hint}</p>
                    </div>
                """, unsafe_allow_html=True)

def evaluate_answers(questions):
    """Evaluate user answers and calculate score"""
    score = 0
    total_questions = len(questions)
    user_answers = []
    correct_answers = []
    
    for i, (_, _, correct_answer, _) in enumerate(questions, 1):
        user_choice = st.session_state[f"question_{i}"]
        selected_key = user_choice[0].lower()
        user_answers.append(selected_key)
        correct_answers.append(correct_answer)
        
        if selected_key == correct_answer:
            score += 1
    
    return score, total_questions, user_answers, correct_answers

def display_performance_chart(score_history):
    """Display performance history chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(range(1, len(score_history) + 1)),
        y=score_history,
        mode='lines+markers',
        name='Score History',
        line=dict(color='#4CAF50', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title='Your Performance History in Ratio Analysis',
        xaxis_title='Attempt Number',
        yaxis_title='Score',
        plot_bgcolor='#2D2D2D',
        paper_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF'),
        showlegend=False
    )
    
    st.plotly_chart(fig)

def maini():
    """Main application function"""
    # Initialize session state
    if 'questions' not in st.session_state:
        st.session_state.questions = generate_questions()
        st.session_state.submitted = False
        st.session_state.start_time = time.time()
        st.session_state.score_history = []
        st.session_state.attempts = 0
        st.session_state.show_celebration = False

    # Show celebration if perfect score
    if st.session_state.show_celebration:
        display_celebration()

    # Sidebar with statistics
    with st.sidebar:
        st.title("📊 Ratio Analysis Quiz Statistics")
        st.write(f"Total Attempts: {st.session_state.attempts}")
        if st.session_state.score_history:
            st.write(f"Best Score: {max(st.session_state.score_history)}/10")
            st.write(f"Average Score: {sum(st.session_state.score_history)/len(st.session_state.score_history):.1f}/10")
            display_performance_chart(st.session_state.score_history)

    # Main quiz section
    st.title("📊 Ratio Analysis in BEFA Quiz")
    st.subheader("Test Your Knowledge of Financial Ratio Analysis!")

    # Timer
    if not st.session_state.submitted:
        elapsed_time = int(time.time() - st.session_state.start_time)
        st.markdown(f"""
            <div class="timer">
                Time Elapsed: {elapsed_time//60:02d}:{elapsed_time%60:02d}
            </div>
        """, unsafe_allow_html=True)

    # Display questions
    display_questions(st.session_state.questions)

    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Submit Quiz", use_container_width=True):
            st.session_state.submitted = True
            score, total, user_answers, correct_answers = evaluate_answers(st.session_state.questions)
            st.session_state.score_history.append(score)
            st.session_state.attempts += 1
            
            # Display results
            st.markdown(f"""
                <div class="score-card">
                    <h2>Quiz Results</h2>
                    <h3>Your score: {score}/{total} ({(score/total)*100:.1f}%)</h3>
                    <div class="progress-bar" style="width: {(score/total)*100}%;"></div>
                </div>
            """, unsafe_allow_html=True)
            
            # Trigger celebration for perfect score
            if score == total:
                st.session_state.show_celebration = True
                st.rerun()
            
            # Detailed feedback
            st.write("\n### Detailed Feedback:")
            for i, (question, options, correct, _) in enumerate(st.session_state.questions):
                user = user_answers[i]
                is_correct = user == correct
                
                feedback_color = "#4CAF50" if is_correct else "#FF5252"
                st.markdown(f"""
                    <div style="background-color: #2D2D2D; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid {feedback_color}">
                        <p>Question {i+1}: {question}</p>
                        <p>Your answer: {user.upper()}) {options[user]}</p>
                        <p>Correct answer: {correct.upper()}) {options[correct]}</p>
                        <p style="color: {feedback_color}">{'✅ Correct!' if is_correct else '❌ Incorrect'}</p>
                    </div>
                """, unsafe_allow_html=True)

            # Reset button
            if st.button("🔄 Start New Quiz"):
                for key in list(st.session_state.keys()):
                    if key not in ['score_history', 'attempts']:
                        del st.session_state[key]
                st.session_state.show_celebration = False
                st.rerun()

if __name__ == "__main__":
    maini()
