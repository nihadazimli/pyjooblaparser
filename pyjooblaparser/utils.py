# Libraries to be used
import docx2txt
import textract
from nltk import SnowballStemmer
import xlsxwriter
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
from collections import OrderedDict


##CONSTANTS###
STOPWORDS = set(stopwords.words('english'))
YEAR = r'(((20|19)(\d{2})))'
MONTHS_SHORT = r'(jan)|(feb)|(mar)|(apr)|(may)|(jun)|(jul)|(aug)|(sep)|(oct)|(nov)|(dec)'
MONTHS_LONG = r'(january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december)'
MONTH = r'(' + MONTHS_SHORT + r'|' + MONTHS_LONG + r')'
EDUCATION = ['UNIVERSITY', 'B.E.', 'B.E', "B.Sc", 'ME', 'M.E', 'M.E.', 'MS', 'M.S', 'BTECH', 'MTECH',
             'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII', 'PHD', 'BS', 'HIGH SCHOOL', 'COLLEGE', 'SCHOOL', 'BSC', 'MSC'
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
          "bahcesehir university",
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


def extract_text(resume_full_path, ext):
    # INPUTS
    # resume_full_path: full file path of CV
    # ext: extension of CV file (e.g. .pdf)
    if ext == '.pdf':
        text_raw = extract_text_from_pdf(resume_full_path)
    # elif ext == '.docx':
    #     text_raw = extract_text_from_docx(resume_full_path)
    else:
        text_raw = extract_text_from_any(resume_full_path)

    return text_raw


def refine_score_by_experience(listing_exp_len, total_exp_month, score):
    if 0 < listing_exp_len < 24:
        if total_exp_month > 36:
            score = score - (total_exp_month - 36) * 1.5
    elif 24 < listing_exp_len < 60:
        if 0 < total_exp_month < 24:
            score = score - (24 - total_exp_month) * 1.5
        elif total_exp_month > 72:
            score = score - (total_exp_month - 12) * 1.2
    elif 60 < listing_exp_len < 120:
        if 0 < total_exp_month < 60:
            score = score - (60 - total_exp_month) * 1
        if total_exp_month > 120:
            score = score - (total_exp_month - 60) * 0.6
    elif listing_exp_len > 120:
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

    return experience_duration


def extract_name():
    # To be populated
    pass


def top100(text):
    text = text.lower()
    for i in TOP100:
        search = re.findall(i, text)
        if len(search) > 0:
            return search[0]


def extract_department_listing(text):
    found = ""
    found_arr = []
    for i in BACHELORS:
        found = re.findall(i, text.lower())
        if found:
            found_arr.append(found[0].lower())

    return found_arr


def matcher(found_arr, dep):
    for i in found_arr:
        s = re.findall(dep, i)
        if len(s) > 0:
            return s
    return None


from concurrent.futures import ProcessPoolExecutor


def extract_skills2(text_raw, noun_chunks, skills_file=None):

    pool = ProcessPoolExecutor(2)

    array1 = [text_raw[:int(len(text_raw) / 2)], noun_chunks[:int(len(noun_chunks) / 2)], None]
    array2 = [text_raw[int(len(text_raw) / 2):], noun_chunks[int(len(noun_chunks) / 2):], None]
    future = pool.submit(lambda d: extract_skills2(*d), array1)
    future = pool.submit(lambda d: extract_skills2(*d), array1)
    return future.result()


def extract_skills(text_raw, noun_chunks, skills_file=None):

    '''
    Helper function to extract skills from spacy nlp text
    :param text_raw: object of `spacy.tokens.doc.Doc`
    :param noun_chunks: noun chunks extracted from nlp text
    :return: list of skills extracted
    '''

    if len(text_raw) > 1:
        tokens = text_raw.text.split()
    else:
        return {}
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
        if count < len(tokens) - 1:
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


def cluster_finder(text_raw, this, soft=False):
    text = text_raw.strip(":")
    text = text.lower()
    text = text.split("\n")
    try:
        file = open(this, "r")
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
            s = re.findall(i, k)
            if len(s) > 0 and i != '':
                label.append(s)
                ste = re.compile(s[len(s) - 1])
                big = (" ".join(text))
                t = ste.search(big)
                ve = t.start()
                line.append(ve)
    if soft:
        return label

    return label, line


def extract_education(nlp_text):


    bachelor = ""
    uni = ""
    '''
    Helper function to extract education from spacy nlp text
    :param nlp_text: object of `spacy.tokens.doc.Doc`
    :return: tuple of education degree and year if year if found else only returns education degree
    '''
    edu = {}
    # Extract education degree

    nlp_text_n = []
    found = False
    for i in nlp_text:
        tex = re.sub(r'&', " and ", i)
        tex = re.sub(r'[\n|[?|$|.|!|,]', ' ', tex)
        tex = re.sub(r'\s+', ' ', tex)
        s = tex.lower()
        r = re.search("university", s)
        t = re.search("college", s)
        word = "university"
        if r or t:
            if t:
                word = "college"
            arr = s.split()
            tex = tex.split()

            index = arr.index(word)
            if len(arr) > index + 1:
                if arr[index + 1] == 'of':

                    if tex[index - 1][0].isupper():

                        uni = arr[index - 1] + " " + arr[index] + " " + "of" + " " + arr[index + 2]
                    else:
                        uni = arr[index] + " " + "of" + " " + arr[index + 2]
                else:
                    uni = arr[index - 1] + " " + arr[index]
        nlp_text_n.append(s)

    text = ' '.join(nlp_text_n)

    for i in BACHELORS:
        s = re.findall(i, text)

        if len(s) > 0:
            bachelor = s[0]
            break

    years = re.findall(YEAR, text)

    if len(years) > 0:

        educ = {"UNI": uni, "DEP": bachelor, 'year': years[len(years) - 1][0]}
    else:
        educ = {"UNI": uni, "DEP": bachelor, 'year': None}



    return educ


def extract_entity_sections_grad(text):
    '''
    Helper function to extract all the raw text from sections of
    resume specifically for graduates and undergraduates
    :param text: Raw text of resume
    :return: dictionary of entities
    '''
    text = re.sub("/", " ", text)
    text_split = [i.strip() for i in text.split('\n')]
    text_split2 = text_split
    # sections_in_resume = [i for i in text_split if i.lower() in sections]
    entities = {}
    count = 0
    for i in text_split2:
        count = count + 1
        experience = re.search(r'(?P<fmonth>\w+.\d\d\d\d)\s*(\D|to)\s*(?P<smonth>\w+.\d\d\d\d|present|recent)', i, re.I)
        if experience:
            try:
                if text_split2[count - 1] != '' and text_split2[count - 3] != '' \
                        and len(text_split2[count - 1].split()) < 7:
                    text_split2[count - 3] = text_split2[count - 3] + " " + text_split2[count - 1]

                    text_split2.pop(count - 1)
            except IndexError:
                #
                if text_split2[count - 1] == '':
                    text_split2 = text_split2[count - 1] + text_split2[count]
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


    return entities


def entity_grad_2(text):
    text = re.sub(":|,|\.", " ", text)
    text = re.sub("\n", " ", text)
    text = re.sub("\t", " ", text)
    text = re.sub("\s+", " ", text)
    text2_U = text.split(" ")
    text2 = text.lower().split(" ")

    t = text.lower().split()
    try:
        education = text2.index("university")
    except:
        education = text2.index("college")
    experiences = re.findall(r'(?P<fmonth>\w+.\d\d\d\d)\s*(\D|to)\s*(?P<smonth>\w+.\d\d\d\d|present|recent)', text,
                             re.I)

    try:
        if get_number_of_months_from_dates(experiences[0][0], experiences[0][2]) is not 0:

            experience = t.index(experiences[0][0].split(" ")[-1].lower())

        else:
            experiences = experiences[1:]
            experience = t.index(experiences[0][-1].split(" ")[-1].lower())


    except IndexError:
        experience = t.index(experiences[0].split(" ")[0].lower())
    if education > experience:
        exp_end = len(t) - 1
        edu_end = len(t) - 1
    else:
        edu_end = experience - 1
        exp_end = len(t) - 1

    edu = text2_U[education - 30:edu_end]
    edu = ' '.join(edu)
    edu = edu.split('\n')
    exp = text2_U[experience - 15:exp_end]
    exp = ' '.join(exp)
    for i in experiences:
        s = ' '.join(i)
        exp = re.sub(s, str(s + " \n"), exp)
    exp = exp.split("\n")

    return {"education": edu,
            "experience": exp}


def get_total_experience(experience_list):
    '''
    Wrapper function to extract total months of experience from a resume
    :param experience_list: list of experience text extracted
    :return: total months of experience
    '''
    exp_ = []
    for line in experience_list:
        experience = re.search(
            r'(?P<fmonth>\w+.\d\d\d\d)\s*(\D|to)\s*(?P<smonth>\w+.\d\d\d\d|present|recent)',
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
    if date2.lower() == 'present' or date2.lower() == 'recent':
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
            r'(?P<fmonth>\w+.\d\d\d\d)\s*(\D|to)\s(?P<smonth>\w+.\d\d\d\d|present|Present|Recent|recent)',
            line,
            re.I
        )
        if experience:
            date_name = line[experience.start():experience.end()]
            exp_name = (line[:experience.start()])
            words = exp_name.split()
            cons_uppper = re.findall(
                '([A-Z][a-z]+(?=\s[A-Z])(?:\s[A-Z][a-z]+)+)|([A-Z][A-Z]+(?=\s[A-Z])(?:\s[A-Z][A-Z]+)+)', exp_name)
            if len(cons_uppper) > 1:
                if len(cons_uppper[1]) > 0:

                    try:
                        cons_uppper = cons_uppper[1][:4]
                    except:
                        cons_uppper = cons_uppper
                    exp_name = " ".join(cons_uppper)
            elif len(cons_uppper) > 0 and len(cons_uppper[0]) > 0:
                try:
                    cons_uppper = cons_uppper[0][:4]
                except:
                    cons_uppper = cons_uppper
                exp_name = " ".join(cons_uppper)
            elif len(words) > 2:
                exp_name = " ".join(words[:2])

            if exp_name == "":
                if count is not 1:
                    t = re.sub('\s+', '', experience_list[count - 2])
                    if t is '':
                        s_count = count
                        while True:
                            s = re.sub('\s+', '', experience_list[s_count])
                            if s is not '':
                                break
                            s_count = s_count + 1
                        exp_name = experience_list[s_count]
                    else:
                        exp_name = experience_list[count - 1]

                else:
                    exp_name = experience_list[count - 2]

            exp_ = (experience.groups())
            if exp_[2] == "Present":
                exp_n = str(exp_[2]).lower()
                exp_month = (get_number_of_months_from_dates(exp_[0], exp_n))
            else:
                exp_month = (get_number_of_months_from_dates(exp_[0], exp_[2]))
            total[count] = {'Experience Name': exp_name, "Month": exp_month, "Date_name": date_name}
            count = count + 1

    return total


def get_skill_months(experience_list, text_raw, nlp):
    exp_list = list(experience_list.keys())
    count = 0
    mounthly = {}

    for i in exp_list:
        if len(exp_list) > count + 1:
            start = re.search(experience_list[i]['Date_name'], text_raw)
            end = re.search(experience_list[i + 1]['Date_name'], text_raw[start.start():])
            try:
                if end.start() < start.start():
                    skills_t = nlp(text_raw[end.start():start.start()])
                elif end.start() > start.start():
                    skills_t = nlp(text_raw[start.start():end.start()])

            except AttributeError:
                #
                count = count + 1
                continue
            noun_chunks = list(skills_t.noun_chunks)
            mounthly[count + 1] = {'Experience Name': experience_list[i]['Experience Name'],
                                   "Skills": extract_skills(skills_t, noun_chunks),
                                   "Month": experience_list[i]['Month']}
        else:
            start = re.search(experience_list[i]['Date_name'], text_raw)
            if start is not None:
                skills_t = nlp(text_raw[start.start():])
                noun_chunks = list(skills_t.noun_chunks)
                mounthly[count + 1] = {'Experience Name': experience_list[i]['Experience Name'],
                                       "Skills": extract_skills(skills_t, noun_chunks),
                                       "Month": experience_list[i]['Month']}
        count = count + 1

    return mounthly


def job_listing_years_ext(text_raw):
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
                    if len(before_keyword) > 1:
                        if before_keyword[-2] == 'to' or before_keyword[-2] == 'than' or before_keyword[-2] == 'of':
                            before_keyword[-2] = before_keyword[-3]
                        experience_definition = before_keyword[-2:]
                    elif len(before_keyword) > 0:
                        experience_definition = before_keyword[-1:]
                    else:
                        return None
                    experience_definition = ' '.join(experience_definition)

                    year = re.search(
                        r"([0-9]+\-[0-9]+)|([a-z]+ [0-9(-^)]+\+|[a-z]+ [0-9(-^)]+|[a-z]+ [0-9]+[^-])|([0-9]+[^-]\+|[0-9]+)|([a-z]+\. [0-9])",
                        experience_definition)

                    exp = {}
                    if year:
                        if year.group(1):
                            year = year.group(1).split('-')
                            exp = {"min": year[0], 'max': year[1]}
                            return exp

                        if year.group(2):
                            print("I am in group 2")
                            # for phrases as min of less, than up to
                            min_key = ['min', 'minimum', 'least', 'more']
                            max_key = ['max', 'maximum', 'less', 'up']
                            matched_str = year.group(2)
                            matched_str = matched_str.split()
                            phrase = matched_str[0]
                            if phrase in min_key:
                                exp = {"min": matched_str[1], 'max': "100"}
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
                                exp = {'min': year, 'max': '100'}
                            else:
                                exp = {'min': year, 'max': year}
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

    return exp


def refine_score_by_skills(experience_duration_totals_dict, listing_exp_len_min, score):
    for skill, duration in experience_duration_totals_dict.items():
        if abs(duration - listing_exp_len_min) < 13:
            if 0 < score < 40:
                score = score + 12
            elif 40 < score < 60:
                score = score + 10
            elif 60 < score < 80:
                score = score + 5
            elif 80 < score < 90:
                score = score + 3
    return score


def refine_score_by_education(cv_data, candidate_level, listing_d_education):

    bonus = 0

    if cv_data['top100'] is not None:
        bonus_university = 10
    dep_cv = cv_data['education']['DEP']
    dep_listing = listing_d_education
    if len(dep_cv) > 0 and len(dep_listing) > 0:
        stemmer = SnowballStemmer("english")
        dep_cv_arr = dep_cv.split()
        if len(dep_cv_arr) == 2:
            for k in dep_cv_arr:
                for i in dep_listing:
                    z = i.split()
                    z = z[0]
                    dep1 = stemmer.stem(z)
                    dep2 = stemmer.stem(k)
                    if dep1 == dep2:
                        if candidate_level == 'junior':
                            bonus = bonus + 10
                            bonus_department = 10
                        elif candidate_level == 'medior':
                            bonus = bonus + 5
                            bonus_department = 5
                        elif candidate_level == 'senior':
                            bonus = bonus + 3
                            bonus_department = 3
                        break
                    print("DEPARTMENTS", dep1, dep2)
        else:
            for i in dep_listing:
                dep1 = stemmer.stem(i)
                dep2 = stemmer.stem(dep_cv)
                print("DEPARTAMENTS", dep1, dep2)

    return bonus


def convert_to_excel(cv_name,listing_name, upload_folder, final_score, skills_cv,
                     matching_skills_must_dict, matching_skills_good_dict, matching_skills_soft_dict,
                     score_must, score_good, score_soft):
    workbook_filename = cv_name.split('.')[0] + '__' + listing_name.split('.')[0] + '.xlsx'
    workbook = xlsxwriter.Workbook(upload_folder + '/' + workbook_filename)
    worksheet = workbook.add_worksheet()

    # Widen the first column to make the text clearer.
    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 20)
    worksheet.set_column('D:D', 10)
    worksheet.set_column('E:E', 20)
    worksheet.set_column('F:F', 20)
    worksheet.set_column('G:G', 10)
    worksheet.set_column('H:H', 20)
    worksheet.set_column('I:I', 10)
    worksheet.set_column('J:J', 20)
    worksheet.set_column('K:K', 10)

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': True})

    # Write some simple text.
    worksheet.write('A1', 'CV ID', bold)
    worksheet.write('B1', 'JOB LISTING ID', bold)
    worksheet.write('C1', 'EXPECTED SCORE', bold)
    worksheet.write('D1', 'SCORE', bold)
    worksheet.write('E1', 'CV KEYWORDS', bold)
    worksheet.write('F1', 'CLUSTER MUST HAVE MATCH', bold)
    worksheet.write('G1', 'CLUSTER MUST HAVE SCORE', bold)
    worksheet.write('H1', 'CLUSTER GOOD TO HAVE MATCH', bold)
    worksheet.write('I1', 'CLUSTER GOOD TO HAVE SCORE', bold)
    worksheet.write('J1', 'CLUSTER SOFT MATCH', bold)
    worksheet.write('K1', 'CLUSTER SOFT SCORE', bold)

    # Text with formatting.
    worksheet.write('A2', cv_name)
    worksheet.write('B2', listing_name)
    worksheet.write('C2', '')
    worksheet.write('D2', final_score)

    count = 1
    for k, v in skills_cv.items():
        count += 1
        worksheet.write('E' + str(count), k + ' : ' + str(v))

    count = 1
    for k, v in matching_skills_must_dict.items():
        count += 1
        worksheet.write('F' + str(count), k + ' : ' + str(v))
    worksheet.write('G2', score_must)

    count = 1
    for k, v in matching_skills_good_dict.items():
        count += 1
        worksheet.write('H' + str(count), k + ' : ' + str(v))
    worksheet.write('I2', score_good)

    count = 1
    for k, v in matching_skills_soft_dict.items():
        count += 1
        worksheet.write('J' + str(count), k + ' : ' + str(v))
    worksheet.write('K2', score_soft)

    workbook.close()
    return workbook_filename


