import streamlit as st
import pandas as pd
import random

# ============================
# SQL Concept Tutor - Data
# ============================

CONCEPTS = [
    "SELECT",
    "WHERE",
    "JOIN",
    "GROUP BY",
    "AGGREGATION",
    "HAVING",
    "SUBQUERY"
]

# Question bank with SQL answers + explanations
QUESTIONS = [
    {
        "id": "Q1",
        "text": "List the names and GPAs of all students with GPA above 3.0.",
        "concepts": ["SELECT", "WHERE"],
        "topic": "filtering",
        "difficulty": "easy",
        "answer_sql": "SELECT name, gpa FROM Students WHERE gpa > 3.0;",
        "explanation": "We select only the name and gpa columns and use WHERE gpa > 3.0 to filter rows."
    },
    {
        "id": "Q2",
        "text": "Show all columns for students whose major is 'CS'.",
        "concepts": ["SELECT", "WHERE"],
        "topic": "filtering",
        "difficulty": "easy",
        "answer_sql": "SELECT * FROM Students WHERE major = 'CS';",
        "explanation": "SELECT * returns all columns; WHERE major = 'CS' filters only CS majors."
    },
    {
        "id": "Q3",
        "text": "List each student's name together with the titles of the courses they are enrolled in.",
        "concepts": ["SELECT", "JOIN"],
        "topic": "joins",
        "difficulty": "medium",
        "answer_sql": """
SELECT s.name, c.title
FROM Students s
JOIN Enrollments e ON s.id = e.student_id
JOIN Courses c ON e.course_id = c.id;
""",
        "explanation": "We join Students → Enrollments → Courses and pick the student name with the course title."
    },
    {
        "id": "Q4",
        "text": "For each major, show the average GPA of students in that major.",
        "concepts": ["SELECT", "GROUP BY", "AGGREGATION"],
        "topic": "grouping",
        "difficulty": "medium",
        "answer_sql": """
SELECT major, AVG(gpa) AS avg_gpa
FROM Students
GROUP BY major;
""",
        "explanation": "GROUP BY major groups rows by major; AVG(gpa) computes the average GPA for each group."
    },
    {
        "id": "Q5",
        "text": "Show only those majors where the average GPA is at least 3.0.",
        "concepts": ["SELECT", "GROUP BY", "AGGREGATION", "HAVING"],
        "topic": "grouping",
        "difficulty": "hard",
        "answer_sql": """
SELECT major, AVG(gpa) AS avg_gpa
FROM Students
GROUP BY major
HAVING AVG(gpa) >= 3.0;
""",
        "explanation": "HAVING filters groups after aggregation, keeping only majors with avg GPA >= 3.0."
    },
    {
        "id": "Q6",
        "text": "List students whose GPA is above the overall average GPA.",
        "concepts": ["SELECT", "WHERE", "SUBQUERY", "AGGREGATION"],
        "topic": "subqueries",
        "difficulty": "hard",
        "answer_sql": """
SELECT name, gpa
FROM Students
WHERE gpa > (SELECT AVG(gpa) FROM Students);
""",
        "explanation": "The subquery finds the overall average GPA; the outer query keeps students above that number."
    }
]

# ============================
# Session state initialization
# ============================

# Concept stats for "You" (this browser session)
if "concept_stats" not in st.session_state:
    st.session_state.concept_stats = {
        concept: {"seen": 0, "correct": 0, "mastery": None}
        for concept in CONCEPTS
    }

# Track current question id
if "current_qid" not in st.session_state:
    st.session_state.current_qid = None

# Track whether solution is revealed
if "show_solution" not in st.session_state:
    st.session_state.show_solution = False

# Track user's last typed answer (just to keep text box filled)
if "user_answer" not in st.session_state:
    st.session_state.user_answer = ""

# ============================
# Helper functions
# ============================

def get_question_by_id(qid):
    for q in QUESTIONS:
        if q["id"] == qid:
            return q
    return None


def pick_random_question(difficulty_filter, topic_filter):
    """Pick a random question that matches the filters."""
    candidates = [
        q for q in QUESTIONS
        if (difficulty_filter == "All" or q["difficulty"] == difficulty_filter)
        and (topic_filter == "All" or q["topic"] == topic_filter)
    ]
    if not candidates:
        return None
    return random.choice(candidates)


def update_concept_stats_for_question(question, was_correct):
    """Update the session concept stats based on the student's self-evaluation."""
    stats = st.session_state.concept_stats
    for c in question["concepts"]:
        stats[c]["seen"] += 1
        if was_correct:
            stats[c]["correct"] += 1

    # Recompute mastery
    for concept, data in stats.items():
        if data["seen"] > 0:
            data["mastery"] = 100.0 * data["correct"] / data["seen"]
        else:
            data["mastery"] = None


