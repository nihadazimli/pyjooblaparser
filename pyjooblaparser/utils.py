#Libraries to be used
from textblob import TextBlob

def extract_text(resume_full_name, ext):
    # To be populated
    pass


def extract_name():
    # To be populated
    pass


def extract_email():
    # To be populated
    pass


def extract_location():
    # To be populated
    pass


def extract_skills(text_raw, skills_file_location):
    # Inputs are:
    # text raw: full string version of CV file
    # skills_file_location: full name and location of skills file (e.g. path\to\skills.csv)

    # To be populated
    # return list of skill out of text raw string input

    pass



def noun_phase_extractor(text_raw):
    # Extract Noun Phrases using  TextBlob Library
    blob = TextBlob(text_raw)
    nouns = blob.noun_phrases
    return nouns
