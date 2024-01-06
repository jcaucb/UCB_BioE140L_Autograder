# grading_scripts/grade_design1.py

from bs4 import BeautifulSoup

import logging
from bs4 import BeautifulSoup

def grade(submission):
    logging.debug(f"Starting to grade submission ID: {submission.get('id', 'Unknown')}")

    # Parse the HTML content in the submission body
    soup = BeautifulSoup(submission['body'], 'html.parser')
    logging.debug(f"HTML content parsed for submission ID: {submission.get('id', 'Unknown')}")

    # Extract text
    submission_text = soup.get_text().strip()
    logging.debug(f"Extracted text from submission ID {submission.get('id', 'Unknown')}: {submission_text}")

    try:
        # Try to convert the submission text to an integer
        submission_int = int(submission_text)
        logging.debug(f"Converted text to integer for submission ID {submission.get('id', 'Unknown')}: {submission_int}")
    except ValueError:
        logging.error(f"ValueError for submission ID {submission.get('id', 'Unknown')}: Cannot convert '{submission_text}' to an integer")
        # If the conversion fails, return -1 to indicate an error
        return -1, "Invalid submission format. Please submit a valid integer."

    # Grading logic for Design1
    if submission_int == 37:
        logging.info(f"Submission ID {submission.get('id', 'Unknown')} graded with score 5")
        return 5, 'Score: 5'
    elif submission_int == 33:
        logging.info(f"Submission ID {submission.get('id', 'Unknown')} graded with score 3")
        return 3, 'Score: 3'
    else:
        logging.info(f"Submission ID {submission.get('id', 'Unknown')} graded with score 0")
        return 0, 'Score: 0'
