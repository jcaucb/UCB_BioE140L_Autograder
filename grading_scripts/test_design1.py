import grade_design1

def test_grader1(cf_text):
    # Mock a submission object as it would be received from Canvas
    submission = {
        'id': 'test_submission',
        'body': cf_text  # The text of the construction file
    }

    # Call the grading function
    score, comments = grade_design1.grade(submission)

    # Print out the results
    print(f"Grade: {score}")
    print("Comments:")
    for comment in comments:
        print(comment)

# Example CF text to test
cf_text_example = """
PCR ceaB-F ceaB-R ColE2 pcrpdt
Digest pcrpdt BglII,XhoI 1 pcrdig
Digest pBca9145-Bca1089 BglII,XhoI 1 vectdig
Ligate pcrdig vectdig pBca9145-ceaB

oligo ceaB-F ccaaaAGATCTatgagcggtggcgatggacg
oligo ceaB-R gctagCTCGAGttaGGATCCttacttaccccgatgaatatc
"""

# Run the test
test_grader1(cf_text_example)
