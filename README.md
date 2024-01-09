
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
The script evaluates submissions based on the following criteria, each carrying specific point values:

1. **CF Shorthand Parsing (1 point)**: Checks whether the CF shorthand is correctly formatted. Incorrect formatting results in 0 points.

2. **PCR Step Simulation (1 point)**: Verifies the successful simulation of the PCR step. Failure to simulate correctly results in 0 points.

3. **Restriction Sites Check (1 point)**: Assesses the presence of necessary restriction sites (EcoRI, BamHI, BglII, XhoI) in the PCR product. Missing one or more required sites results in a deduction of points.

4. **Biobricking Check (1 point)**: Ensures that the biobricking restriction sites are in the correct order and appear only once. Errors in ordering or multiple occurrences lead to point deductions.

5. **5' Tails Check (1 point)**: Confirms the presence and adequacy of 5' tails for each restriction site. Missing or insufficient tails result in a deduction of points.

6. **CF Simulation (2 points)**: Involves the full simulation of the construction file. Failure in this step leads to a deduction of points.

7. **Product Check (2 points)**: Evaluates the final product plasmid for the presence of target sequences and backbone. Missing elements or incorrect sequences result in a deduction of points.

Each step contributes to the total score, with a maximum possible score of 9 points. Detailed feedback is provided for each step to guide students on areas of improvement.


Scores and comments are generated for each criterion.

## Dependencies
- Python 3.x
- Requests library
- BeautifulSoup library
- PyDNA_CF_Simulator library
