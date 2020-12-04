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
import datetime
from dateutil import relativedelta
from nltk.corpus import stopwords
import spacy


##CONSTANTS###
STOPWORDS = set(stopwords.words('english'))
YEAR = r'(((20|19)(\d{2})))'
MONTHS_SHORT = r'(jan)|(feb)|(mar)|(apr)|(may)|(jun)|(jul)|(aug)|(sep)|(oct)|(nov)|(dec)'
MONTHS_LONG = r'(january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december)'
MONTH = r'(' + MONTHS_SHORT + r'|' + MONTHS_LONG + r')'
EDUCATION = ['UNIVERSITY','B.E.', 'B.E',"B.Sc", 'ME', 'M.E', 'M.E.', 'MS', 'M.S', 'BTECH', 'MTECH',
                    'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII','PHD','BS','HIGH SCHOOL','COLLEGE','SCHOOL','BSC','MSC'
                    ]

RESUME_SECTIONS = [
                    'experience',
                    'education',
                    'skills',
                ]
################################


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
    count = 0

    for token in tokens:
        first = token.lower()
        Can_Check = False
        if count < len(tokens)-1:
            second = str(tokens[count + 1]).lower()
            phrase = first + " " + second
            Can_Check = True

        if phrase in skills and Can_Check:
            if skillset.get(phrase, -1) == -1:
                skillset[phrase] = 1
            else:
                skillset[phrase] = skillset[phrase] + 1
            Can_Check = False
        elif first in skills:
            token = token.lower()
            if skillset.get(token, -1) == -1:
                skillset[token] = 1

            else:
                skillset[token] = skillset[token] + 1
        count = count + 1

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


def extract_education(nlp_text):
    '''
    Helper function to extract education from spacy nlp text
    :param nlp_text: object of `spacy.tokens.doc.Doc`
    :return: tuple of education degree and year if year if found else only returns education degree
    '''
    edu = {}
    # Extract education degree
    for index, text in enumerate(nlp_text):
        count = 0
        splitted = text.split()
        for tex in text.split():

            tex = re.sub(r'[?|$|.|!|,]', r'', tex)
            if tex.upper() in EDUCATION and tex not in STOPWORDS:
                if (tex.lower() == 'university'):
                    tex = splitted[count-1] +" "+tex
                edu[tex] = text + nlp_text[index]

            count = count + 1
    # Extract year
    education = []
    for key in edu.keys():
        #year = re.search(re.compile(YEAR), edu[key])
        years = (re.findall(YEAR,edu[key]))
        biggest = 0
        for i in years:
            new = int(i[0])
            if new > biggest:
                biggest = new
        if biggest > 0:
                education.append((key,biggest))
        else:
            education.append(key)
    educ = {}
    count = 0
    for i in education:
        count = count + 1

        if len(i) > 1:
            if str(i[1]).isnumeric():
                educ[count] = {"Facility/Title": i[0], 'year': i[1]}

            else:
                educ[count] = {"Facility/Title": i, 'year': None}
        else:
            educ[count] = {"Facility/Title": i,'year': None}


        #print(year.string)
        # if year:
        #     education.append((key, ''.join(year.group(0))))
        # else:
        #     education.append(key)
    return educ

# def extract_education2(education_list):
#     edu = {}
#     for line in education_list:
#         line = re.sub(r'[?|$|.|!|,]', r'',line)
#         words = line.split()
#         count = 0
#         for word in words:
#             count = count + 1
#             if word.upper() in EDUCATION and word not in STOPWORDS:
#                 if (word.lower() == 'university'):
#                     line = words[count-2] + " " + word
#                 edu[word] = line
#
#     return edu

        # if line.upper() in EDUCATION and line not in STOPWORDS:
        #     if (lnie.lower() == 'university'):
        #         line = splitted[count - 1] + " " + tex
        #     edu[tex] = text + nlp_text[index]
        #
        # count = count + 1


