import streamlit as st
from utils.auth import get_current_user
from utils.ui_components import render_page_header
from services.learning_service import ask_learning_tutor, generate_quiz_questions, generate_coding_exercise

def render_learning_assistant():
    """Renders AI Tutor, interactive concept explanations, quizzes, and coding challenges."""
    user = get_current_user()
    if not user:
        return

    render_page_header(
        title="📚 AI Learning Assistant & Tutor",
        subtitle="Master programming languages, web frameworks, algorithms, and system design with interactive AI tutoring.",
        badge="Adaptive AI Tutor"
    )

    tutor_tab, quiz_tab, coding_tab = st.tabs(["💡 AI Concept Tutor", "📝 Interactive Quizzes", "💻 Coding Exercises"])

    # 1. AI Concept Tutor Tab
    with tutor_tab:
        st.markdown("### Ask Your AI Tutor")
        c_top1, c_top2 = st.columns([3, 1])
        with c_top1:
            subject = st.selectbox("Subject / Technology", [
                "Python", "Django", "Django REST Framework", "JavaScript", "React",
                "SQL & Databases", "Data Structures & Algorithms", "System Design",
                "Docker & Kubernetes", "Machine Learning & AI", "Other Custom Subject"
            ])
        with c_top2:
            difficulty = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced"])

        question = st.text_area("What concept would you like explained or explored?", placeholder="e.g. How does Django ORM query optimization with select_related vs prefetch_related work?", height=100)

        if st.button("🚀 Explain with Code & Examples", type="primary"):
            if not question:
                st.error("Please enter a question or topic.")
            else:
                with st.spinner("Generating pedagogical explanation with code examples..."):
                    answer = ask_learning_tutor(subject, question, difficulty)
                    st.session_state['last_tutor_answer'] = answer

        if 'last_tutor_answer' in st.session_state:
            st.markdown("---")
            st.markdown(st.session_state['last_tutor_answer'])

    # 2. Interactive Quizzes Tab
    with quiz_tab:
        st.markdown("### Test Your Knowledge")
        q_col1, q_col2, q_col3 = st.columns([2, 1, 1])
        with q_col1:
            quiz_topic = st.text_input("Quiz Topic", value="Python & Django Fundamentals")
        with q_col2:
            quiz_diff = st.selectbox("Quiz Difficulty", ["Beginner", "Intermediate", "Advanced"], key="quiz_diff")
        with q_col3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            gen_quiz = st.button("Generate Quiz", type="primary", use_container_width=True)

        if gen_quiz:
            with st.spinner("Drafting quiz questions..."):
                quiz_data = generate_quiz_questions(quiz_topic, quiz_diff, count=3)
                if "error" in quiz_data:
                    st.error(quiz_data["error"])
                else:
                    st.session_state['active_quiz'] = quiz_data

        active_quiz = st.session_state.get('active_quiz')
        if active_quiz and active_quiz.get('questions'):
            st.markdown("---")
            st.markdown(f"#### Quiz on: **{active_quiz.get('topic')}** ({active_quiz.get('difficulty')})")
            
            for idx, q in enumerate(active_quiz['questions']):
                st.markdown(f"**Q{idx+1}: {q['question']}**")
                user_choice = st.radio(
                    f"Select your answer for Q{idx+1}:",
                    q['options'],
                    key=f"quiz_opt_{idx}"
                )
                
                if st.button(f"Submit Answer Q{idx+1}", key=f"btn_check_{idx}"):
                    correct_idx = q['correct_option_index']
                    chosen_idx = q['options'].index(user_choice)
                    if chosen_idx == correct_idx:
                        st.success(f"🎉 Correct! {q.get('explanation', '')}")
                    else:
                        st.error(f"❌ Incorrect. The correct answer was: '{q['options'][correct_idx]}'. Explanation: {q.get('explanation', '')}")
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # 3. Coding Challenges Tab
    with coding_tab:
        st.markdown("### Practical Coding Challenges")
        code_topic = st.text_input("Challenge Topic", value="Data Structures & Algorithms")
        code_diff = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"], key="code_diff_sel")

        if st.button("Generate Coding Problem", type="primary"):
            with st.spinner("Generating challenge problem..."):
                challenge = generate_coding_exercise(code_topic, code_diff)
                if "error" in challenge:
                    st.error(challenge["error"])
                else:
                    st.session_state['active_coding_challenge'] = challenge

        challenge = st.session_state.get('active_coding_challenge')
        if challenge:
            st.markdown("---")
            st.markdown(f"### 💻 {challenge.get('title', 'Coding Challenge')}")
            st.markdown(f"**Difficulty:** `{challenge.get('difficulty')}`")
            prob_stmt = challenge.get('problem_statement', '')
            st.markdown(f"**Problem Statement:**\n{prob_stmt}")

            if challenge.get('examples'):
                st.markdown("#### Examples")
                for ex in challenge['examples']:
                    st.code(f"Input: {ex.get('input')}\nOutput: {ex.get('output')}")

            st.markdown("#### Starter Code")
            st.code(challenge.get('starter_code', ''), language='python')

            with st.expander("💡 View Hints"):
                for h in challenge.get('hints', []):
                    st.markdown(f"- {h}")

            with st.expander("🔍 View Solution & Detailed Explanation"):
                st.code(challenge.get('solution_code', ''), language='python')
                st.markdown(f"**Explanation:** {challenge.get('explanation', '')}")
