import json
import re

def load_rules():
    """Loads admission rules from the JSON file."""
    with open('admission_rules.json', 'r') as f:
        return json.load(f)

# Load the rules once
RULES = load_rules()

def extract_course_and_marks(user_input):
    """Extracts course name and marks from any user input."""
    user_input = user_input.lower().strip()

    # Extract percentage
    marks_match = re.search(r'(\d{1,3})\s*%', user_input)
    marks = float(marks_match.group(1)) if marks_match else None

    # Extract course using aliases
    matched_course = None
    for course_key, details in RULES.items():
        for alias in details["aliases"]:
            if alias.lower() in user_input:
                matched_course = course_key
                break
        if matched_course:
            break

    return matched_course, marks

def check_admission_eligibility_from_text(user_input):
    """
    Checks eligibility from any free-text user input.
    """
    course, marks = extract_course_and_marks(user_input)

    if not course or marks is None:
        return "Please mention both course name and percentage (e.g., 'CSE 92%')."

    rule = RULES[course]
    if marks >= rule['min_marks']:
        return f"Yes! With {marks}%, you meet the minimum requirement for {course}. {rule['notes']}"
    else:
        return (f"Sorry, the minimum requirement for {course} is {rule['min_marks']}%. "
                f"With {marks}%, you may not be eligible. {rule['notes']}")
