import time
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CANVAS_URL = 'https://bcourses.berkeley.edu/api/v1/'
COURSE_ID = 1531586 # Spr24 BioE 140L canvas course number
ASSIGNMENTS = [
    {
        'id': 8685248,                         # Assignment ID
        'name': 'Design1: Basic Design Quiz',  # Assignment Name
        'grader': 'grade_design1'              # Grader Function Name
    },
    # Add more assignments in the same format
    # Example:
    # {
    #     'id': 1234567,                        # Another Assignment ID
    #     'name': 'Another Assignment Name',    # Another Assignment Name
    #     'grader': 'another_grader_function'   # Corresponding Grader Function
    # }
]

headers = {'Authorization': f'Bearer {API_TOKEN}'}

def get_assignments(course_id):
    response = requests.get(f"{CANVAS_URL}courses/{course_id}/assignments", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve assignments, status code:", response.status_code)
        return []  # Return an empty list in case of failure

def get_submissions(assignment_id):
    submissions = []
    page = 1
    while True:
        response = requests.get(
            f"{CANVAS_URL}courses/{COURSE_ID}/assignments/{assignment_id}/submissions?page={page}",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            submissions.extend(data)
            if not data:  # No more data, break the loop
                break
            page += 1
        else:
            logging.error(f"Failed to retrieve submissions for assignment {assignment_id}, page {page}, status code: {response.status_code}")
            break
    return submissions


import importlib
import requests
from urllib.parse import urljoin, urlparse, parse_qs

def get_submissions(assignment_id):
    submissions = []
    url = f"{CANVAS_URL}courses/{COURSE_ID}/assignments/{assignment_id}/submissions"
    
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            submissions.extend(response.json())

            # Parsing the Link header for pagination
            link_header = response.headers.get('Link', None)
            if link_header:
                links = {rel.split(';')[1].strip().replace('rel="', '').replace('"', ''): urljoin(url, rel.split(';')[0].strip().replace('<', '').replace('>', '')) for rel in link_header.split(',')}
                url = links.get('next', None)
            else:
                url = None
        else:
            logging.error(f"Failed to retrieve submissions for assignment {assignment_id}, status code: {response.status_code}")
            break

    return submissions

def update_submission(course_id, assignment_id, user_id, score, comments, gradeable=True):
    combined_comment = '\n'.join(comments)  # Joins all comments with a newline character between them

    try:
        payload = {
            'submission': {'posted_grade': score},
            'comment': {'text_comment': combined_comment}
        }
        response = requests.put(
            f"{CANVAS_URL}courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}",
            headers=headers, json=payload
        )
        if response.status_code == 200:
            logging.debug(f"Successfully updated submission for user {user_id}")
            return True
        else:
            logging.error(f"Failed to update submission for user {user_id}, status code: {response.status_code}, response: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Exception occurred while updating submission for user {user_id}: {e}")
        return False

# ... [rest of your code before the main function] ...

from grading_scripts import grade_design1  # Import all grading scripts

# Configure logging
import logging
logging.basicConfig(filename='autograder.log', level=logging.DEBUG, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

def main():
    while True:
        logging.info("Starting processing of assignments.")
        for assignment in ASSIGNMENTS:
            assignment_id = assignment['id']
            assignment_name = assignment['name']
            logging.info(f"Processing assignment: {assignment_name} (ID: {assignment_id})")

            try:
                submissions = get_submissions(assignment_id)
                if not submissions:
                    logging.warning(f"No submissions found for assignment {assignment_name}. Continuing to next assignment.")
                    continue

                grader_function = getattr(importlib.import_module(f'grading_scripts.{assignment["grader"]}'), 'grade')
                for submission in submissions:
                    user_id = submission['user_id']
                    submission_state = submission['workflow_state']  # Define submission_state here
                    logging.debug(f"Submission from user {user_id} is in '{submission_state}' state.")
                    
                    if submission_state != 'submitted':
                        logging.debug(f"Skipping non-submitted submission from user {user_id} in state '{submission_state}'.")
                        continue

                    logging.info(f"Grading submission from user {user_id} for assignment {assignment_name}.")
                    score, comment = grader_function(submission)
                    if score < 0:
                        logging.warning(f"Submission from user {user_id} cannot be graded. Comment: {comment}")
                        continue

                    logging.info(f"Updating submission for user {user_id} with score {score} and comment: {comment}")
                    update_successful = update_submission(COURSE_ID, assignment_id, user_id, score, comment, True)
                    if not update_successful:
                        logging.error(f"Failed to update submission for user {user_id}.")
            
            except Exception as e:
                logging.critical(f"Unexpected error while processing assignment {assignment_name}: {e}")
                continue

        logging.info("Completed processing all specified assignments. Waiting for 5 minutes before next iteration.")
        time.sleep(300)

if __name__ == '__main__':
    main()
