import streamlit as st
import pandas as pd

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

QUESTIONS = [
    {
        "id": "Q1",
        "text": "List the names and GPAs of all students with GPA above 3.0.",
        "concepts": ["SELECT", "WHERE"],
        "topic": "filtering",
        "difficulty": "easy"
    },
    {
        "id": "Q2",
        "text": "Show all columns for students whose major is 'CS'.",
        "concepts": ["SELECT", "WHERE"],
        "topic": "filtering",
        "difficulty": "easy"
    },
    {
        "id": "Q3",
        "text": "List each student's name together with the titles of the courses they are enrolled in.",
        "concepts": ["SELECT", "JOIN"],
        "topic": "joins",
        "difficulty": "medium"
    },
    {
        "id": "Q4",
        "text": "For each major, show the average GPA of students in that major.",
        "concepts": ["SELECT", "GROUP BY", "AGGREGATION"],
        "topic": "grouping",
        "difficulty": "medium"
    },
    {
        "id": "Q5",
        "text": "Show only those majors where the average GPA is at least 3.0.",
        "concepts": ["SELECT", "GROUP BY", "AGGREGATION", "HAVING"],
        "topic": "grouping",
        "difficulty": "hard"
    },
    {
        "id": "Q6",
        "text": "List students whose GPA is above the overall average GPA.",
        "concepts": ["SELECT", "WHERE", "SUBQUERY", "AGGREGATION"],
        "topic": "subqueries",
        "difficulty": "hard"
    }
]

STUDENT_ANSWERS = {
    "Alice": {
        "Q1": True,
        "Q2": True,
        "Q3": False,
        "Q4": False,
        "Q5": False,
        "Q6": False,
    },
    "Bob": {
        "Q1": True,
        "Q2": False,
        "Q3": True,
        "Q4": True,
        "Q5": False,
        "Q6": False,
    },
    "Charlie": {
        "Q1": False,
        "Q2": False,
        "Q3": True,
        "Q4": True,
        "Q5": True,
        "Q6": True,
    }
}

# ============================
# Helper functions
# ============================

def get_question_by_id(qid):
    for q in QUESTIONS:
        if q["id"] == qid:
            return q
    return None


def compute_concept_stats_for_student(student_name):
    if student_name not in STUDENT_ANSWERS:
        raise ValueError(f"Unknown student: {student_name}")

    stats = {
        concept: {"seen": 0, "correct": 0, "mastery": None}
        for concept in CONCEPTS
    }

    answers = STUDENT_ANSWERS[student_name]
    for qid, is_correct in answers.items():
        q = get_question_by_id(qid)
        if q is None:
            continue
        for concept in q["concepts"]:
            stats[concept]["seen"] += 1
            if is_correct:
                stats[concept]["correct"] += 1

    for concept, data in stats.items():
        if data["seen"] > 0:
            data["mastery"] = 100.0 * data["correct"] / data["seen"]
        else:
            data["mastery"] = None

    return stats


def categorize_mastery_level(mastery_percent):
    if mastery_percent is None:
        return "No data"
    if mastery_percent >= 80:
        return "Strong"
    elif mastery_percent >= 50:
        return "Okay"
    else:
        return "Needs improvement"


def generate_feedback_for_student(student_name):
    stats = compute_concept_stats_for_student(student_name)

    strong_concepts = []
    ok_concepts = []
    weak_concepts = []

    for concept, data in stats.items():
        m = data["mastery"]
        level = categorize_mastery_level(m)
        if level == "Strong":
            strong_concepts.append(concept)
        elif level == "Okay":
            ok_concepts.append(concept)
        elif level == "Needs improvement":
            weak_concepts.append(concept)

    lines = []
    lines.append(f"Concept-level feedback for {student_name}:\n")

    def list_or_na(items):
        return ", ".join(items) if items else "None"

    lines.append(f"✅ Strong in: {list_or_na(strong_concepts)}")
    lines.append(f"➖ Okay in:   {list_or_na(ok_concepts)}")
    lines.append(f"⚠️ Needs improvement in: {list_or_na(weak_concepts)}\n")

    if weak_concepts:
        lines.append("Recommended focus areas:")
        for c in weak_concepts:
            if c == "JOIN":
                lines.append("- Practice JOINs between multiple tables and understand foreign keys.")
            elif c == "GROUP BY":
                lines.append("- Work on GROUP BY with aggregation (SUM, AVG, COUNT).")
            elif c == "WHERE":
                lines.append("- Review basic filtering conditions and logical operators.")
            elif c == "AGGREGATION":
                lines.append("- Review AVG, COUNT, MIN, MAX, and how they relate to GROUP BY.")
            elif c == "HAVING":
                lines.append("- Understand how HAVING filters groups after aggregation.")
            elif c == "SUBQUERY":
                lines.append("- Practice writing subqueries inside WHERE or FROM.")
            elif c == "SELECT":
                lines.append("- Review basic SELECT syntax and choosing appropriate columns.")
    else:
        lines.append("Overall, this student has a solid grasp of the tested concepts.")

    return "\n".join(lines)


def build_stats_dataframe(stats):
    rows = []
    for concept, data in stats.items():
        mastery = data["mastery"]
        if mastery is None:
            mastery_str = None
        else:
            mastery_str = round(mastery, 1)
        level = categorize_mastery_level(mastery)
        rows.append({
            "Concept": concept,
            "Seen": data["seen"],
            "Correct": data["correct"],
            "Mastery (%)": mastery_str,
            "Level": level
        })
    df = pd.DataFrame(rows)
    return df


# ============================
# Streamlit UI
# ============================

st.set_page_config(page_title="SQL Concept Tutor", layout="centered")

st.title("🧠 SQL Concept Tutor")
st.write("Analyze student SQL performance at the **concept** level (SELECT, WHERE, JOIN, etc.).")

# Sidebar: select student
st.sidebar.header("Student selection")
selected_student = st.sidebar.selectbox(
    "Choose a student",
    options=list(STUDENT_ANSWERS.keys())
)

st.sidebar.write("Tip: Try different students to see how their concept mastery changes.")

# Main section
st.subheader(f"Concept mastery for {selected_student}")

stats = compute_concept_stats_for_student(selected_student)
df_stats = build_stats_dataframe(stats)

st.table(df_stats)

st.subheader("Feedback")
feedback_text = generate_feedback_for_student(selected_student)
st.text(feedback_text)

#  question bank
with st.expander("Show question bank and concept tags"):
    for q in QUESTIONS:
        st.markdown(f"**{q['id']}** – {q['text']}")
        st.markdown(f"- Concepts: `{', '.join(q['concepts'])}`")
        st.markdown(f"- Topic: `{q['topic']}`, Difficulty: `{q['difficulty']}`")
        st.markdown("---")
