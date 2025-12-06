import streamlit as st

# ============================
# ✅ VET CLINIC SCHEMA (STATIC)
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
    owner_id    VARCHAR2(20)
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
    PRIMARY KEY (pet_id, procedure_date)
);
"""

# ============================
# ✅ LEVEL 1 → 15 QUESTIONS
# ============================

LEVELS = [
    {
        "level": 1,
        "title": "Basic pet filtering",
        "question": "List the names and ages of all pets that are older than 5 years.",
        "answer_sql": "SELECT name, age FROM pets WHERE age > 5;",
        "explanation": "Simple SELECT with a WHERE condition to filter rows by age."
    },
    {
        "level": 2,
        "title": "Sort owners by city and last name",
        "question": "List all owners (first_name, last_name, city, state_abbre) ordered by city, then by last_name.",
        "answer_sql": """
SELECT first_name, last_name, city, state_abbre
FROM owners
ORDER BY city, last_name;
""",
        "explanation": "ORDER BY supports multiple columns; it sorts by city first and, for ties, by last_name."
    },
    {
        "level": 3,
        "title": "Count pets per owner",
        "question": "For each owner, show owner_id and the total number of pets they own.",
        "answer_sql": """
SELECT owner_id, COUNT(*) AS pet_count
FROM pets
GROUP BY owner_id;
""",
        "explanation": "GROUP BY owner_id groups rows per owner, and COUNT(*) counts how many pets each owner has."
    },
    {
        "level": 4,
        "title": "List each owner and their pet names",
        "question": "Show each owner's first_name, last_name, and the name of each pet they own.",
        "answer_sql": """
SELECT o.first_name, o.last_name, p.name AS pet_name
FROM owners o
JOIN pets p ON o.owner_id = p.owner_id;
""",
        "explanation": "Inner join on owner_id connects owners with their pets so we can show owner and pet name together."
    },
    {
        "level": 5,
        "title": "Pets and their procedure dates",
        "question": "List each pet's name along with every procedure_date for that pet.",
        "answer_sql": """
SELECT p.name, h.procedure_date
FROM pets p
JOIN procedure_history h ON p.pet_id = h.pet_id;
""",
        "explanation": "Joining pets with procedure_history on pet_id gives all procedure dates per pet."
    },
    {
        "level": 6,
        "title": "Total procedure cost per pet",
        "question": "For each pet, show the pet name and the total amount spent on all of its procedures.",
        "answer_sql": """
SELECT p.name,
       SUM(d.price) AS total_cost
FROM pets p
JOIN procedure_history h ON p.pet_id = h.pet_id
JOIN procedure_details d
    ON h.procedure_type = d.procedure_type
   AND h.procedure_subcode = d.procedure_subcode
GROUP BY p.name;
""",
        "explanation": "We join pets → history → details, then GROUP BY pet name and SUM the price of all procedures."
    },
    {
        "level": 7,
        "title": "Owners with more than one pet",
        "question": "List owner_id values for owners who have more than one pet.",
        "answer_sql": """
SELECT owner_id
FROM pets
GROUP BY owner_id
HAVING COUNT(*) > 1;
""",
        "explanation": "HAVING is used with GROUP BY to filter groups (owners) by an aggregate condition (COUNT(*) > 1)."
    },
    {
        "level": 8,
        "title": "Most expensive procedure",
        "question": "Show the description and price of the most expensive procedure in procedure_details.",
        "answer_sql": """
SELECT description, price
FROM procedure_details
WHERE price = (SELECT MAX(price) FROM procedure_details);
""",
        "explanation": "The subquery finds the maximum price; the outer query returns procedures whose price equals that max."
    },
    {
        "level": 9,
        "title": "Pets with above-average procedure cost",
        "question": "List pet_id values of pets whose average procedure cost is greater than the overall average procedure price.",
        "answer_sql": """
SELECT h.pet_id
FROM procedure_history h
JOIN procedure_details d
  ON h.procedure_type = d.procedure_type
 AND h.procedure_subcode = d.procedure_subcode
GROUP BY h.pet_id
HAVING AVG(d.price) > (SELECT AVG(price) FROM procedure_details);
""",
        "explanation": "We compute AVG(price) per pet and compare it to the global AVG(price) across all procedures."
    },
    {
        "level": 10,
        "title": "High-spending owners",
        "question": "List each owner_id, full name, and total amount spent on procedures, only for owners who spent more than 100.",
        "answer_sql": """
SELECT o.owner_id,
       o.first_name || ' ' || o.last_name AS owner_name,
       SUM(d.price) AS total_spent
FROM owners o
JOIN pets p ON o.owner_id = p.owner_id
JOIN procedure_history h ON p.pet_id = h.pet_id
JOIN procedure_details d
    ON h.procedure_type = d.procedure_type
   AND h.procedure_subcode = d.procedure_subcode
GROUP BY o.owner_id, o.first_name, o.last_name
HAVING SUM(d.price) > 100;
""",
        "explanation": "Full multi-table join followed by GROUP BY owner and a HAVING filter on the total SUM(price)."
    },
    {
        "level": 11,
        "title": "Owners whose pets never had any procedure",
        "question": "List first_name and last_name of owners who have pets, but none of their pets ever appear in procedure_history.",
        "answer_sql": """
