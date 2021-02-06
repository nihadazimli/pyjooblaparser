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
import time
import snowballstemmer
##CONSTANTS###
STOPWORDS = set(stopwords.words('english'))
YEAR = r'(((20|19)(\d{2})))'
MONTHS_SHORT = r'(jan)|(feb)|(mar)|(apr)|(may)|(jun)|(jul)|(aug)|(sep)|(oct)|(nov)|(dec)'
MONTHS_LONG = r'(january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december)'
MONTH = r'(' + MONTHS_SHORT + r'|' + MONTHS_LONG + r')'
EDUCATION = ['UNIVERSITY','B.E.', 'B.E',"B.Sc", 'ME', 'M.E', 'M.E.', 'MS', 'M.S', 'BTECH', 'MTECH',
             'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII','PHD','BS','HIGH SCHOOL','COLLEGE','SCHOOL','BSC','MSC'
             ]
SENIORITY = ['junior',
             'senior',
             'mid',
             'years of experience',
             'years of professional experience',
             'years production expertise',
             'years of production expertise',
             'years\' experience in'
            ]
EXPERIENCE_KEYWORDS = [
             'years of experience',
             'years of professional experience',
             'years production expertise',
             'years of production expertise',
             'years\' experience in'
]
RESUME_SECTIONS = [
                    'experience',
                    'education',
                    'skills',
                    'employment',
                ]
BACHELORS = ["genetic engineering and biotechnology",
"architecture",
"biochemistry",
"biomedical science",
"business administration",
"clinical science",
"commerce",
"computer applications",
"community health",
"computer information systems",
"construction technology",
"criminal justice",
"divinity",
"economics",
"fine arts",
"letters",
"information systems",
"pharmacy",
"philosophy",
"public affairs and policy management",
"social work",
"technology",
"accountancy",
"arts in american studies",
"arts in american indian studies",
"arts in applied psychology",
"arts in biology",
"arts in anthropology",
"arts in child advocacy",
"arts in clinical psychology",
"arts in communication",
"arts in forensic psychology",
"arts in organizational psychology",
"aerospace engineering",
"accountancy",
"actuarial",
"agriculture",
"applied economics",
"architecture",
"architectural engineering",
"athletic training",
"biology",
"biomedical engineering",
"bible",
"business administration",
"business administration - computer application",
"business administration - economics",
"business and technology",
"chemical engineering",
"chemistry",
"civil engineering",
"clinical laboratory science",
"cognitive science",
"computer engineering",
"computer science",
"construction engineering",
"construction management",
"criminal justice",
"criminology",
"diagnostic radiography",
"electrical engineering",
"electronics and communications",
"electronics",
"engineering physics",
"engineering science",
"engineering technology",
"english literature",
"environmental engineering",
"environmental science",
"environmental studies",
"food science",
"foreign service",
"forensic science",
"forestry",
"history",
"hospitality management",
"human resources management",
"industrial engineering",
"information technology",
"information systems",
"integrated science",
"international relations",
"journalism",
"legal management",
"management",
"manufacturing engineering",
"marketing",
"mathematics",
"mathematical engineering",
"mechanical engineering",
"medical technology",
"metallurgical engineering",
"meteorology",
"microbiology",
"mining engineering",
"molecular biology",
"neuroscience",
"nursing",
"nutrition science",
"software engineering",
"petroleum engineering",
"podiatry",
"pharmacology",
"pharmacy",
"physical therapy",
"physics",
"plant science",
"politics",
"psychology",
"public safety",
"physiology",
"quantity surveying engineering",
"radiologic technology",
"real-time interactive simulation",
"respiratory therapy",
"risk management and insurance",
"science education",
"sports management",
"systems engineering",
"music in jazz studies",
"music in composition",
"music in performance",
"music in theory",
"music in music education",
"veterinary technology",
"military and strategic studies"]


