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
