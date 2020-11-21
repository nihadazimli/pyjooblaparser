#Libraries to be used
import docx2txt
import textract
from textblob import TextBlob
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import io
import re
import os
import pandas as pd


def extract_text(resume_full_path, ext):
    # INPUTS
    # resume_full_path: full file path of CV
    # ext: extension of CV file (e.g. .pdf)
    if ext == '.pdf':
        text_raw = extract_text_from_pdf(resume_full_path)
    elif ext == '.docx':
        text_raw = extract_text_from_docx(resume_full_path)
    else:
        text_raw = extract_text_from_any(resume_full_path)

    return text_raw


def extract_name():
    # To be populated
    pass


def extract_email(text_raw):

    # Input email regex
    # regex = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x" \
    #         r"23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](" \
    #         r"?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01" \
    #         r"]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0" \
    #         r"b\x0c\x0e-\x7f])+)\])"

    # matches = re.findall(regex, text_raw, re.MULTILINE)

    # return matches[0]
    return ""


def extract_number(text_raw):
    # Input email regex
    # regex = r"([+]?\d{1,2}[.-\s]?)?(\d{3}[.-]?){2}\d{4}"
    # matches = re.findall(regex, text_raw, re.MULTILINE)
    return ""


def extract_location():
    # To be populated
    pass


def extract_skills(text_raw, noun_chunks,skills_file=None):
    # Inputs are:
    # text raw: full string version of CV file
    # skills_file_location: full name and location of skills file (e.g. path\to\skills.csv)
    # To be populated
    # return list of skill out of text raw string input
    '''
    Helper function to extract skills from spacy nlp text
    :param text_raw: object of `spacy.tokens.doc.Doc`
    :param noun_chunks: noun chunks extracted from nlp text
    :return: list of skills extracted
    '''
    tokens = [token.text for token in text_raw if not token.is_stop]
    if not skills_file:
        data = pd.read_csv(
            os.path.join(os.path.dirname(__file__), 'updated_u.csv')

        )

    else:
        data = pd.read_csv(skills_file)
    skills = list(data.columns.values)
    skillset = {}
    # check for one-grams
    for token in tokens:
        if token.lower() in skills:
            token = token.lower()
            if skillset.get(token, -1) == -1:
                skillset[token] = 1

            else:
                skillset[token] = skillset[token] + 1

    # check for bi-grams and tri-grams
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            token = token.lower()
            if skillset.get(token, -1) == -1:
                skillset[token] = 1

            else:
                skillset[token] = skillset[token] + 1

    return skillset



def noun_phase_extractor(text_raw):
    # Extract Noun Phrases using  TextBlob Library
    blob = TextBlob(text_raw)
    nouns = blob.noun_phrases
    return nouns


def extract_text_from_pdf(pdf_path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()

    if text:
        return text


def extract_text_from_docx(docx_path):
    try:
        temp = docx2txt.process(docx_path)
        text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
        return ' '.join(text)
    except KeyError:
        return ' '


def extract_text_from_any(file_path):
    try:
        text = textract.process(file_path).decode('utf-8')
        return text
    except KeyError:
        return ' '


def cluster_finder(text_raw,this,soft=False):
    text = text_raw.strip(":")
    text = text.lower()
    text = text.split("\n")
    file = open(this,"r")
    file = file.readline()
    phrases = file.split(",")
    label = []
    line = []

    for i in phrases:
        count = 0
        for k in text:
            count = count + 1
            s = re.findall(i,k)
            if len(s) > 0 and i!='':
                label.append(s)
                ste = re.compile(s[len(s)-1])
                big = (" ".join(text))
                t = ste.search(big)
                ve = t.start()
                line.append(ve)
    if soft == True:
        return label
    return label,line

