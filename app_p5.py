import streamlit as st
import json
from google import genai
from google.genai import types


# ==================================================
# GEMINI API SETUP
# ==================================================

API_KEY = "AQ.Ab8RN6Lll0T0duRKA3OtH-DkoF4kjbrNNlcBNkdbIiN73N0gNQ"  # Replace with your actual API key

client = genai.Client(
    api_key=API_KEY
)

MODEL_NAME = "gemini-3.6-flash"


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Navya GPT - Study Buddy",
    page_icon="📚",
    layout="centered"
)


# ==================================================
# SESSION STATE
# ==================================================

if "stage" not in st.session_state:
    st.session_state.stage = "topic_input"

if "topic" not in st.session_state:
    st.session_state.topic = ""

if "overview" not in st.session_state:
    st.session_state.overview = ""

if "quiz" not in st.session_state:
    st.session_state.quiz = []

if "score" not in st.session_state:
    st.session_state.score = 0

if "results" not in st.session_state:
    st.session_state.results = []


# ==================================================
# RESET FUNCTION
# ==================================================

def reset_study_buddy():

    st.session_state.stage = "topic_input"

    st.session_state.topic = ""

    st.session_state.overview = ""

    st.session_state.quiz = []

    st.session_state.score = 0

    st.session_state.results = []


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.title("📚 Navya Study Buddy")

    st.write(
        "Study → Practice → Check your score"
    )

    st.divider()

    if st.button(
        "🔄 Reset Study Buddy",
        use_container_width=True
    ):

        reset_study_buddy()

        st.rerun()


# ==================================================
# TITLE
# ==================================================

st.title("📚 Navya GPT Study Buddy")

st.caption(
    "Learn a topic, take a 3-question quiz, "
    "and check your score."
)


# ==================================================
# GEMINI QUIZ GENERATION
# ==================================================

def generate_study_material(topic):

    prompt = f"""
You are an expert educational tutor.

Create study material for this topic:

TOPIC:
{topic}

Your response MUST contain:

1. A concept overview of exactly two useful paragraphs.
2. Exactly 3 multiple-choice questions.
3. Each question must have exactly 4 options.
4. Each question must have one correct answer.
5. Include a short explanation/rationale for the correct answer.

The quiz should test understanding rather than memorization.

Return ONLY valid JSON.

Do not use markdown.
Do not use ```json.
Do not add any text outside the JSON.

Required JSON structure:

{{
    "overview": "Two-paragraph explanation",
    "quiz": [
        {{
            "question": "Question 1",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer": "Option A",
            "explanation": "Why this answer is correct."
        }},
        {{
            "question": "Question 2",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer": "Option B",
            "explanation": "Why this answer is correct."
        }},
        {{
            "question": "Question 3",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer": "Option C",
            "explanation": "Why this answer is correct."
        }}
    ]
}}
"""


    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=prompt,

            config=types.GenerateContentConfig(

                response_mime_type="application/json"
            )
        )


        data = json.loads(
            response.text
        )


        return data


    except Exception as e:

        st.error(
            "❌ Could not generate the study material."
        )

        st.code(
            str(e)
        )

        return None


# ==================================================
# STAGE 1
# topic_input
# ==================================================

if st.session_state.stage == "topic_input":

    st.header("🎯 Stage 1: Choose a Topic")

    st.write(
        "Enter any topic you want to study."
    )

    topic = st.text_input(
        "Topic",
        placeholder="Example: TCP vs UDP"
    )


    if st.button(
        "📖 Start Learning",
        type="primary",
        use_container_width=True
    ):

        if not topic.strip():

            st.warning(
                "Please enter a topic first."
            )

        else:

            with st.spinner(
                "🤖 Creating your study material..."
            ):

                material = generate_study_material(
                    topic.strip()
                )


            if material:

                st.session_state.topic = (
                    topic.strip()
                )

                st.session_state.overview = (
                    material["overview"]
                )

                st.session_state.quiz = (
                    material["quiz"]
                )

                st.session_state.stage = (
                    "quiz_active"
                )

                st.rerun()


