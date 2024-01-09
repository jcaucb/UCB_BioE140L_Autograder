
# UCB BioE140L Autograder

## Description
This project provides an autograding script for the BioE 140L course at UC Berkeley. It interfaces with the Canvas LMS to automate grading of student submissions.

## Installation
```bash
!pip install git+https://github.com/UCB-BioE-Anderson-Lab/PyDNA_CF_Simulator.git
```

## Usage
1. **Start the Main Script**: Initiates grading, connecting to Canvas and iterating through assignments.
2. **Automatic Grading and Feedback**: Evaluates each submission, applying grading criteria and generating scores and comments.
3. **Submission Updates**: Updates Canvas with scores and detailed comments for each student.

## Grading Scheme
The script evaluates submissions based on several criteria:
1. **CF Shorthand Parsing**
2. **PCR Step Simulation**
3. **Restriction Sites Check**
4. **Biobricking Check**
5. **5' Tails Check**
6. **CF Simulation**
7. **Product Check**

Scores and comments are generated for each criterion.

## Dependencies
- Python 3.x
- Requests library
- BeautifulSoup library
- PyDNA_CF_Simulator library