TOP100 = ["university of california, los angeles (ucla)",
"nanyang technological university, singapore (ntu)",
"ucl",
"university of washington",
"columbia university",
"cornell university",
"new york university (nyu)",
"peking university",
"the university of edinburgh",
"university of waterloo",
"university of british columbia",
"the hong kong university of science and technology",
"georgia institute of technology",
"the university of tokyo",
"california institute of technology (caltech)",
"the chinese university of hong kong (cuhk)",
"university of texas at austin",
"the university of melbourne",
"university of illinois at urbana-champaign",
"shanghai jiao tong university",
"university of pennsylvania",
"kaist - korea advanced institute of science & technology",
"technical university of munich",
"the university of hong kong",
"université psl",
"politecnico di milano",
"the australian national university",
"the university of sydney",
"kth royal institute of technology",
"university of southern california",
"university of amsterdam",
"yale university",
"university of chicago",
"seoul national university",
"university of michigan-ann arbor",
"university of maryland, college park",
"aarhus university",
"boston university",
"city university of hong kong",
"delft university of technology",
"duke university",
"ecole polytechnique",
"eindhoven university of technology",
"fudan university",
"indian institute of technology bombay (iitb)",
"indian institute of technology delhi (iitd)",
"johns hopkins university",
"ku leuven",
"king abdulaziz university (kau)",
"king's college london",
"kit, karlsruhe institute of technology",
"korea university",
"kyoto university",
"lomonosov moscow state university",
"ludwig-maximilians-universität münchen",
"mcgill university",
"monash university",
"national taiwan university (ntu)",
"politecnico di torino",
"purdue university",
"rwth aachen university",
"sapienza university of rome",
"sorbonne university",
"sungkyunkwan university(skku)",
"technische universität berlin (tu berlin)",
"vienna university of technology",
"the hong kong polytechnic university",
"the university of auckland",
"the university of manchester",
"the university of new south wales (unsw sydney)",
"the university of queensland",
"tokyo institute of technology (tokyo tech)",
"trinity college dublin, the university of dublin",
"universidad de chile",
"universidade de são paulo",
"alma mater studiorum - university of bologna",
"universitat politècnica de catalunya · barcelonatech (upc)",
"université catholique de louvain (uclouvain)",
"université de montréal",
"universiti malaya (um)",
"university of alberta",
"university of california, san diego (ucsd)",
"university of science and technology of china",
"university of technology sydney",
"university of wisconsin-madison"]

################################
strt_time = 0
end_time = 0


def refine_score_by_experience(listing_exp_len, total_exp_month, score):
    print("listing_exp_len", listing_exp_len)
    print("total_exp_month", total_exp_month)
    print("score", score)

    if 0 < listing_exp_len < 24:
        if total_exp_month > 36:
            print("1")
            score = score - (total_exp_month - 36) * 1.5
    elif 24 < listing_exp_len < 60:
        print("2")
        if 0 < total_exp_month < 24:
            score = score - (24 - total_exp_month) * 1.5
        elif total_exp_month > 72:
            score = score - (total_exp_month - 12) * 1.2
    elif 60 < listing_exp_len < 120:
        print("3")
        if 0 < total_exp_month < 60:
            score = score - (60 - total_exp_month) * 1
        if total_exp_month > 120:
            score = score - (total_exp_month - 60) * 0.6
    elif listing_exp_len > 120:
        print("4")
        if 0 < total_exp_month < 120:
            score = score - (120 - total_exp_month) * 0.5

    return score


def experience_total_duration(experience, intersection_must_list):
    experience_duration = {}
    for _, y in experience.items():
        for skill, _ in y['Skills'].items():
            if skill in intersection_must_list:
                try:
                    experience_duration[skill] += y['Month']
                except KeyError:
                    experience_duration[skill] = y['Month']
                except Exception as e:
                    print("Unexcepted error", e)
    print(experience_duration)
    return experience_duration


def extract_text(resume_full_path, ext):
    strt_time = datetime.datetime.now()
    # INPUTS
    # resume_full_path: full file path of CV
    # ext: extension of CV file (e.g. .pdf)
    if ext == '.pdf':
        text_raw = extract_text_from_pdf(resume_full_path)
    # elif ext == '.docx':
    #     text_raw = extract_text_from_docx(resume_full_path)
    else:
        text_raw = extract_text_from_any(resume_full_path)
    end_time = datetime.datetime.now() - strt_time
    print("EXTR TXT",end_time)
    return text_raw


