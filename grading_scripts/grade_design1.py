from bs4 import BeautifulSoup
from pydna_cf_simulator.parse_CF_shorthand import parse_CF_shorthand
from pydna_cf_simulator.construction_file import ConstructionFile, PCR
from pydna_cf_simulator.simulate_CF import simulate_CF
import logging
import json

def grade(submission):
    comments = []
    logging.debug(f"Starting to grade submission ID: {submission.get('id', 'Unknown')}")

    # Parse HTML and extract CF shorthand
    try:
        logging.debug(f"Parsing HTML content for submission ID: {submission.get('id', 'Unknown')}")
        soup = BeautifulSoup(submission['body'], 'html.parser')
        cf_shorthand = soup.get_text(separator='\n').strip()  # Use '\n' as the separator
        logging.debug(f"CF shorthand extracted for submission ID {submission.get('id', 'Unknown')}: {cf_shorthand}")
    except Exception as e:
        error_msg = f"Error parsing HTML for submission ID {submission.get('id', 'Unknown')}: {e}"
        logging.error(error_msg)
        comments.append(error_msg)
        return 0, comments


    # Parse CF shorthand
    try:
        logging.debug(f"Attempting to parse CF shorthand for submission ID {submission.get('id', 'Unknown')}")
        cf = parse_CF_shorthand(cf_shorthand)
        logging.info(f"CF shorthand successfully parsed for submission ID {submission.get('id', 'Unknown')}")
    except Exception as e:
        error_msg = f"Invalid CF shorthand format for submission ID {submission.get('id', 'Unknown')}: {e}"
        logging.error(error_msg)
        comments.append(error_msg)
        return 0, comments

    # Check PCR step
    logging.debug("Checking PCR step")
    score, pcr_product = check_pcr_step(cf, comments)
    logging.debug(f"PCR step check completed with score: {score}")
    if score != 5:
        return score, comments

    # Check for restriction sites
    logging.debug("Checking for restriction sites")
    score = check_restriction_sites(pcr_product, comments)
    logging.debug(f"Restriction sites check completed with score: {score}")
    if score != 5:
        return score, comments

    # Check for biobricking
    logging.debug("Checking for biobricking")
    score = check_biobricking(pcr_product, comments)
    logging.debug(f"Biobricking check completed with score: {score}")
    if score != 5:
        return score, comments

    # Check for 5' tails
    logging.debug("Checking for 5' tails")
    score = check_5_prime_tails(pcr_product, comments)
    logging.debug(f"5' tails check completed with score: {score}")
    if score != 5:
        return score, comments

    # Simulate entire CF and check product
    logging.debug("Preparing to check simulated product")
    try:
        score = check_simulated_product(cf, comments)
        logging.debug(f"Product check completed with score: {score}")
    except Exception as e:
        logging.error(f"Error during product check: {e}")
        comments.append(f"Error during product check: {e}")
        return 3, comments

    logging.debug(f"Final score after all checks: {score}")
    return score, comments


# Helper functions

def check_pcr_step(cf, comments):
    logging.debug("Checking PCR step in the construction file")

    # Find PCR steps in the construction file
    pcr_steps = [step for step in cf.steps if isinstance(step, PCR)]
    logging.debug(f"Found {len(pcr_steps)} PCR steps")

    # Check for the number of PCR steps
    if len(pcr_steps) != 1:
        error_msg = f"Expected 1 PCR step, found {len(pcr_steps)}."
        logging.error(error_msg)
        comments.append(error_msg)
        return 2, None  # Return 2 points if the number of PCR steps is not exactly one

    # Log details of the PCR step
    pcr_step = pcr_steps[0]
    logging.debug(f"PCR Step: {pcr_step}")

    # Create a new construction file with only the PCR step and the original sequences
    new_cf = ConstructionFile([pcr_step], cf.sequences)
    logging.debug("Created a new construction file with the PCR step and original sequences")

    # Attempt to simulate the PCR step
    try:
        simulated_seqs = simulate_CF(new_cf)
        success_msg = "PCR step successfully simulated."
        logging.info(success_msg)
        comments.append(success_msg)
        pcr_product_name = pcr_steps[0].output  # Get the name of the output of the PCR step
        return 5, simulated_seqs[pcr_product_name]  # Return full points and the PCR product
    except Exception as e:
        error_msg = f"PCR Step failed to simulate: {e}"
        logging.error(error_msg)
        comments.append(error_msg)
        return 2, None  # Return 2 points if simulation fails

