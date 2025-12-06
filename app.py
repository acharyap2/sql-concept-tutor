import streamlit as st

# ============================
#  VET CLINIC SCHEMA (FROM CLASS)
# ============================

SCHEMA_TEXT = """
-- All questions use this veterinary clinic database:

TABLE owners(
    owner_id        VARCHAR2(10) PRIMARY KEY,
    first_name      VARCHAR2(20),
    last_name       VARCHAR2(20),
    street_address  VARCHAR2(50),
    city            VARCHAR2(50),
    state_abbre     VARCHAR2(2),
    state           VARCHAR2(20),
    zipcode         INT
);

TABLE pets(
    pet_id      VARCHAR2(10) PRIMARY KEY,
    name        VARCHAR2(20),
    kind        VARCHAR2(20),
    gender      VARCHAR2(20),
    age         INT,
    owner_id    VARCHAR2(20),
    FOREIGN KEY(owner_id) REFERENCES owners
);

TABLE procedure_details(
    procedure_type     VARCHAR2(20),
    procedure_subcode  INT,
    description        VARCHAR2(50),
    price              INT,
    PRIMARY KEY (procedure_type, procedure_subcode)
);

TABLE procedure_history(
    pet_id            VARCHAR2(10),
    procedure_date    DATE,
    procedure_type    VARCHAR2(20),
    procedure_subcode INT,
    PRIMARY KEY (pet_id, procedure_date),
    FOREIGN KEY(procedure_type, procedure_subcode) REFERENCES procedure_details,
    FOREIGN KEY(pet_id) REFERENCES pets
);
"""

# ============================
#  LEVEL DEFINITIONS (1–15)
# ============================
# Each level has:
# - question, answer_sql, explanation
# - required_tables: list of lowercase table names that should appear
# - required_keywords: list of lowercase SQL fragments to look for
# - forbidden_keywords: list of patterns to warn about (e.g., "select *")