def modify_cluster(skills_listing_must, skills_listing_good):
    modified_skills_listing_good = skills_listing_good
    modified_skills_listing_must = skills_listing_must
    if len(skills_listing_must) > 10:
        ordered_dict = OrderedDict(sorted(skills_listing_must.items(), key=lambda item: item[1],reverse=True))
        top_dict = dict(ordered_dict.items())
        while len(top_dict) > 10:
            item_tuple = top_dict.popitem()
            try:
                modified_skills_listing_good[item_tuple[0]] = item_tuple[1]
            except:
                modified_skills_listing_good[item_tuple[0]] += item_tuple[1]

        modified_skills_listing_must = dict(top_dict)
    if len(skills_listing_must) < 2:
        if len(skills_listing_good) > 1:
            count = 0
            for item in skills_listing_good:
                count += 1
                try:
                    modified_skills_listing_must[item] = skills_listing_good[item]
                    modified_skills_listing_good[item] = None
                except:
                    modified_skills_listing_must[item] += skills_listing_good[item]
                    modified_skills_listing_good[item] = None
                if count == 10:
                    break
    return modified_skills_listing_must, modified_skills_listing_good


def modify_cluster_favor(skills_listing_must, skills_listing_good, intersection_list_must):
    modified_skills_listing_good = {}
    modified_skills_listing_must = {}
    match_skill_counter = 0
    modified_intersection_list_must = []
    if len(skills_listing_must) > 10:
        ordered_dict = OrderedDict(sorted(skills_listing_must.items(), key=lambda item: item[1],reverse=True))
        top_dict = dict(ordered_dict.items())
        for match_skill in intersection_list_must:
            if match_skill_counter < 10:
                try:
                    top_dict.pop(match_skill)
                    modified_intersection_list_must.append(match_skill)
                    modified_skills_listing_must[match_skill] = skills_listing_must[match_skill]
                    match_skill_counter += 1
                except:
                    pass
        while len(top_dict) > 10:
            item_tuple = top_dict.popitem()
            try:
                modified_skills_listing_good[item_tuple[0]] = item_tuple[1]
            except:
                modified_skills_listing_good[item_tuple[0]] += item_tuple[1]

    if len(skills_listing_must) < 2:
        if len(skills_listing_good) > 1:
            count = 0
            for item in skills_listing_good:
                count += 1
                try:
                    modified_skills_listing_must[item] = skills_listing_good[item]
                    modified_skills_listing_good[item] = None
                except:
                    modified_skills_listing_must[item] += skills_listing_good[item]
                    modified_skills_listing_good[item] = None
                if count == 10:
                    break

    return modified_skills_listing_must, modified_skills_listing_good, modified_intersection_list_must