def check_restriction_sites(pcr_product, comments):
    logging.debug("Checking restriction sites in the PCR product")
    
    # Define the restriction sites to check
    restriction_sites = {
        "EcoRI": "GAATTC",
        "BamHI": "GGATCC",
        "BglII": "AGATCT",
        "XhoI": "CTCGAG"
    }

    # Check for the presence of the restriction sites
    sites_present = {site: (seq in pcr_product.sequence) for site, seq in restriction_sites.items()}
    logging.debug(f"Restriction sites presence: {sites_present}")

    # Add comments based on the presence of restriction sites
    for site, present in sites_present.items():
        if present:
            comments.append(f"Restriction site {site} is present in the PCR product.")
        else:
            comments.append(f"Restriction site {site} is missing in the PCR product.")

    # Check if the required pairs of restriction sites are present
    if (sites_present["EcoRI"] and sites_present["BamHI"]) or (sites_present["BglII"] and sites_present["XhoI"]):
        comments.append("Required pairs of restriction sites are present.")
        return 5  # Return full points if at least one pair is present
    else:
        comments.append("Required pairs of restriction sites are missing.")
        return 3  # Deduct points if none of the pairs are present
    
def check_biobricking(pcr_product, comments):
    logging.debug("Checking biobricking")
    
    # Define the biobricking restriction sites
    biobrick_sites = {"EcoRI": "GAATTC", "BglII": "AGATCT", "BamHI": "GGATCC", "XhoI": "CTCGAG"}

    # Check if the sites are present in order and only once
    site_positions = {site: pcr_product.sequence.find(seq) for site, seq in biobrick_sites.items()}
    logging.debug(f"Site positions: {site_positions}")
    ordered_sites = sorted([(pos, site) for site, pos in site_positions.items() if pos != -1])
    logging.debug(f"Ordered sites: {ordered_sites}")

    # Check if they are in the correct order
    if ordered_sites == sorted(ordered_sites, key=lambda x: x[0]):
        comments.append("Biobricking restriction sites are in the correct order.")
    else:
        comments.append("Biobricking restriction sites are not in the correct order.")
        return 4  # Deduct points if the order is incorrect

    # Check if there is more than one count of any site
    if any(pcr_product.sequence.count(seq) > 1 for site, seq in biobrick_sites.items()):
        comments.append("Multiple counts of a biobricking restriction site found.")
        return 4  # Deduct points for multiple counts

    comments.append("Biobricking check passed.")
    return 5  # Return full points if passed

def check_5_prime_tails(pcr_product, comments):
    logging.debug("Checking for 5' tails in the PCR product")

    # Define the restriction sites and their sequences
    restriction_sites = {
        "EcoRI": "GAATTC", "BglII": "AGATCT", "BamHI": "GGATCC", "XhoI": "CTCGAG"
    }

    # Iterate over restriction sites to check for 5' tails
    for site, sequence in restriction_sites.items():
        index = pcr_product.sequence.find(sequence)
        logging.debug(f"Checking 5' tail for {site}: Found at index {index}")

        # Check if the restriction site is present
        if index != -1:
            # Check for 5' tail
            if index < 5 or (len(pcr_product.sequence) - (index + len(sequence))) < 5:
                comments.append(f"5' tail missing or insufficient for restriction site {site}.")
                logging.warning(f"5' tail missing or insufficient for restriction site {site}.")
                return 3  # Deduct points for missing 5' tail
            else:
                comments.append(f"5' tail present for restriction site {site}.")
                logging.info(f"5' tail present for restriction site {site}.")

    logging.debug("All required 5' tails are present.")
    return 5  # Return full points if all 5' tails are present

