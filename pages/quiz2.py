import streamlit as st
import google.generativeai as genai
import re
import json
import time
import os
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests
import random

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
        "hint": "This ratio compares current assets to current liabilities.",
        "explanation": "The Current Ratio is a liquidity ratio that measures a company's ability to pay short-term obligations by comparing current assets to current liabilities."
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
        "hint": "It shows how much profit is generated from each dollar of sales.",
        "explanation": "Profit Margin Ratio reveals the percentage of sales revenue that translates into profit, indicating the company's pricing strategy and cost management."
    },
    {
        "question": "The Debt-to-Equity Ratio compares what two financial components?",
        "options": {
            "a": "Assets to Liabilities",
            "b": "Total Debt to Shareholders' Equity",
            "c": "Revenue to Expenses",
            "d": "Cash to Investments"
        },
        "correct_answer": "b",
        "hint": "This ratio shows the proportion of financing from debt versus equity.",
        "explanation": "The Debt-to-Equity Ratio compares a company's total debt to its shareholders' equity, revealing the company's financial leverage and risk profile."
    },
    {
        "question": "What does the Asset Turnover Ratio measure?",
        "options": {
            "a": "Company's profitability",
            "b": "How efficiently a company uses its assets to generate revenue",
            "c": "Total value of company assets",
            "d": "Company's debt obligations"
        },
        "correct_answer": "b",
        "hint": "It relates sales revenue to total assets.",
        "explanation": "The Asset Turnover Ratio indicates how efficiently a company uses its assets to generate sales revenue."
    },
    {
        "question": "Which ratio helps assess a company's ability to pay interest on its debt?",
        "options": {
            "a": "Liquidity Ratio",
            "b": "Debt Ratio",
            "c": "Interest Coverage Ratio",
            "d": "Profitability Ratio"
        },
        "correct_answer": "c",
        "hint": "It shows how many times a company can cover its interest expenses.",
        "explanation": "The Interest Coverage Ratio measures how many times a company can pay its interest expenses with its available earnings."
    }
]

def apply_custom_styling():
    """Apply custom CSS styling to the Streamlit app"""
    st.markdown("""
    <style>
    /* Global Styling */
    body {
        background-color: #0f172a;
        color: #e2e8f0;
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Question Card Styling */
    .question-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #3b82f6;
    }

    .question-card h3 {
        color: #60a5fa;
        margin-bottom: 10px;
    }

    /* Radio Button Styling */
    .stRadio > div {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 15px;
    }

    .stRadio div[role="radiogroup"] label {
        color: #e2e8f0;
        font-weight: 500;
    }

    /* Button Styling */
    .stButton > button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #2563eb;
        transform: scale(1.05);
    }

    /* Sidebar Styling */
    .css-1aumxhk {
        background-color: #1e293b;
    }

    /* Score Card */
    .score-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .progress-bar {
        height: 8px;
        background-color: #10b981;
        border-radius: 4px;
        margin-top: 15px;
    }

    /* Timer Styling */
    .timer {
        background-color: #1e293b;
        color: #60a5fa;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-weight: bold;
    }

    /* Hint Box */
    .hint-box {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 15px;
        margin-top: 10px;
    }

    /* Feedback Cards */
    .feedback-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }

    .feedback-card:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    </style>
    """, unsafe_allow_html=True)

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
            <h1 style="color: #10B981; font-size: 2.5em; text-shadow: 0 4px 6px rgba(0,0,0,0.1);">🎉 PERFECT SCORE! 🎉</h1>
            <p style="color: #60A5FA; font-size: 1.2em;">Congratulations on mastering Ratio Analysis!</p>
        </div>
    """, unsafe_allow_html=True)
    
    st_lottie(
        animation,
        key="celebration_confetti",
        height=300
    )

def generate_questions(num_questions=5):
    """Generate quiz questions from predefined set"""
    # Shuffle and select questions
    selected_questions = random.sample(PREDEFINED_QUESTIONS, min(num_questions, len(PREDEFINED_QUESTIONS)))
    
    return [
        (
            q['question'], 
            q['options'], 
            q['correct_answer'], 
            q['hint'],
            q.get('explanation', 'No additional explanation available.')
        ) for q in selected_questions
    ]

def display_questions(questions):
    """Display all questions in the quiz with improved UI"""
    for i, (question, options, _, hint, explanation) in enumerate(questions, 1):
        with st.container():
            st.markdown(f"""
                <div class="question-card">
                    <h3>Question {i}</h3>
                    <p>{question}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Use columns to make radio buttons more compact and visually appealing
            cols = st.columns(2)
            
            with cols[0]:
                answer_a = st.radio(
                    "A) " + options['a'],
                    [True, False],
                    key=f"question_{i}_a",
                    label_visibility="visible"
                )
            
            with cols[1]:
                answer_b = st.radio(
                    "B) " + options['b'], 
                    [True, False],
                    key=f"question_{i}_b",
                    label_visibility="visible"
                )
            
            cols = st.columns(2)
            
            with cols[0]:
                answer_c = st.radio(
                    "C) " + options['c'], 
                    [True, False],
                    key=f"question_{i}_c",
                    label_visibility="visible"
                )
            
            with cols[1]:
                answer_d = st.radio(
                    "D) " + options['d'], 
                    [True, False],
                    key=f"question_{i}_d",
                    label_visibility="visible"
                )
            
            # Hint and Explanation toggle
            with st.expander("💡 Need a Hint?"):
                st.markdown(f"""
                    <div class="hint-box">
                        <strong>Hint:</strong> {hint}
                        <br><br>
                        <strong>Explanation:</strong> {explanation}
                    </div>
                """, unsafe_allow_html=True)

