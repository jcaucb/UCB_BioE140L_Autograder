# grading_scripts/grade_design1.py

from bs4 import BeautifulSoup

def grade(submission):
    # Parse the HTML content in the submission body
    soup = BeautifulSoup(submission['body'], 'html.parser')

    # Extract text
    submission_text = soup.get_text().strip()

    try:
        # Try to convert the submission text to an integer
        submission_int = int(submission_text)
    except ValueError:
        # If the conversion fails, return -1 to indicate an error
        return -1, "Invalid submission format. Please submit a valid integer."

    # Grading logic for Design1
    if submission_int == 55:
        return 5, 'Score: 5'
    elif submission_int == 33:
        return 3, 'Score: 3'
    else:
        return 0, 'Score: 0'