# Variables for sequences (to be provided)
ceaB_sequence = "ATGAGCGGTGGCGATGGACGCGGCCATAACACGGGCGCGCATAGCACAAGTGGTAACATTAATGGTGGCCCGACCGGGCTTGGTGTAGGTGGTGGTGCTTCTGATGGCTCCGGATGGAGTTCGGAAAATAACCCGTGGGGTGGTGGTTCCGGTAGCGGCATTCACTGGGGTGGTGGTTCCGGTCATGGTAATGGCGGGGGGAATGGTAATTCCGGTGGTGGTTCGGGAACAGGCGGTAATCTGTCAGCAGTAGCTGCGCCAGTGGCATTTGGTTTTCCGGCACTTTCCACTCCAGGAGCTGGCGGTCTGGCGGTCAGTATTTCAGCGGGAGCATTATCGGCAGCTATTGCTGATATTATGGCTGCCCTGAAAGGACCGTTTAAATTTGGTCTTTGGGGGGTGGCTTTATATGGTGTATTGCCATCACAAATAGCGAAAGATGACCCCAATATGATGTCAAAGATTGTGACGTCATTACCCGCAGATGATATTACTGAATCACCTGTCAGTTCATTACCTCTCGATAAGGCAACAGTAAACGTAAATGTTCGTGTTGTTGATGATGTAAAAGACGAACGACAGAATATTTCGGTTGTTTCAGGTGTTCCGATGAGTGTTCCGGTGGTTGATGCAAAACCTACCGAACGTCCAGGTGTTTTTACGGCATCAATTCCAGGTGCACCTGTTCTGAATATTTCAGTTAATAACAGTACGCCAGAAGTACAGACATTAAGCCCAGGTGTTACAAATAATACTGATAAGGATGTTCGCCCGGCAGGATTTACTCAGGGTGGTAATACCAGGGATGCAGTTATTCGATTCCCGAAGGACAGCGGTCATAATGCCGTATATGTTTCAGTGAGTGATGTTCTTAGTCCTGACCAGGTAAAACAACGTCAGGATGAAGAAAATCGCCGTCAGCAGGAATGGGATGCTACGCATCCGGTTGAAGCGGCTGAGCGAAATTATGAACGCGCGCGTGCAGAGCTGAATCAGGCAAATGAAGATGTTGCCAGAAATCAGGAGCGACAGGCTAAAGCTGTTCAGGTTTATAATTCGCGTAAAAGCGAACTTGATGCAGCGAATAAAACTCTTGCTGATGCAATAGCTGAAATAAAACAATTTAATCGATTTGCCCATGACCCAATGGCTGGCGGTCACAGAATGTGGCAAATGGCCGGACTTAAAGCTCAGCGGGCGCAGACGGATGTAAATAATAAGCAGGCTGCATTTGATGCTGCTGCAAAAGAGAAGTCAGATGCTGATGCTGCATTAAGTGCCGCGCAGGAGCGCCGCAAACAGAAGGAAAATAAAGAAAAGGACGCTAAGGATAAATTAGATAAGGAGAGTAAACGGAATAAGCCAGGGAAGGCGACAGGTAAAGGTAAACCAGTTGGTGATAAATGGCTGGATGATGCAGGTAAAGATTCAGGAGCGCCAATTCCAGATCGCATTGCTGATAAGTTGCGTGATAAAGAATTTAAAAACTTTGACGATTTCCGGAAGAAATTCTGGGAAGAAGTGTCAAAAGATCCCGATCTTAGTAAGCAATTTAAAGGCAGTAATAAGACGAACATTCAAAAGGGAAAAGCACCTTTTGCAAGGAAGAAAGACCAAGTAGGTGGTAGGGAACGCTTTGAATTACATCATGATAAACCAATCAGTCAGGATGGTGGTGTCTATGATATGAATAATATCAGAGTGACCACACCTAAGCGACATATTGATATTCATCGGGGTAAGTAA"
ceaB_with_restriction_sites = "GATCTATGAGCGGTGGCGATGGACGCGGCCATAACACGGGCGCGCATAGCACAAGTGGTAACATTAATGGTGGCCCGACCGGGCTTGGTGTAGGTGGTGGTGCTTCTGATGGCTCCGGATGGAGTTCGGAAAATAACCCGTGGGGTGGTGGTTCCGGTAGCGGCATTCACTGGGGTGGTGGTTCCGGTCATGGTAATGGCGGGGGGAATGGTAATTCCGGTGGTGGTTCGGGAACAGGCGGTAATCTGTCAGCAGTAGCTGCGCCAGTGGCATTTGGTTTTCCGGCACTTTCCACTCCAGGAGCTGGCGGTCTGGCGGTCAGTATTTCAGCGGGAGCATTATCGGCAGCTATTGCTGATATTATGGCTGCCCTGAAAGGACCGTTTAAATTTGGTCTTTGGGGGGTGGCTTTATATGGTGTATTGCCATCACAAATAGCGAAAGATGACCCCAATATGATGTCAAAGATTGTGACGTCATTACCCGCAGATGATATTACTGAATCACCTGTCAGTTCATTACCTCTCGATAAGGCAACAGTAAACGTAAATGTTCGTGTTGTTGATGATGTAAAAGACGAACGACAGAATATTTCGGTTGTTTCAGGTGTTCCGATGAGTGTTCCGGTGGTTGATGCAAAACCTACCGAACGTCCAGGTGTTTTTACGGCATCAATTCCAGGTGCACCTGTTCTGAATATTTCAGTTAATAACAGTACGCCAGAAGTACAGACATTAAGCCCAGGTGTTACAAATAATACTGATAAGGATGTTCGCCCGGCAGGATTTACTCAGGGTGGTAATACCAGGGATGCAGTTATTCGATTCCCGAAGGACAGCGGTCATAATGCCGTATATGTTTCAGTGAGTGATGTTCTTAGTCCTGACCAGGTAAAACAACGTCAGGATGAAGAAAATCGCCGTCAGCAGGAATGGGATGCTACGCATCCGGTTGAAGCGGCTGAGCGAAATTATGAACGCGCGCGTGCAGAGCTGAATCAGGCAAATGAAGATGTTGCCAGAAATCAGGAGCGACAGGCTAAAGCTGTTCAGGTTTATAATTCGCGTAAAAGCGAACTTGATGCAGCGAATAAAACTCTTGCTGATGCAATAGCTGAAATAAAACAATTTAATCGATTTGCCCATGACCCAATGGCTGGCGGTCACAGAATGTGGCAAATGGCCGGACTTAAAGCTCAGCGGGCGCAGACGGATGTAAATAATAAGCAGGCTGCATTTGATGCTGCTGCAAAAGAGAAGTCAGATGCTGATGCTGCATTAAGTGCCGCGCAGGAGCGCCGCAAACAGAAGGAAAATAAAGAAAAGGACGCTAAGGATAAATTAGATAAGGAGAGTAAACGGAATAAGCCAGGGAAGGCGACAGGTAAAGGTAAACCAGTTGGTGATAAATGGCTGGATGATGCAGGTAAAGATTCAGGAGCGCCAATTCCAGATCGCATTGCTGATAAGTTGCGTGATAAAGAATTTAAAAACTTTGACGATTTCCGGAAGAAATTCTGGGAAGAAGTGTCAAAAGATCCCGATCTTAGTAAGCAATTTAAAGGCAGTAATAAGACGAACATTCAAAAGGGAAAAGCACCTTTTGCAAGGAAGAAAGACCAAGTAGGTGGTAGGGAACGCTTTGAATTACATCATGATAAACCAATCAGTCAGGATGGTGGTGTCTATGATATGAATAATATCAGAGTGACCACACCTAAGCGACATATTGATATTCATCGGGGTAAGTAAGGATCC"
plasmid_backbone_sequence = "GGATCCTAACTCGAGCTGCAGGCTTCCTCGCTCACTGACTCGCTGCGCTCGGTCGTTCGGCTGCGGCGAGCGGTATCAGCTCACTCAAAGGCGGTAATACGGTTATCCACAGAATCAGGGGATAACGCAGGAAAGAACATGTGAGCAAAAGGCCAGCAAAAGGCCAGGAACCGTAAAAAGGCCGCGTTGCTGGCGTTTTTCCATAGGCTCCGCCCCCCTGACGAGCATCACAAAAATCGACGCTCAAGTCAGAGGTGGCGAAACCCGACAGGACTATAAAGATACCAGGCGTTTCCCCCTGGAAGCTCCCTCGTGCGCTCTCCTGTTCCGACCCTGCCGCTTACCGGATACCTGTCCGCCTTTCTCCCTTCGGGAAGCGTGGCGCTTTCTCATAGCTCACGCTGTAGGTATCTCAGTTCGGTGTAGGTCGTTCGCTCCAAGCTGGGCTGTGTGCACGAACCCCCCGTTCAGCCCGACCGCTGCGCCTTATCCGGTAACTATCGTCTTGAGTCCAACCCGGTAAGACACGACTTATCGCCACTGGCAGCAGCCACTGGTAACAGGATTAGCAGAGCGAGGTATGTAGGCGGTGCTACAGAGTTCTTGAAGTGGTGGCCTAACTACGGCTACACTAGAAGGACAGTATTTGGTATCTGCGCTCTGCTGAAGCCAGTTACCTTCGGAAAAAGAGTTGGTAGCTCTTGATCCGGCAAACAAACCACCGCTGGTAGCGGTGGTTTTTTTGTTTGCAAGCAGCAGATTACGCGCAGAAAAAAAGGATCTCAAGAAGATCCTTTGATCTTTTCTACGGGGTCTGACGCTCAGTGGAACGAAAACTCACGTTAAGGGATTTTGGTCATGAGATTATCAAAAAGGATCTTCACCTAGATCCTTTTAAATTAAAAATGAAGTTTTAAATCAATCTAAAGTATATATGAGTAAACTTGGTCTGACAGTTACCAATGCTTAATCAGTGAGGCACCTATCTCAGCGATCTGTCTATTTCGTTCATCCATAGTTGCCTGACTCCCCGTCGTGTAGATAACTACGATACGGGAGGGCTTACCATCTGGCCCCAGTGCTGCAATGATACCGCGAGACCCACGCTCACCGGCTCCAGATTTATCAGCAATAAACCAGCCAGCCGGAAGGGCCGAGCGCAGAAGTGGTCCTGCAACTTTATCCGCCTCCATCCAGTCTATTAATTGTTGCCGGGAAGCTAGAGTAAGTAGTTCGCCAGTTAATAGTTTGCGCAACGTTGTTGCCATTGCTACAGGCATCGTGGTGTCACGCTCGTCGTTTGGTATGGCTTCATTCAGCTCCGGTTCCCAACGATCAAGGCGAGTTACATGATCCCCCATGTTGTGCAAAAAAGCGGTTAGCTCCTTCGGTCCTCCGATCGTTGTCAGAAGTAAGTTGGCCGCAGTGTTATCACTCATGGTTATGGCAGCACTGCATAATTCTCTTACTGTCATGCCATCCGTAAGATGCTTTTCTGTGACTGGTGAGTACTCAACCAAGTCATTCTGAGAATAGTGTATGCGGCGACCGAGTTGCTCTTGCCCGGCGTCAATACGGGATAATACCGCGCCACATAGCAGAACTTTAAAAGTGCTCATCATTGGAAAACGTTCTTCGGGGCGAAAACTCTCAAGGATCTTACCGCTGTTGAGATCCAGTTCGATGTAACCCACTCGTGCACCCAACTGATCTTCAGCATCTTTTACTTTCACCAGCGTTTCTGGGTGAGCAAAAACAGGAAGGCAAAATGCCGCAAAAAAGGGAATAAGGGCGACACGGAAATGTTGAATACTCATACTCTTCCTTTTTCAATATTATTGAAGCATTTATCAGGGTTATTGTCTCATGAGCGGATACATATTTGAATGTATTTAGAAAAATAAACAAATAGGGGTTCCGCGCACATTTCCCCGAAAAGTGCCACCTGACGTCTAAGAAACCATTATTATCATGACATTAACCTATAAAAATAGGCGTATCACGAGGCAGAATTTCAGATAAAAAAAATCCTTAGCTTTCGCTAAGGATGATTTCTGGAATTCATGA"