def extract_entity_sections_grad(text):
    '''
    Helper function to extract all the raw text from sections of
    resume specifically for graduates and undergraduates
    :param text: Raw text of resume
    :return: dictionary of entities
    '''
    text = re.sub("/"," ",text)
    text_split = [i.strip() for i in text.split('\n')]
    text_split2 = text_split
    # sections_in_resume = [i for i in text_split if i.lower() in sections]
    entities = {}
    count = 0
    for i in text_split2:
        count = count + 1
        experience = re.search(
        r'(?P<fmonth>\w+.\d\d\d\d)\s*(\D|to)\s*(?P<smonth>\w+.\d\d\d\d|present)',
        i,
        re.I
        )
        if experience:
            try:
                if text_split2[count - 1] != '' and text_split2[count - 3] != '' and len(text_split2[count - 1].split()) < 7 :
                    text_split2[count-3] = text_split2[count - 3]+ " " + text_split2[count-1]
                    text_split2.pop(count - 1)
            except IndexError:
                print("INDEX")
                # if text_split2[count - 1] == '':
                #     text_split2 = text_split2[count - 1] + text_split2[count]



    text_split = text_split2
    key = False
    for phrase in text_split:
        if len(phrase) == 1:
            p_key = phrase
        else:
            p_key = set(phrase.lower().split()) & set(RESUME_SECTIONS)
        try:
            p_key = list(p_key)[0]
        except IndexError:
            pass
        if p_key in RESUME_SECTIONS and entities.get(p_key,0) == 0:
            entities[p_key] = []
            key = p_key
        elif key and phrase.strip():
                entities[key].append(phrase)
        count = count + 1


    # entity_key = False
    # for entity in entities.keys():
    #     sub_entities = {}
    #     for entry in entities[entity]:
    #         if u'\u2022' not in entry:
    #             sub_entities[entry] = []
    #             entity_key = entry
    #         elif entity_key:
    #             sub_entities[entity_key].append(entry)
    #     entities[entity] = sub_entities

    # pprint.pprint(entities)

    # make entities that are not found None
    # for entity in cs.RESUME_SECTIONS:
    #     if entity not in entities.keys():
    #         entities[entity] = None
    return entities


def get_total_experience(experience_list):
    '''
    Wrapper function to extract total months of experience from a resume
    :param experience_list: list of experience text extracted
    :return: total months of experience
    '''
    exp_ = []
    for line in experience_list:
        experience = re.search(
            r'(?P<fmonth>\w+.\d\d\d\d)\s*(\D|to)\s*(?P<smonth>\w+.\d\d\d\d|present)',
            line,
            re.I
        )
        if experience:
            exp_.append(experience.groups())
    total_exp = sum(
        [get_number_of_months_from_dates(i[0], i[2]) for i in exp_]
    )
    total_experience_in_months = total_exp
    return total_experience_in_months


def get_number_of_months_from_dates(date1, date2):
    '''
    Helper function to extract total months of experience from a resume
    :param date1: Starting date
    :param date2: Ending date
    :return: months of experience from date1 to date2
    '''
    if date2.lower() == 'present':
        date2 = datetime.datetime.now().strftime('%b %Y')
    try:
        if len(date1.split()[0]) > 3:
            date1 = date1.split()
            date1 = date1[0][:3] + ' ' + date1[1]
        if len(date2.split()[0]) > 3:
            date2 = date2.split()
            date2 = date2[0][:3] + ' ' + date2[1]
    except IndexError:
        return 0
    try:
        date1 = datetime.datetime.strptime(str(date1), '%b %Y')
        date2 = datetime.datetime.strptime(str(date2), '%b %Y')
        months_of_experience = relativedelta.relativedelta(date2, date1)
        months_of_experience = (months_of_experience.years
                                * 12 + months_of_experience.months)
    except ValueError:
        return 0
    return months_of_experience


def extract_experience(experience_list):

    total = {}
    count = 1
    for line in experience_list:
        experience = re.search(
            r'(?P<fmonth>\w+.\d\d\d\d)\s*(\D|to)\s(?P<smonth>\w+.\d\d\d\d|present)',
            line,
            re.I
        )

        if experience:
            exp_name = (line[:experience.start()])
            exp_ = (experience.groups())

            exp_month = (get_number_of_months_from_dates(exp_[0], exp_[2]))
            total[count] = {'Experience Name': exp_name, "Month":exp_month}
            count = count + 1
    return total
def get_skill_months(experience_list,text_raw):
    exp_list = list(experience_list.keys())
    count = 0
    mounthly = {}
    nlp = spacy.load('en_core_web_sm')
    for i in exp_list:
        if len(exp_list) < count + 1:
            start = re.search(experience_list[i]['Experience Name'],text_raw)
            end = re.search(experience_list[i+1]['Experience Name'],text_raw)
            #        self.__nlp = nlp(self.__text)
            # self.__noun_chunks = list(self.__nlp.noun_chunks)
            skills_t = nlp(text_raw[start.start():end.start()])
            noun_chunks = list(skills_t.noun_chunks)
            mounthly[count+1] = {'Experience Name':experience_list[i]['Experience Name'],"Skills": extract_skills(skills_t, noun_chunks), "Month":experience_list[i]['Month']}
        else:
            start = re.search(experience_list[i]['Experience Name'], text_raw)
            if start is not None:
                skills_t = nlp(text_raw[start.start():])
                noun_chunks = list(skills_t.noun_chunks)
                mounthly[count+1] = {'Experience Name': experience_list[i]['Experience Name'],"Skills": extract_skills(skills_t, noun_chunks), "Month":experience_list[i]['Month']}
        count = count+1
    return mounthly
