
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

## Grading Scheme for Design1

The autograder evaluates "Design1" submissions based on several criteria, each with specific point values. The maximum possible score is 5 points. Here's a breakdown of the evaluation criteria:

1. **CF Shorthand Parsing (1 point)**: 
   - Validates the format of the Construction File (CF) shorthand. Incorrect formatting results in 0 points.
   
2. **PCR Step Simulation (1 point)**: 
   - Verifies the successful simulation of the Polymerase Chain Reaction (PCR) step. Failure to simulate correctly results in 0 points.

3. **Restriction Sites Check (1 point)**: 
   - Assesses the presence of required restriction sites (EcoRI, BamHI, BglII, XhoI) in the PCR product. Missing sites result in a deduction of points.

4. **Biobricking Check (1 point)**: 
   - Ensures biobricking restriction sites are in the correct order and occur only once. Errors lead to point deductions.

5. **5' Tails Check (1 point)**: 
   - Confirms the presence and adequacy of 5' tails for each restriction site. Missing or insufficient tails result in a deduction of points.

If any step fails, subsequent steps are not evaluated, capping the maximum possible score at the point of failure.

Scores and comments are generated for each criterion.

## Dependencies
- Python 3.x
- Requests library
- BeautifulSoup library
- PyDNA_CF_Simulator library