LEVELS = [
    {
        "level": 1,
        "title": "List all owners",
        "question": "List all owners, showing owner_id, first_name, last_name, and city.",
        "answer_sql": """
SELECT owner_id, first_name, last_name, city
FROM owners;
""",
        "explanation": "Basic SELECT from the owners table with four columns.",
        "required_tables": ["owners"],
        "required_keywords": [],
        "forbidden_keywords": ["select *"]
    },
    {
        "level": 2,
        "title": "Filter older pets",
        "question": "List the name, kind, and age of all pets that are older than 5 years.",
        "answer_sql": """
SELECT name, kind, age
FROM pets
WHERE age > 5;
""",
        "explanation": "We use a WHERE clause on age > 5 in the pets table.",
        "required_tables": ["pets"],
        "required_keywords": ["where"],
        "forbidden_keywords": ["select *"]
    },
    {
        "level": 3,
        "title": "Owners and their pets",
        "question": "List each owner's first_name, last_name, and the name of each pet they own.",
        "answer_sql": """
SELECT o.first_name, o.last_name, p.name AS pet_name
FROM owners o
JOIN pets p ON o.owner_id = p.owner_id;
""",
        "explanation": "We join owners and pets on owner_id so we can show owner and pet together.",
        "required_tables": ["owners", "pets"],
        "required_keywords": ["join"],
        "forbidden_keywords": []
    },
    {
        "level": 4,
        "title": "Count pets per owner",
        "question": "For each owner, show owner_id and the number of pets they own.",
        "answer_sql": """
SELECT owner_id, COUNT(*) AS nr_pets
FROM pets
GROUP BY owner_id;
""",
        "explanation": "GROUP BY owner_id groups rows per owner; COUNT(*) counts how many pets they have.",
        "required_tables": ["pets"],
        "required_keywords": ["group by", "count("],
        "forbidden_keywords": []
    },
    {
        "level": 5,
        "title": "Owners with more than one pet",
        "question": "Show owner_id values for owners who have more than one pet.",
        "answer_sql": """
SELECT owner_id
FROM pets
GROUP BY owner_id
HAVING COUNT(*) > 1;
""",
        "explanation": "Use HAVING COUNT(*) > 1 to keep only owners with more than one pet.",
        "required_tables": ["pets"],
        "required_keywords": ["group by", "having", "count("],
        "forbidden_keywords": []
    },
    {
        "level": 6,
        "title": "Procedures above a price threshold",
        "question": "List procedure_type, procedure_subcode, and price for all procedures that cost more than 500, ordered by price descending.",
        "answer_sql": """
SELECT procedure_type, procedure_subcode, price
FROM procedure_details
WHERE price > 500
ORDER BY price DESC;
""",
        "explanation": "We filter by price > 500 and ORDER BY price DESC to show most expensive first.",
        "required_tables": ["procedure_details"],
        "required_keywords": ["where", "order by"],
        "forbidden_keywords": []
    },
    {
        "level": 7,
        "title": "Number of subcodes per procedure type",
        "question": "For each procedure_type, report the number of subcodes it has, naming the calculated column nr_subcodes, ordered from most subcodes to fewest.",
        "answer_sql": """
SELECT procedure_type,
       COUNT(procedure_subcode) AS nr_subcodes
FROM procedure_details
GROUP BY procedure_type
ORDER BY nr_subcodes DESC;
""",
        "explanation": "We group by procedure_type and count subcodes, then order by the count descending.",
        "required_tables": ["procedure_details"],
        "required_keywords": ["group by", "count(", "order by"],
        "forbidden_keywords": []
    },
    {
        "level": 8,
        "title": "Most expensive procedure(s)",
        "question": "Find the procedure_type, procedure_subcode, and price of the most expensive procedure(s).",
        "answer_sql": """
SELECT procedure_type, procedure_subcode, price
FROM procedure_details
WHERE price = (
    SELECT MAX(price)
    FROM procedure_details
);
""",
        "explanation": "A subquery finds the maximum price; the outer query returns all procedures with that price.",
        "required_tables": ["procedure_details"],
        "required_keywords": ["where", "max("],
        "forbidden_keywords": []
    },
    {
        "level": 9,
        "title": "Owners with at least 2 different pets with care",
        "question": (
            "Report owner_id, first_name, last_name, and the number of different pets (nr_of_pets) for each owner who has "
            "at least 2 different pets that received pet care services. Count each pet only once per owner."
        ),
        "answer_sql": """
SELECT o.owner_id,
       o.first_name,
       o.last_name,
       COUNT(DISTINCT h.pet_id) AS nr_of_pets
FROM owners o
JOIN pets p ON o.owner_id = p.owner_id
JOIN procedure_history h ON p.pet_id = h.pet_id
GROUP BY o.owner_id, o.first_name, o.last_name
HAVING COUNT(DISTINCT h.pet_id) >= 2
ORDER BY nr_of_pets DESC;
""",
        "explanation": "We join owners → pets → procedure_history and use COUNT(DISTINCT h.pet_id) with HAVING to require at least 2 different pets.",
        "required_tables": ["owners", "pets", "procedure_history"],
        "required_keywords": ["join", "group by", "having", "count(distinct"],
        "forbidden_keywords": []
    },
    {
        "level": 10,
        "title": "Procedures that were never used",
        "question": "Report procedure_type and procedure_subcode of all procedures that have never been used in procedure_history. Use a correlated subquery with NOT EXISTS or COUNT(*).",
        "answer_sql": """
SELECT d.procedure_type, d.procedure_subcode
FROM procedure_details d
WHERE NOT EXISTS (
    SELECT 1
    FROM procedure_history h
    WHERE h.procedure_type = d.procedure_type
      AND h.procedure_subcode = d.procedure_subcode
);
""",
        "explanation": "For each procedure in procedure_details, we check that no matching rows exist in procedure_history using NOT EXISTS.",
        "required_tables": ["procedure_details", "procedure_history"],
        "required_keywords": ["where", "not exists"],
        "forbidden_keywords": []
    },
    {
        "level": 11,
        "title": "Total cost per pet",
        "question": "For each pet, show pet_id, name, and the total amount spent on that pet's procedures.",
        "answer_sql": """
SELECT p.pet_id,
       p.name,
       SUM(d.price) AS total_cost
FROM pets p
JOIN procedure_history h ON p.pet_id = h.pet_id
JOIN procedure_details d
    ON h.procedure_type = d.procedure_type
   AND h.procedure_subcode = d.procedure_subcode
GROUP BY p.pet_id, p.name;
""",
        "explanation": "We join pets → procedure_history → procedure_details, then group by pet to sum the price of all procedures.",
        "required_tables": ["pets", "procedure_history", "procedure_details"],
        "required_keywords": ["join", "group by", "sum("],
        "forbidden_keywords": []
    },
    {
        "level": 12,
        "title": "Total cost per owner",
        "question": "For each owner, show owner_id, first_name, last_name, and the total amount spent on all of their pets' procedures.",
        "answer_sql": """
SELECT o.owner_id,
       o.first_name,
       o.last_name,
       SUM(d.price) AS total_spent
FROM owners o
JOIN pets p ON o.owner_id = p.owner_id
JOIN procedure_history h ON p.pet_id = h.pet_id
JOIN procedure_details d
    ON h.procedure_type = d.procedure_type
   AND h.procedure_subcode = d.procedure_subcode
GROUP BY o.owner_id, o.first_name, o.last_name;
""",
        "explanation": "We join owners → pets → procedure_history → procedure_details and group by owner to sum all prices.",
        "required_tables": ["owners", "pets", "procedure_history", "procedure_details"],
        "required_keywords": ["join", "group by", "sum("],
        "forbidden_keywords": []
    },
    {
        "level": 13,
        "title": "Increase prices using CASE",
        "question": (
            "Write an UPDATE that increases the price of all procedures under 25 by 10%, "
            "and increases the price of all procedures that cost 25 or more by 5%. Use a single UPDATE with CASE."
        ),
        "answer_sql": """
UPDATE procedure_details
SET price = CASE
    WHEN price < 25 THEN price * 1.10
    ELSE price * 1.05
END;
""",
        "explanation": "We use CASE in the SET clause to apply different multipliers depending on the current price.",
        "required_tables": ["procedure_details"],
        "required_keywords": ["update", "set", "case"],
        "forbidden_keywords": []
    },
    {
        "level": 14,
        "title": "Delete history for pets starting with 'J'",
        "question": "Delete all procedure_history rows for pets whose names start with the letter 'J'. Use a subquery on pets.",
        "answer_sql": """
DELETE FROM procedure_history
WHERE pet_id IN (
    SELECT pet_id
    FROM pets
    WHERE UPPER(name) LIKE 'J%'
);
""",
        "explanation": "We find all pet_id values for pets whose name starts with 'J' in a subquery, then delete their history rows.",
        "required_tables": ["procedure_history", "pets"],
        "required_keywords": ["delete", "where", "in", "select"],
        "forbidden_keywords": []
    },
    {
        "level": 15,
        "title": "High-revenue procedure types",
        "question": (
            "For each procedure_type, show procedure_type and the total revenue "
            "from all procedures of that type, but only include procedure types where total revenue is at least 2000."
        ),
        "answer_sql": """
SELECT d.procedure_type,
       SUM(d.price) AS total_revenue
FROM procedure_history h
JOIN procedure_details d
    ON h.procedure_type = d.procedure_type
   AND h.procedure_subcode = d.procedure_subcode
GROUP BY d.procedure_type
HAVING SUM(d.price) >= 2000;
""",
        "explanation": "We join history with details, group by procedure_type, sum prices, and filter groups with HAVING.",
        "required_tables": ["procedure_history", "procedure_details"],
        "required_keywords": ["join", "group by", "having", "sum("],
        "forbidden_keywords": []
    },
]

