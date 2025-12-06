import streamlit as st

# ============================
#  VET CLINIC SCHEMA
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

LEVELS = [
    {
        "level": 1,
        "title": "Owners in a specific state",
        "question": (
            "List owner_id, first_name, last_name, city, and state_abbre for all owners "
            "who live in the state 'Ohio' (state = 'OH'), ordered by last_name."
        ),
        "answer_sql": """
SELECT owner_id,
       first_name,
       last_name,
       city,
       state_abbre
FROM owners
WHERE state_abbre = 'OH'
ORDER BY last_name;
""",
        "explanation": "Basic filtering on state_abbre and sorting by last_name."
    },
    {
        "level": 2,
        "title": "Average age of pets by kind",
        "question": (
            "For each kind of pet (e.g., 'Dog', 'Cat'), show kind and the average age of pets of that kind. "
            "Name the calculated column avg_age and order by avg_age descending."
        ),
        "answer_sql": """
SELECT kind,
       AVG(age) AS avg_age
FROM pets
GROUP BY kind
ORDER BY avg_age DESC;
""",
        "explanation": "GROUP BY kind and use AVG(age) to compute the average age per kind."
    },
    {
        "level": 3,
        "title": "Owners and number of pets in each city",
        "question": (
            "For each city, show the city name, the number of distinct owners in that city, "
            "and the total number of pets owned by people in that city. "
            "Name the columns nr_owners and nr_pets."
        ),
        "answer_sql": """
SELECT o.city,
       COUNT(DISTINCT o.owner_id) AS nr_owners,
       COUNT(p.pet_id)           AS nr_pets
FROM owners o
LEFT JOIN pets p ON o.owner_id = p.owner_id
GROUP BY o.city;
""",
        "explanation": (
            "We join owners with pets and group by city. COUNT(DISTINCT owner_id) counts owners, "
            "and COUNT(pet_id) counts pets. LEFT JOIN ensures cities with owners but no pets still appear."
        )
    },
    {
        "level": 4,
        "title": "Number of procedures per pet",
        "question": (
            "For each pet, show pet_id, name, and the number of procedures that pet has received. "
            "Name the calculated column nr_procedures. Only include pets that have at least one procedure."
        ),
        "answer_sql": """
SELECT p.pet_id,
       p.name,
       COUNT(*) AS nr_procedures
FROM pets p
JOIN procedure_history h ON p.pet_id = h.pet_id
GROUP BY p.pet_id, p.name;
""",
        "explanation": "We join pets with procedure_history and group by each pet to count how many procedure_history rows it has."
    },
    {
        "level": 5,
        "title": "Average and extreme prices per procedure type",
        "question": (
            "For each procedure_type, show procedure_type, the average price, the minimum price, "
            "and the maximum price for that type. Name the columns avg_price, min_price, and max_price."
        ),
        "answer_sql": """
SELECT procedure_type,
       AVG(price) AS avg_price,
       MIN(price) AS min_price,
       MAX(price) AS max_price
FROM procedure_details
GROUP BY procedure_type;
""",
        "explanation": "We group by procedure_type and compute AVG, MIN, and MAX over the price column."
    },
    {
        "level": 6,
        "title": "Procedure types with above-average price",
        "question": (
            "List procedure_type values whose average price is greater than the overall average price "
            "across all procedures. Do not show the average itself, just the procedure_type."
        ),
        "answer_sql": """
SELECT procedure_type
FROM procedure_details
GROUP BY procedure_type
HAVING AVG(price) > (
    SELECT AVG(price)
    FROM procedure_details
);
""",
        "explanation": "We compare each procedure_type's AVG(price) to the overall AVG(price) using HAVING and a scalar subquery."
    },
    {
        "level": 7,
        "title": "Owners with many procedures",
        "question": (
            "For each owner, show owner_id, first_name, last_name, and the total number of procedures "
            "performed on all of their pets. Name the column nr_procedures. Only include owners who have "
            "at least 3 procedures in total."
        ),
        "answer_sql": """
SELECT o.owner_id,
       o.first_name,
       o.last_name,
       COUNT(*) AS nr_procedures
FROM owners o
JOIN pets p ON o.owner_id = p.owner_id
JOIN procedure_history h ON p.pet_id = h.pet_id
GROUP BY o.owner_id, o.first_name, o.last_name
HAVING COUNT(*) >= 3;
""",
        "explanation": "We join owners → pets → procedure_history and group by owner, then filter with HAVING COUNT(*) >= 3."
    },
    {
        "level": 8,
        "title": "Pets that never had any procedure",
        "question": (
            "List pet_id and name for all pets that never had any procedure recorded in procedure_history."
        ),
        "answer_sql": """
SELECT p.pet_id,
       p.name
FROM pets p
WHERE NOT EXISTS (
    SELECT 1
    FROM procedure_history h
    WHERE h.pet_id = p.pet_id
);
""",
        "explanation": "NOT EXISTS with a correlated subquery checks that no history rows exist for that pet_id."
    },
    {
        "level": 9,
        "title": "Owners with pets of multiple kinds",
        "question": (
            "List owner_id, first_name, and last_name for owners who own pets of at least two different kinds "
            "(for example, both a dog and a cat)."
        ),
        "answer_sql": """
SELECT o.owner_id,
       o.first_name,
       o.last_name
FROM owners o
JOIN pets p ON o.owner_id = p.owner_id
GROUP BY o.owner_id, o.first_name, o.last_name
HAVING COUNT(DISTINCT p.kind) >= 2;
""",
        "explanation": "We group by owner and use COUNT(DISTINCT kind) to require at least two different pet kinds."
    },
    {
        "level": 10,
        "title": "Owners whose pets only received one procedure type",
        "question": (
            "List owner_id, first_name, and last_name for owners whose pets have received procedures "
            "from exactly one distinct procedure_type (for all of their pets combined)."
        ),
        "answer_sql": """
SELECT o.owner_id,
       o.first_name,
       o.last_name
FROM owners o
JOIN pets p ON o.owner_id = p.owner_id
JOIN procedure_history h ON p.pet_id = h.pet_id
GROUP BY o.owner_id, o.first_name, o.last_name
HAVING COUNT(DISTINCT h.procedure_type) = 1;
""",
        "explanation": "We join owners, pets, and history, group by owner, and require exactly one distinct procedure_type in HAVING."
    },
    {
        "level": 11,
        "title": "High-spending owners using a CTE",
        "question": (
            "Using a WITH clause, first compute, for each owner, the total amount spent on all procedures "
            "for their pets. Then select owner_id, first_name, last_name, and total_spent for owners whose "
            "total_spent is greater than 500."
        ),
        "answer_sql": """
WITH owner_totals AS (
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
    GROUP BY o.owner_id, o.first_name, o.last_name
)
SELECT owner_id, first_name, last_name, total_spent
FROM owner_totals
WHERE total_spent > 500;
""",
        "explanation": "The CTE owner_totals computes total_spent per owner, and the outer query filters to owners over 500."
    },
    {
        "level": 12,
        "title": "Update prices with CASE by procedure type",
        "question": (
            "Write an UPDATE that increases prices in procedure_details as follows: "
            "for procedures of type 'VACCINATIONS', increase price by 15%; "
            "for procedures of type 'GROOMING', increase price by 5%; "
            "for all other procedure types, leave the price unchanged. Use a single UPDATE with a CASE expression."
        ),
        "answer_sql": """
UPDATE procedure_details
SET price = CASE
    WHEN procedure_type = 'VACCINATIONS' THEN price * 1.15
    WHEN procedure_type = 'GROOMING'     THEN price * 1.05
    ELSE price
END;
""",
        "explanation": "CASE chooses a different multiplier based on procedure_type; other types keep the same price."
    },
    {
        "level": 13,
        "title": "Delete history for very cheap procedures",
        "question": (
            "Delete all rows from procedure_history that correspond to procedures with a price less than 20. "
            "Use a subquery on procedure_details (joined by procedure_type and procedure_subcode)."
        ),
        "answer_sql": """
DELETE FROM procedure_history h
WHERE EXISTS (
    SELECT 1
    FROM procedure_details d
    WHERE d.procedure_type = h.procedure_type
      AND d.procedure_subcode = h.procedure_subcode
      AND d.price < 20
);
""",
        "explanation": "The correlated subquery finds procedure_details with price < 20 that match each history row; EXISTS keeps only those to delete."
    },
    {
        "level": 14,
        "title": "Daily activity summary",
        "question": (
            "For each procedure_date, show procedure_date, the number of distinct pets treated that day, "
            "and the total revenue for that day. Name the columns nr_pets and total_revenue."
        ),
        "answer_sql": """
SELECT h.procedure_date,
       COUNT(DISTINCT h.pet_id) AS nr_pets,
       SUM(d.price)             AS total_revenue
FROM procedure_history h
JOIN procedure_details d
  ON h.procedure_type = d.procedure_type
 AND h.procedure_subcode = d.procedure_subcode
GROUP BY h.procedure_date;
""",
        "explanation": "We group by procedure_date and compute both the number of distinct pets and the sum of prices."
    },
    {
        "level": 15,
        "title": "Spending by owner and procedure type",
        "question": (
            "For each combination of owner and procedure_type, show owner_id, first_name, last_name, procedure_type, "
            "and the total amount spent on that type. Name the calculated column total_spent. "
            "Only include rows where total_spent is at least 500, and order the final result by total_spent descending."
        ),
        "answer_sql": """
SELECT o.owner_id,
       o.first_name,
       o.last_name,
       d.procedure_type,
       SUM(d.price) AS total_spent
FROM owners o
JOIN pets p ON o.owner_id = p.owner_id
JOIN procedure_history h ON p.pet_id = h.pet_id
JOIN procedure_details d
  ON h.procedure_type = d.procedure_type
 AND h.procedure_subcode = d.procedure_subcode
GROUP BY o.owner_id, o.first_name, o.last_name, d.procedure_type
HAVING SUM(d.price) >= 500
ORDER BY total_spent DESC;
""",
        "explanation": (
            "We join all four tables, group by owner and procedure_type, and keep only combinations with SUM(price) >= 500, "
            "then sort by total_spent descending."
        )
    },
]