def check_simulated_product(cf, comments):
    # # Log the CF
    # try:
    #     cf_json = json.dumps(cf, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    #     logging.debug(f"CF JSON: {cf_json}")
    # except Exception as e:
    #     logging.error(f"Error converting CF to JSON: {e}")

    try:
        logging.debug("Attempting full CF simulation.")
        seqs = simulate_CF(cf)
        logging.debug("CF simulation successful.")
        comments.append("CF simulation successful. Checking product plasmid.")

        # Retrieve the name of the product plasmid from the last step
        product_plasmid_name = cf.steps[-1].output
        product_plasmid = seqs.get(product_plasmid_name, None)
        logging.debug(f"Product plasmid: {product_plasmid}")

        if product_plasmid is None:
            comments.append(f"No product plasmid '{product_plasmid_name}' found.")
            return 3.5

        # Perform checks on the product plasmid
        if ceaB_sequence not in product_plasmid.sequence:
            comments.append("Missing ceaB sequence in product plasmid.")
            return 3.5
        if ceaB_with_restriction_sites not in product_plasmid.sequence:
            comments.append("Missing ceaB sequence with restriction sites in product plasmid.")
            return 3.5
        if plasmid_backbone_sequence not in product_plasmid.sequence:
            comments.append("Missing plasmid backbone sequence in product plasmid.")
            return 3.5

        logging.debug("All checks passed for simulated product.")
        return 5

    except Exception as e:
        error_msg = f"CF simulation failed: {e}"
        logging.error(error_msg)
        comments.append(error_msg)
        return 3
