# grading_scripts/grade_design1.py

from bs4 import BeautifulSoup

def grade(submission):
    # Parse the HTML content in the submission body
    soup = BeautifulSoup(submission['body'], 'html.parser')

    # Extract text
    submission_text = soup.get_text().strip()

    # Grading logic for Design1
    if submission_text == '55':
        return 5, 'comment Score: 5'
    elif submission_text == '33':
        return 3, 'comment Score: 3'
    else:
        return 0, 'comment Score: 0'