def extract_name():
    # To be populated
    pass

def top100(text):
    text = text.lower()
    for i in TOP100:
        search = re.findall(i,text)
        if len(search) > 0:
            return search[0]
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

def extract_department_listing(text):
    found = ""
    found_arr = []
    for i in BACHELORS:
        found = re.findall(i, text.lower())
        if found:
            found_arr.append(found[0].lower())

    return found_arr

def matcher(found_arr,dep):
    for i in found_arr:
        s = re.findall(dep,i)
        if len(s)>0:
            return s
    return None

def extract_skills(text_raw, noun_chunks, skills_file=None):
    strt_time = datetime.datetime.now()
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
    end_time = datetime.datetime.now() - strt_time
    print("EXTR SKILLS",end_time)
    return skillset


def noun_phase_extractor(text_raw):
    strt_time = datetime.datetime.now()

    # Extract Noun Phrases using  TextBlob Library
    blob = TextBlob(text_raw)
    nouns = blob.noun_phrases
    end_time = datetime.datetime.now() - strt_time
    print("Phrase EXTR",end_time)
    return nouns


def extract_text_from_pdf(pdf_path):
    strt_time = datetime.datetime.now()
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
    end_time = datetime.datetime.now() - strt_time
    print("EXTRACT TEXT")
    if text:
        return text


def extract_text_from_docx(docx_path):
    strt_time = datetime.datetime.now()
    try:
        temp = docx2txt.process(docx_path)
        text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
        end_time = datetime.datetime.now() - strt_time
        print("From docx", end_time)
        return ' '.join(text)
    except KeyError:

        return ' '


def extract_text_from_any(file_path):
    strt_time = datetime.datetime.now()
    try:
        text = textract.process(file_path).decode('utf-8')
        end_time = datetime.datetime.now() - strt_time
        print("FROM ANY ", end_time)
        return text

    except KeyError:
        return ' '


def cluster_finder(text_raw, this, soft=False):
    strt_time = datetime.datetime.now()
    text = text_raw.strip(":")
    text = text.lower()
    text = text.split("\n")
    try:
        file = open(this,"r")
    except:
        os.system("ls")


    file = file.readline()
    phrases = file.split(",")
    label = []
    line = []

    for i in phrases:
        count = 0
        for k in text:
            count = count + 1
            s = re.findall(i,k)
            if len(s) > 0 and i != '':
                label.append(s)
                ste = re.compile(s[len(s)-1])
                big = (" ".join(text))
                t = ste.search(big)
                ve = t.start()
                line.append(ve)
    if soft:
        return label
    end_time = datetime.datetime.now() - strt_time
    print("CLuster finder",end_time)
    return label, line