SELECT DISTINCT o.first_name, o.last_name
FROM owners o
JOIN pets p ON o.owner_id = p.owner_id
WHERE NOT EXISTS (
    SELECT 1
    FROM procedure_history h
    WHERE h.pet_id = p.pet_id
);
""",
        "explanation": "We join owners to pets, then use NOT EXISTS to keep owners whose pets have no matching rows in procedure_history."
    },
    {
        "level": 12,
        "title": "Total revenue by pet kind",
        "question": "For each kind of pet (e.g., 'Dog', 'Cat'), show the total revenue from all procedures done on that kind, ordered from highest to lowest revenue.",
        "answer_sql": """
SELECT p.kind,
       SUM(d.price) AS total_revenue
FROM pets p
JOIN procedure_history h ON p.pet_id = h.pet_id
JOIN procedure_details d
    ON h.procedure_type = d.procedure_type
   AND h.procedure_subcode = d.procedure_subcode
GROUP BY p.kind
ORDER BY total_revenue DESC;
""",
        "explanation": "We group by pet kind and sum all procedure prices. ORDER BY total_revenue DESC shows the most valuable kinds first."
    },
    {
        "level": 13,
        "title": "Most expensive procedure per owner",
        "question": "For each owner, show owner_id, full name, and the price of the single most expensive procedure ever performed on any of their pets.",
        "answer_sql": """
SELECT o.owner_id,
       o.first_name || ' ' || o.last_name AS owner_name,
       MAX(d.price) AS max_procedure_price
FROM owners o
JOIN pets p ON o.owner_id = p.owner_id
JOIN procedure_history h ON p.pet_id = h.pet_id
JOIN procedure_details d
    ON h.procedure_type = d.procedure_type
   AND h.procedure_subcode = d.procedure_subcode
GROUP BY o.owner_id, o.first_name, o.last_name;
""",
        "explanation": "We join all ownership and procedure tables, then GROUP BY owner and use MAX(price) to find the highest single charge per owner."
    },
    {
        "level": 14,
        "title": "Owners who have both a dog and a cat",
        "question": "List owner_id values for owners who own at least one 'Dog' and at least one 'Cat'.",
        "answer_sql": """
SELECT owner_id
FROM pets
GROUP BY owner_id
HAVING SUM(CASE WHEN kind = 'Dog' THEN 1 ELSE 0 END) >= 1
   AND SUM(CASE WHEN kind = 'Cat' THEN 1 ELSE 0 END) >= 1;
""",
        "explanation": "Using conditional aggregation with CASE inside HAVING, we ensure each owner has at least one Dog and one Cat."
    },
    {
        "level": 15,
        "title": "Top 3 highest-spending owners",
        "question": "Show the top 3 owners by total amount spent on all procedures, including owner_id, full name, and total_spent. Break ties arbitrarily.",
        "answer_sql": """
SELECT o.owner_id,
       o.first_name || ' ' || o.last_name AS owner_name,
       SUM(d.price) AS total_spent
FROM owners o
JOIN pets p ON o.owner_id = p.owner_id
JOIN procedure_history h ON p.pet_id = h.pet_id
JOIN procedure_details d
    ON h.procedure_type = d.procedure_type
   AND h.procedure_subcode = d.procedure_subcode
GROUP BY o.owner_id, o.first_name, o.last_name
ORDER BY total_spent DESC
FETCH FIRST 3 ROWS ONLY;
""",
        "explanation": (
            "We compute total_spent per owner and then ORDER BY total_spent DESC to rank them. "
            "FETCH FIRST 3 ROWS ONLY returns the top 3 spenders. "
            "This uses a common Oracle-style pagination clause."
        )
    },
]

# Helper: get level info safely
def get_level(level_number: int):
    for lvl in LEVELS:
        if lvl["level"] == level_number:
            return lvl
    return None

# ============================
# ✅ STREAMLIT UI (STUDENT-ONLY)
# ============================

st.set_page_config(page_title="SQL Level Practice (Vet Clinic)", layout="centered")

st.title("🧠 SQL Level Practice Tutor – Vet Clinic Database")

st.markdown(
    "Practice SQL using a realistic veterinary clinic schema. "
    "Start from **Level 1** and work up to **Level 15** for advanced joins, subqueries, and HAVING."
)

# Show schema at top
st.markdown("## 📘 Relational Schema")
st.code(SCHEMA_TEXT, language="sql")

st.markdown("---")

# Sidebar: choose level
st.sidebar.header("Choose Level")
selected_level = st.sidebar.slider(
    "Level (1 = easiest, 15 = hardest)",
    min_value=1,
    max_value=15,
    value=1,
    step=1
)

level_info = get_level(selected_level)

st.markdown(f"## ✅ Level {level_info['level']}: {level_info['title']}")
st.markdown(f"**Question:** {level_info['question']}")

st.markdown(
    "✏️ **Tip:** Try to write the query yourself first (in your own SQL editor or in the box below). "
    "Then reveal the solution and compare."
)

# Optional answer typing area (not graded)
_ = st.text_area(
    "Your SQL answer (for your own practice – not auto-graded):",
    height=140
)

with st.expander("✅ Show solution and explanation"):
    st.markdown("**Suggested SQL answer:**")
    st.code(level_info["answer_sql"], language="sql")
    st.markdown("**Explanation:**")
    st.write(level_info["explanation"])

# Final congratulations message at max level
if selected_level == 15:
    st.success(
        "🎉 Congratulations! You've reached **Level 15** on the Vet Clinic database.\n\n"
        "If you understand all of these queries, you have strong skills with multi-table joins, "
        "GROUP BY, HAVING, and subqueries in a realistic relational schema."
    )