# ============================
#  KEYWORD HINTS
# ============================

KEYWORD_HINTS = {
    "join": "This query probably needs at least one JOIN between the related tables.",
    "group by": "Because the question asks 'for each ...', you likely need GROUP BY.",
    "having": "To filter groups based on aggregates (like COUNT or SUM), use HAVING.",
    "distinct": "Use DISTINCT to avoid duplicate values in the result.",
    "order by": "Use ORDER BY to sort the results (for example, by price or by count).",
    "avg(": "Use AVG(...) to compute the average of a numeric column.",
    "sum(": "Use SUM(...) to add up numeric values (like total cost or revenue).",
    "count(": "Use COUNT(...) to count rows or distinct values.",
    "count(distinct": "COUNT(DISTINCT ...) is useful when each entity should be counted only once.",
    "where": "Use a WHERE clause to filter rows before grouping.",
    "not exists": "NOT EXISTS is useful to find rows that have no matching rows in another table.",
    "exists": "EXISTS can test whether related rows exist in another table.",
    "case": "The CASE expression lets you apply different logic in one statement (for example, different percentage increases).",
    "update": "Use UPDATE to modify existing rows in a table.",
    "delete": "Use DELETE FROM ... WHERE ... to remove rows from a table.",
    "in": "IN is handy for matching a value against a list or a subquery result.",
    "with": "WITH introduces a common table expression (CTE) that can be referenced in the main query.",
}

# ============================
#  ANALYSIS FUNCTION
# ============================