def extract_education(nlp_text):
    #nlp_text = " ".join(nlp_text)
    #nlp_text = nlp_text.split("\n")
    print("educarion ",nlp_text)
    strt_time = datetime.datetime.now()
    bachelor = ""
    uni = ""
    '''
    Helper function to extract education from spacy nlp text
    :param nlp_text: object of `spacy.tokens.doc.Doc`
    :return: tuple of education degree and year if year if found else only returns education degree
    '''
    edu = {}
    # Extract education degree
    print("HAAAA",nlp_text)
    nlp_text_n  = []
    found = False
    for i in nlp_text:
        tex = re.sub(r'&'," and ",i)
        tex = re.sub(r'[\n|[?|$|.|!|,]', ' ',tex)
        tex = re.sub(r'\s+',' ',tex)
        s = tex.lower()
        r = re.search("university",s)
        t = re.search("college",s)
        word = "university"
        if r or t:
            if t:
                word = "college"
            arr = s.split()
            tex = tex.split()
            print(tex)
            index = arr.index(word)
            if len(arr) > index + 1:
                if arr[index + 1] == 'of':
                    print("ASASSAS", tex[index - 1])
                    if tex[index - 1][0].isupper():
                        print("ASASSAS",tex[index - 1])
                        print(arr)
                        uni = arr[index-1] + " " + arr[index] + " " + "of" + " " + arr[index + 2]
                    else:
                        uni = arr[index] + " " + "of" + " " + arr[index+2]
                else:
                    uni = arr[index -1] + " " + arr[index]
            # target = string[r.start()-10:r.start()]
            # uni = target.split()
            # uni = uni[len(uni)-1]
        nlp_text_n.append(s)

    text = ' '.join(nlp_text_n)
    print(text)
    for i in BACHELORS:
        s = re.findall(i,text)
        print("SSS",s)
        if len(s) > 0:
            bachelor = s[0]
            break


    # for index, text in enumerate(nlp_text):
    #     count = 0
    #     splitted = text.split()
    #     for tex in text.split():
    #
    #         tex = re.sub(r'[?|$|.|!|,]', r'', tex)
    #         if te.lower() in
    #         if tex.upper() in EDUCATION:
    #             if tex.lower() == 'university':
    #                 if splitted[count + 1] == "of":
    #                     tex = tex + " " + splitted[count + 1] + " " + splitted[count + 2]
    #                 else:
    #                     tex = splitted[count-1] + " " + tex
    #             edu[tex] = text + nlp_text[index]
    #
    #
    #         count = count + 1
    # Extract year
    education = []
    #year = re.search(re.compile(YEAR), edu[key])
    years = re.findall(YEAR, text)
    print("TEASR",years)
    if len(years)> 0:

        educ = {"UNI": uni, "DEP": bachelor, 'year': years[len(years)-1][0]}
    else:
        educ = {"UNI": uni, "DEP": bachelor, 'year': None}

        #print(year.string)
        # if year:
        #     education.append((key, ''.join(year.group(0))))
        # else:
        #     education.append(key)
    end_time = datetime.datetime.now() - strt_time
    print("EDUCATION",end_time)
    print("EDUCATION",educ)
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
    strt_time = datetime.datetime.now()
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
        experience = re.search(r'(?P<fmonth>\w+.\d\d\d\d)\s*(\D|to)\s*(?P<smonth>\w+.\d\d\d\d|present)', i, re.I)
        if experience:
            try:
                if text_split2[count - 1] != '' and text_split2[count - 3] != '' \
                        and len(text_split2[count - 1].split()) < 7:
                    text_split2[count-3] = text_split2[count - 3] + " " + text_split2[count-1]

                    #print("POPED",text_split2[count-1])
                    # if (len(text_split2[count-1])<3):
                    text_split2.pop(count - 1)
            except IndexError:
                #print("Index",text_split2[count - 1] )
                if text_split2[count - 1] == '':
                    text_split2 = text_split2[count - 1] + text_split2[count]
    text_split = text_split2
    key = False
    for phrase in text_split:
        if len(phrase) == 1:
            p_key = phrase
            print("PKEY",p_key)
        else:
            p_key = set(phrase.lower().split()) & set(RESUME_SECTIONS)
            print("PKEY2",p_key)
        try:
            p_key = list(p_key)[0]
            print("PKEY4",p_key)
        except IndexError:
            print("PKEY3",p_key)
            pass
        if p_key in RESUME_SECTIONS and entities.get(p_key, 0) == 0:
            entities[p_key] = []
            key = p_key
        elif key and phrase.strip():
                entities[key].append(phrase)
        count = count + 1
        try:
            if len(entities['employment']) > len(entities['experience']):
                entities['experience'] = entities['employment']
        except:
            pass

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
    end_time = datetime.datetime.now() - strt_time
    print("Entity ext",end_time)
    print("ENT",entities)
    return entities