# Helper to find level info
def get_level_info(level_number: int):
    for lvl in LEVELS:
        if lvl["level"] == level_number:
            return lvl
    return None

# ============================
#  STREAMLIT UI
# ============================

st.set_page_config(page_title="CSC 350 SQL Practice Tutor", layout="centered")

st.title("CSC 350 SQL Practice Tutor")

st.caption("Note: Please don't look at the solution first; this page is for you to practice writing SQL.")

st.markdown("## Relational Schema")
st.code(SCHEMA_TEXT, language="sql")

st.markdown("---")

# Sidebar: old-school level selection using radio buttons
st.sidebar.header("Select Level")
level_numbers = [lvl["level"] for lvl in LEVELS]
selected_level = st.sidebar.radio("Level", options=level_numbers, index=0)

level_info = get_level_info(selected_level)

if level_info is None:
    st.error("Level not found.")
else:
    st.markdown(f"### Level {level_info['level']}: {level_info['title']}")
    st.write(level_info["question"])

    # User SQL area (no hints, no grading)
    _ = st.text_area("Write your SQL here:", height=200)

    with st.expander("Show solution and explanation"):
        st.markdown("**Suggested SQL solution:**")
        st.code(level_info["answer_sql"], language="sql")
        st.markdown("**Explanation:**")
        st.write(level_info["explanation"])

    if selected_level == max(level_numbers):
        st.success("🎉 You reached the highest level in this practice tutor.")