def categorize_mastery_level(mastery_percent):
    if mastery_percent is None:
        return "No data"
    if mastery_percent >= 80:
        return "Strong"
    elif mastery_percent >= 50:
        return "Okay"
    else:
        return "Needs improvement"


def build_stats_dataframe():
    rows = []
    stats = st.session_state.concept_stats
    for concept, data in stats.items():
        m = data["mastery"]
        if m is None:
            mastery_str = None
        else:
            mastery_str = round(m, 1)
        level = categorize_mastery_level(m)
        rows.append(
            {
                "Concept": concept,
                "Seen": data["seen"],
                "Correct": data["correct"],
                "Mastery (%)": mastery_str,
                "Level": level,
            }
        )
    return pd.DataFrame(rows)


# ============================
# Streamlit UI
# ============================

st.set_page_config(page_title="SQL Concept Tutor", layout="centered")

st.title("🧠 SQL Concept Tutor")
st.write(
    "Practice SQL questions and track your understanding of key concepts like "
    "`SELECT`, `WHERE`, `JOIN`, `GROUP BY`, and `SUBQUERY`."
)

# ---------- Sidebar: filters & controls ----------

st.sidebar.header("Practice settings")

difficulty_options = ["All"] + sorted({q["difficulty"] for q in QUESTIONS})
topic_options = ["All"] + sorted({q["topic"] for q in QUESTIONS})

difficulty_filter = st.sidebar.selectbox("Difficulty", difficulty_options, index=0)
topic_filter = st.sidebar.selectbox("Topic", topic_options, index=0)

if st.sidebar.button("New question"):
    q = pick_random_question(difficulty_filter, topic_filter)
    st.session_state.current_qid = q["id"] if q else None
    st.session_state.show_solution = False
    st.session_state.user_answer = ""

if st.sidebar.button("Reset progress"):
    st.session_state.concept_stats = {
        concept: {"seen": 0, "correct": 0, "mastery": None}
        for concept in CONCEPTS
    }

# ---------- Progress section ----------

st.subheader("Your concept progress (this session)")
df_stats = build_stats_dataframe()
st.table(df_stats)

st.markdown(
    "_Tip: As you mark questions correct/incorrect, this table updates to show "
    "which SQL concepts you are strong in and which need more practice._"
)

st.markdown("---")

# ---------- Current question section ----------

st.subheader("Current question")

# If no question yet, automatically pick one on first load
if st.session_state.current_qid is None:
    q = pick_random_question(difficulty_filter, topic_filter)
    if q is not None:
        st.session_state.current_qid = q["id"]

qid = st.session_state.current_qid
question = get_question_by_id(qid) if qid else None

if question is None:
    st.warning("No question available for the selected filters. Try changing difficulty/topic.")
else:
    st.markdown(f"**{question['id']} – {question['text']}**")
    st.markdown(f"- **Difficulty:** `{question['difficulty']}`")
    st.markdown(f"- **Topic:** `{question['topic']}`")
    st.markdown(f"- **Concepts:** `{', '.join(question['concepts'])}`")

    st.markdown("### Your SQL answer (type here)")
    st.session_state.user_answer = st.text_area(
        "Write your SQL answer here (this is just for you; the app does not auto-grade).",
        value=st.session_state.user_answer,
        height=120,
        label_visibility="collapsed"
    )

    # Buttons for showing solution and self-evaluation
    cols = st.columns(3)
    with cols[0]:
        if st.button("Show solution / explanation"):
            st.session_state.show_solution = True
    with cols[1]:
        if st.button("I was correct"):
            update_concept_stats_for_question(question, was_correct=True)
            st.success("Nice! Marked as correct and progress updated.")
    with cols[2]:
        if st.button("I was wrong"):
            update_concept_stats_for_question(question, was_correct=False)
            st.info("Marked as incorrect and progress updated. Keep practicing!")

    if st.session_state.show_solution:
        st.markdown("### Suggested SQL solution")
        st.code(question["answer_sql"], language="sql")

        st.markdown("### Explanation")
        st.write(question["explanation"])

st.markdown("---")

with st.expander("Show full question bank"):
    for q in QUESTIONS:
        st.markdown(f"**{q['id']}** – {q['text']}")
        st.markdown(f"- Concepts: `{', '.join(q['concepts'])}`")
        st.markdown(f"- Topic: `{q['topic']}`, Difficulty: `{q['difficulty']}`")
        st.markdown("---")