def entity_grad_2(text):
    text = re.sub(":|,|\."," ",text)
    text = re.sub("\n"," ",text)
    text = re.sub("\t"," ",text)
    text = re.sub("  "," ",text)
    text2_U = text.split(" ")
    text2 = text.lower().split(" ")

    print("TEXT2",text2)
    t = text.lower().split()
    try:
        education = text2.index("university")
    except:
        education = text2.index("college")
    experiences = re.findall(r'(?P<fmonth>\w+.\d\d\d\d)\s*(\D|to)\s*(?P<smonth>\w+.\d\d\d\d|present)', text, re.I)
    print(experiences)
    print("eEE",experiences)


    try:

        experience = t.index(experiences[0][0].split(" ")[0].lower())
    except IndexError:
        experience = t.index(experiences[0].split(" ")[0].lower())
    if education > experience:
        exp_end = education - 1
        exp_end = education - 1
        edu_end = len(t)-1
    else:
        edu_end = experience - 1
        exp_end = len(t)-1
    edu = text2_U[education-10:edu_end]
    edu = ' '.join(edu)
    edu = edu.split('\n')
    exp = text2_U[experience-15:exp_end]
    exp = ' '.join(exp)
    for i in experiences:
        exp = re.sub(i[-1],str(i[-1]+" \n"), exp)
    exp = exp.split("\n")
    print("education",edu)

    print("experience",exp)
    return {"education": edu,
            "experience": exp}


def get_total_experience(experience_list):
    strt_time = datetime.datetime.now()
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
    end_time = datetime.datetime.now() - strt_time
    print("total exp",end_time)
    return total_experience_in_months


def get_number_of_months_from_dates(date1, date2):
    strt_time = datetime.datetime.now()
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
    end_time = datetime.datetime.now() - strt_time
    print("Number of month",end_time)
    return months_of_experience


def extract_experience(experience_list):

    strt_time = datetime.datetime.now()
    total = {}
    count = 1
    for line in experience_list:

        experience = re.search(
            r'(?P<fmonth>\w+.\d\d\d\d)\s*(\D|to)\s(?P<smonth>\w+.\d\d\d\d|present|Present)',
            line,
            re.I
        )
        if experience:
            date_name = line[experience.start():experience.end()]
            exp_name = (line[:experience.start()])

            if exp_name == "":
                if count is not 1:
                    t = re.sub('\s+','',experience_list[count-2])
                    if t is '':
                        s_count = count
                        while True:
                            s = re.sub('\s+','',experience_list[s_count])
                            if s is not '':
                                break
                            s_count = s_count + 1
                        exp_name = experience_list[s_count]
                    else:
                        exp_name = experience_list[count - 1]

                else:
                    exp_name = experience_list[count-2]

            exp_ = (experience.groups())
            if exp_[2] == "Present":
                exp_n = str(exp_[2]).lower()
                exp_month = (get_number_of_months_from_dates(exp_[0], exp_n))
            else:
                exp_month = (get_number_of_months_from_dates(exp_[0], exp_[2]))
            total[count] = {'Experience Name': exp_name, "Month": exp_month,"Date_name":date_name}
            count = count + 1
    end_time = datetime.datetime.now() - strt_time
    print("EXT EXPERIENCE",end_time)
    return total


def get_skill_months(experience_list, text_raw,nlp):
    strt_time = datetime.datetime.now()
    exp_list = list(experience_list.keys())
    count = 0
    mounthly = {}

    for i in exp_list:
        if len(exp_list) > count+1:
            start = re.search(experience_list[i]['Date_name'], text_raw)
            end = re.search(experience_list[i+1]['Date_name'], text_raw[start.start():])
            try:
                skills_t = nlp(text_raw[start.start():end.start()])
            except AttributeError:
                #print("STRING EXP",experience_list[i]['Experience Name'])
                count = count + 1
                continue
            noun_chunks = list(skills_t.noun_chunks)
            mounthly[count+1] = {'Experience Name': experience_list[i]['Experience Name'],
                                 "Skills": extract_skills(skills_t, noun_chunks),
                                 "Month": experience_list[i]['Month']}
        else:
            start = re.search(experience_list[i]['Date_name'], text_raw)
            if start is not None:
                skills_t = nlp(text_raw[start.start():])
                noun_chunks = list(skills_t.noun_chunks)
                mounthly[count+1] = {'Experience Name': experience_list[i]['Experience Name'],
                                     "Skills": extract_skills(skills_t, noun_chunks),
                                     "Month": experience_list[i]['Month']}
        count = count+1
    end_time = datetime.datetime.now() - strt_time
    print("GET SKILL MONTH",end_time)

    return mounthly