def analyze_answer(user_sql: str, level_info: dict) -> str:
    """
    Simple rule-based analysis:
      - Checks that required tables appear.
      - Checks that required keywords (JOIN, GROUP BY, etc.) appear.
      - Warns about forbidden patterns like SELECT *.
    Returns a feedback string.
    """
    if not user_sql or user_sql.strip() == "":
        return "Please type a SQL statement above before asking for hints."

    feedback_lines = []
    user_lower = user_sql.lower()

    # Check required tables
    missing_tables = []
    for table in level_info.get("required_tables", []):
        if table not in user_lower:
            missing_tables.append(table)

    if missing_tables:
        feedback_lines.append("🔍 **Tables you might be missing:**")
        for t in missing_tables:
            feedback_lines.append(f"- It looks like you might need to use the `{t}` table in this query.")
        feedback_lines.append("")

    # Check required keywords
    missing_keywords = []
    for kw in level_info.get("required_keywords", []):
        if kw not in user_lower:
            missing_keywords.append(kw)

    if missing_keywords:
        feedback_lines.append("🧠 **SQL features you might need:**")
        for kw in missing_keywords:
            hint = KEYWORD_HINTS.get(kw, f"You may need to use `{kw.upper()}` in this query.")
            feedback_lines.append(f"- {hint}")
        feedback_lines.append("")

    # Check forbidden patterns
    bad_patterns = []
    for bad in level_info.get("forbidden_keywords", []):
        if bad in user_lower:
            bad_patterns.append(bad)

    if bad_patterns:
        feedback_lines.append("⚠️ **Style / pattern warnings:**")
        for bad in bad_patterns:
            if bad == "select *":
                feedback_lines.append("- Try to avoid `SELECT *`. Select only the columns requested in the question.")
            else:
                feedback_lines.append(f"- Consider avoiding the pattern `{bad}` here.")
        feedback_lines.append("")

    # A tiny generic hint about HAVING without GROUP BY
    if "having" in user_lower and "group by" not in user_lower:
        feedback_lines.append("⚠️ You used HAVING but not GROUP BY. HAVING is normally used together with GROUP BY.")

    if not feedback_lines:
        feedback_lines.append("✅ Your statement contains the expected tables and main SQL features for this level.")
        feedback_lines.append("Now compare details (columns, conditions, grouping) with the model solution below.")

    return "\n".join(feedback_lines)

# ============================
#  STREAMLIT UI
# ============================

st.set_page_config(page_title="Rule-Based SQL Tutor – Vet Clinic", layout="centered")

st.title("🧠 Rule-Based AI-Like SQL Tutor (Vet Clinic DB)")
st.write(
    "Practice advanced SQL on the veterinary clinic database (joins, aggregates, "
    "subqueries, NOT EXISTS, CASE, UPDATE, DELETE). "
    "Type your answer, then click **Get Hints** to see what you might be missing."
)

st.markdown("## 📘 Relational Schema")
st.code(SCHEMA_TEXT, language="sql")

st.markdown("---")

# Sidebar: choose level
levels_available = [lvl["level"] for lvl in LEVELS]
default_level = 1

st.sidebar.header("Choose Level")
selected_level = st.sidebar.slider(
    "Level (1 = easiest, 15 = hardest)",
    min_value=min(levels_available),
    max_value=max(levels_available),
    value=default_level,
    step=1,
)

# Get level info
level_info = next((lvl for lvl in LEVELS if lvl["level"] == selected_level), None)

if level_info is None:
    st.error("Something went wrong: level not found.")
else:
    st.markdown(f"## ✅ Level {level_info['level']}: {level_info['title']}")
    st.markdown(f"**Question:** {level_info['question']}")

    st.markdown(
        "✏️ **Tip:** Try to write the query or statement yourself first. "
        "Then click **Get Hints** to see which tables or SQL features you might be missing."
    )

    # Text area for user's SQL
    user_sql = st.text_area(
        "Your SQL answer (not auto-graded, but analyzed for hints):",
        height=200,
    )

    if st.button("🔍 Get Hints"):
        feedback = analyze_answer(user_sql, level_info)
        st.markdown("### 💡 Hints / Feedback")
        st.write(feedback)

    with st.expander("✅ Show model solution and explanation"):
        st.markdown("**Suggested SQL solution:**")
        st.code(level_info["answer_sql"], language="sql")
        st.markdown("**Explanation:**")
        st.write(level_info["explanation"])

    if selected_level == max(levels_available):
        st.success(
            "🎉 You've reached Level 15 on the Vet Clinic database. "
            "If you understand these statements, you're in great shape for advanced SQL in this course!"
        )