def evaluate_answers(questions):
    """Evaluate user answers and calculate score"""
    score = 0
    total_questions = len(questions)
    user_answers = []
    correct_answers = []
    detailed_feedback = []
    
    for i, (question, options, correct_answer, _, explanation) in enumerate(questions, 1):
        # Find the selected answer by determining which radio button is True
        selected_keys = [key for key in ['a', 'b', 'c', 'd'] if st.session_state[f"question_{i}_{key}"]]
        
        if selected_keys:
            selected_key = selected_keys[0]
            user_answers.append(selected_key)
            correct_answers.append(correct_answer)
            
            if selected_key == correct_answer:
                score += 1
                detailed_feedback.append({
                    "status": "correct",
                    "question": question,
                    "your_answer": options[selected_key],
                    "explanation": explanation
                })
            else:
                detailed_feedback.append({
                    "status": "incorrect",
                    "question": question,
                    "your_answer": options[selected_key],
                    "correct_answer": options[correct_answer],
                    "explanation": explanation
                })
    
    return score, total_questions, user_answers, correct_answers, detailed_feedback

def display_performance_chart(score_history):
    """Display performance history chart with enhanced styling"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(range(1, len(score_history) + 1)),
        y=score_history,
        mode='lines+markers',
        name='Score History',
        line=dict(color='#10B981', width=3),
        marker=dict(size=12, color='#3B82F6', line=dict(width=2, color='#60A5FA'))
    ))
    
    fig.update_layout(
        title='Your Performance in Ratio Analysis Quiz',
        xaxis_title='Attempt Number',
        yaxis_title='Score',
        plot_bgcolor='#1E293B',
        paper_bgcolor='#0F172A',
        font=dict(color='#E2E8F0'),
        title_font_size=20,
        title_x=0.5,
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_detailed_feedback(detailed_feedback):
    """Display detailed feedback for each question"""
    st.markdown("## 🔍 Detailed Quiz Breakdown")
    
    for i, feedback in enumerate(detailed_feedback, 1):
        if feedback['status'] == 'correct':
            # Correct answer card
            st.markdown(f"""
                <div class="feedback-card" style="border-left: 4px solid #10B981; color: #10B981;">
                    <h4>Question {i}: ✅ Correct!</h4>
                    <p><strong>Your Answer:</strong> {feedback['your_answer']}</p>
                    <p><strong>Explanation:</strong> {feedback['explanation']}</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Incorrect answer card
            st.markdown(f"""
                <div class="feedback-card" style="border-left: 4px solid #EF4444; color: #EF4444;">
                    <h4>Question {i}: ❌ Incorrect</h4>
                    <p><strong>Your Answer:</strong> {feedback['your_answer']}</p>
                    <p><strong>Correct Answer:</strong> {feedback['correct_answer']}</p>
                    <p><strong>Explanation:</strong> {feedback['explanation']}</p>
                </div>
            """, unsafe_allow_html=True)

def mainy():
    """Main Streamlit application function"""
    # Initialize or load score history
    if 'score_history' not in st.session_state:
        st.session_state.score_history = []

    # Set up page configuration


    # Apply custom styling
    apply_custom_styling()

    # Main title and description
    st.title("🧮 Ratio Analysis Quiz")
    st.markdown("""
        Test your knowledge of financial ratio analysis! 
        Answer the questions and get detailed feedback on your performance.
    """)

    # Start Quiz Button
    if st.button("🚀 Start Quiz", key="start_quiz"):
        # Generate questions
        questions = generate_questions()
        
        # Store questions in session state
        st.session_state.questions = questions
        st.session_state.quiz_started = True
    
    # Quiz Logic
    if st.session_state.get('quiz_started', False):
        with st.form(key='quiz_form'):
            # Display questions
            display_questions(st.session_state.questions)
            
            # Submit button
            submit_button = st.form_submit_button("Submit Answers")
        
        if submit_button:
            # Evaluate answers
            score, total_questions, user_answers, correct_answers, detailed_feedback = evaluate_answers(st.session_state.questions)
            
            # Update score history
            st.session_state.score_history.append(score)
            
            # Display performance metrics
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Performance Chart
                display_performance_chart(st.session_state.score_history)
            
            with col2:
                # Score Card
                st.markdown(f"""
                    <div class="score-card">
                        <h2>🏆 Your Score</h2>
                        <h1 style="color: #10B981; font-size: 3em;">{score}/{total_questions}</h1>
                        <div class="progress-bar" style="width: {(score/total_questions)*100}%"></div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Detailed Feedback
            display_detailed_feedback(detailed_feedback)
            
            # Perfect Score Celebration
            if score == total_questions:
                display_celebration()
            
            # Reset quiz started state
            st.session_state.quiz_started = False

def run():
    """Configure and run the Streamlit application"""
    # Configure Gemini API (replace with your actual API key management)
    genai.configure(api_key=GENAI_API_KEY)
    
    # Run the main application
    mainy()

if __name__ == "__main__":
    run()