def job_listing_years_ext(text_raw):
    strt_time = datetime.datetime.now()
    text_raw_l = text_raw.lower()
    exp = None
    text_raw_l = re.sub(r'[?|$|.|!|,]', r'', text_raw_l)
    text_raw_l = text_raw_l.split("\n")
    for i in text_raw_l:
        for word in SENIORITY:
            found = re.search(word, i)
            if found:
                found_str = i[found.start():found.end()]
                if found_str in EXPERIENCE_KEYWORDS:
                    before_keyword = i[:found.start()].split()
                    if len(before_keyword)>1:
                        if before_keyword[-2] == 'to' or before_keyword[-2] == 'than' or before_keyword[-2] == 'of':
                            before_keyword[-2] = before_keyword[-3]
                        experience_definition = before_keyword[-2:]
                    elif len(before_keyword)>0:
                        experience_definition = before_keyword[-1:]
                    else:
                        return None
                    experience_definition = ' '.join(experience_definition)
                    print("EXPERIENCe DEFINISYON", experience_definition, "ismail gotdu")

                    year = re.search(r"([0-9]+\-[0-9]+)|([a-z]+ [0-9(-^)]+\+|[a-z]+ [0-9(-^)]+|[a-z]+ [0-9]+[^-])|([0-9]+[^-]\+|[0-9]+)|([a-z]+\. [0-9])",experience_definition)

                    # year = experience_definition[year.start():year.end()]
                    exp = {}
                    if year:
                        if year.group(1):
                            print("I am in group 2")
                            year = year.group(1).split('-')
                            exp = {"min":year[0],'max':year[1]}
                            return exp

                        if year.group(2):
                            print("I am in group 2")
                            # for phrases as min of less, than up to
                            min_key = ['min','minimum','least','more']
                            max_key = ['max','maximum','less','up']
                            matched_str = year.group(2)
                            matched_str = matched_str.split()
                            phrase = matched_str[0]
                            if phrase in min_key:
                                exp = {"min":matched_str[1], 'max':"100"}
                            elif phrase in max_key:
                                exp = {"min": '0', 'max': matched_str[1]}
                            else:
                                if matched_str[1][-1] == '+':
                                    exp = {"min": matched_str[1][:-1], 'max': "100"}
                                else:
                                    exp = {"min": matched_str[1], "max": matched_str[1]}

                                # print(year.group(2),"group 2 ext")

                        if year.group(3):
                            print("I am in group 3")
                            year = year.group(3)
                            if year[-1] == '+':
                                year = year[:-1]
                                exp = {'min':year,'max':'100'}
                            else:
                                exp = {'min':year,'max':year}
                            return exp
                        # if year.group(4):
                        #     print("I am in group 4")
                        #     year = year.group(4).split()
                        #     if year[0] == 'min.':
                        #         exp = {'min':year[1],'max':"100"}
                        #     elif year[0] == 'max.':
                        #         exp = {'min': 0, 'max': year[1]}
                        #     else:
                        #         print("group 4 exit")
                elif found_str == "junior":
                    exp = {'min': '2', 'max': '100'}
                elif found_str == "mid":
                    exp = {'min': '3', 'max': '5'}
                elif found_str == "senior":
                    exp = {'min': '5', 'max': '100'}

    # 10-15 years of experience
    # minimum 3 years of experience
    # 10+ years of experience
    # max. 2 years of experience
    # minumum of 3 years of experience
    # least 3 years
    # up to 5 years  years of experience
    # more than 5 years of experience
    # less than 5 years of experience
    # mnihad. 5 years of experience
    # nihad 5 years of experience
    # nihad 5-10 years of exp
    end_time = datetime.datetime.now() - strt_time
    print("JOB LISTING YEARS EXT",end_time)
    return exp

# def refine_score_by_skills(experience_duration_totals_dict, listing_exp_len_min, score):
#     print(experience_duration_totals_dict, listing_exp_len_min, score)
#     for skill, duration in experience_duration_totals_dict.items():
#         if abs(duration-listing_exp_len_min) < 13:
#             if 0 < score < 40:
#                 score = score + 12
#             elif 40 < score < 60:
#                 score = score + 10
#             elif 60 < score < 80:
#                 score = score + 5
#             elif 80 < score < 90:
#                 score = score + 3
#     return score
