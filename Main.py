import time
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CANVAS_URL = 'https://bcourses.berkeley.edu/api/v1/'
COURSE_ID = 1531205

headers = {'Authorization': f'Bearer {API_TOKEN}'}

def get_assignments(course_id):
    response = requests.get(f"{CANVAS_URL}courses/{course_id}/assignments", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve assignments, status code:", response.status_code)
        return []  # Return an empty list in case of failure

def get_submissions(assignment_id):
    response = requests.get(f"{CANVAS_URL}courses/{COURSE_ID}/assignments/{assignment_id}/submissions", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve submissions for assignment {assignment_id}")
        return []

def grade_submission(assignment, submission):
    # Placeholder for grading logic. This needs to be integrated with your actual grading scripts.
    # Return a tuple of (score, comment)
    return 0, "Not graded yet"

def update_submission(course_id, assignment_id, user_id, score, comment):
    payload = {
        'submission': {
            'posted_grade': score
        },
        'comment': {
            'text_comment': comment
        }
    }
    response = requests.put(f"{CANVAS_URL}courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}",
                            headers=headers, json=payload)
    return response.status_code == 200


def main():
    while True:
        print("Fetching assignments...")
        assignments = get_assignments(COURSE_ID)

        if not assignments:
            print("No assignments found or failed to retrieve assignments.")

        for assignment in assignments:
            print(f"Processing assignment: {assignment['name']} (ID: {assignment['id']})")
            submissions = get_submissions(assignment['id'])

            if not submissions:
                print(f"No submissions found for assignment {assignment['name']}.")

            for submission in submissions:
                print(f"Checking submission from user {submission['user_id']} for assignment {assignment['name']}.")
                if submission['workflow_state'] == 'submitted':
                    print(f"Grading submission from user {submission['user_id']} for assignment {assignment['name']}.")
                    score, comment = grade_submission(assignment, submission)
                    print(f"Attempting to update submission for user {submission['user_id']} with score {score} and comment: {comment}")
                    update_successful = update_submission(COURSE_ID, assignment['id'], submission['user_id'], score, comment)
                    if update_successful:
                        print(f"Successfully updated submission for user {submission['user_id']} with score {score}.")
                    else:
                        print(f"Failed to update submission for user {submission['user_id']}.")
        
        print("Completed processing all assignments. Waiting for 5 minutes before next iteration.")
        # Wait for 5 minutes before the next iteration
        time.sleep(300)


if __name__ == '__main__':
    main()