# ==================================================
# STAGE 2
# quiz_active
# ==================================================

elif st.session_state.stage == "quiz_active":

    st.header(
        "📖 Stage 2: Learn & Practice"
    )

    st.subheader(
        f"Topic: {st.session_state.topic}"
    )


    # ----------------------------------------------
    # CONCEPT OVERVIEW
    # ----------------------------------------------

    st.markdown(
        "### 📚 Concept Overview"
    )

    st.write(
        st.session_state.overview
    )


    st.divider()


    # ----------------------------------------------
    # QUIZ
    # ----------------------------------------------

    st.markdown(
        "### 📝 3-Question Quiz"
    )

    st.write(
        "Choose one answer for each question."
    )


    with st.form(
        "quiz_form"
    ):

        selected_answers = []


        for index, question in enumerate(
            st.session_state.quiz
        ):

            st.markdown(
                f"### Question {index + 1}"
            )

            st.write(
                question["question"]
            )


            answer = st.radio(

                "Choose your answer:",

                question["options"],

                key=f"question_{index}",

                index=None
            )


            selected_answers.append(
                answer
            )


            st.divider()


        submitted = st.form_submit_button(

            "✅ Submit Quiz",

            use_container_width=True
        )


    if submitted:

        # ------------------------------------------
        # CHECK WHETHER ALL QUESTIONS ARE ANSWERED
        # ------------------------------------------

        unanswered = any(
            answer is None
            for answer in selected_answers
        )


        if unanswered:

            st.warning(
                "⚠️ Please answer all 3 questions."
            )

        else:

            score = 0

            results = []


            # --------------------------------------
            # GRADING
            # --------------------------------------

            for index, question in enumerate(
                st.session_state.quiz
            ):

                selected = (
                    selected_answers[index]
                )

                correct = (
                    question["answer"]
                )

                is_correct = (
                    selected == correct
                )


                if is_correct:

                    score += 1


                results.append({

                    "question":
                        question["question"],

                    "selected":
                        selected,

                    "correct":
                        correct,

                    "is_correct":
                        is_correct,

                    "explanation":
                        question["explanation"]
                })


            st.session_state.score = score

            st.session_state.results = results

            st.session_state.stage = "graded"

            st.rerun()


# ==================================================
# STAGE 3
# graded
# ==================================================

elif st.session_state.stage == "graded":

    st.header(
        "🏆 Stage 3: Your Results"
    )

    st.subheader(
        f"Topic: {st.session_state.topic}"
    )


    # ==================================================
    # SCORE
    # ==================================================

    score = st.session_state.score

    total = len(
        st.session_state.quiz
    )


    st.metric(
        label="Final Score",
        value=f"{score}/{total}"
    )


    # ==================================================
    # PASS / FAIL
    # ==================================================

    if score >= 2:

        st.success(
            "🎉 PASS! Great job!"
        )

    else:

        st.error(
            "📚 KEEP PRACTICING! "
            "Review the explanations below."
        )


    st.divider()


    # ==================================================
    # DETAILED RESULTS
    # ==================================================

    st.subheader(
        "📋 Detailed Results"
    )


    for index, result in enumerate(
        st.session_state.results
    ):

        st.markdown(
            f"### Question {index + 1}"
        )


        st.write(
            result["question"]
        )


        if result["is_correct"]:

            st.success(
                "✅ Correct"
            )

            st.write(
                f"Your answer: "
                f"**{result['selected']}**"
            )

        else:

            st.error(
                "❌ Incorrect"
            )

            st.write(
                f"Your answer: "
                f"**{result['selected']}**"
            )

            st.write(
                f"Correct answer: "
                f"**{result['correct']}**"
            )


        st.info(
            "💡 Explanation: "
            + result["explanation"]
        )


        st.divider()


    # ==================================================
    # STUDY AGAIN
    # ==================================================

    if st.button(
        "🔄 Study Another Topic",
        type="primary",
        use_container_width=True
    ):

        reset_study_buddy()

        st.rerun()