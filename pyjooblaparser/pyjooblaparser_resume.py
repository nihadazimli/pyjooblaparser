import io
import os
import re
from . import utils
from . import config
import spacy

class ResumeParser(object):

    def __init__(
        self,
        resume
    ):
        self.__details = {
            'name': None,
            'email': None,
            'mobile_number': None,
            'location': None,
            'skills': None,
            'education':None,
            'experience':None,
            'total_experience':None
            #'edu2':None
        }
        self.__resume = resume

        if not isinstance(self.__resume, io.BytesIO):
            try:
                ext = os.path.splitext(self.__resume)[1]
            except:
                ext = '.txt'
                print("as you did not enter extension to file default value is set")
                print("default is " + ext)
        else:
            ext = '.' + self.__resume.name.split('.')[1]

        nlp = spacy.load('en_core_web_sm')

        self.__text_raw = utils.extract_text(self.__resume, ext)
        self.__text = ' '.join(self.__text_raw.split())
        self.__nlp = nlp(self.__text)
        self.__noun_chunks = list(self.__nlp.noun_chunks)

        self.__populate_details()

    def get_details(self):
        return self.__details

    def get_full_raw_text(self):
        return self.__text_raw

    def __populate_details(self):

        # personal_information_seperator_regex = config.PERSONAL_INFORMATION_SEPERATOR
        # personal_information_raw_text = re.split(personal_information_seperator_regex, self.__text_raw.lower())
        #this = self.__nlp
        entities = utils.extract_entity_sections_grad(self.__text_raw)
        #self.__details['education'] = utils.extract_education ([sent.string.strip() for sent in this.sents])
        self.__details['email'] = utils.extract_email(self.__text_raw)
        self.__details['mobile_number'] = utils.extract_number(self.__text_raw)
        self.__details['skills'] = utils.extract_skills(self.__nlp,self.__noun_chunks,None)
        self.__details['experience'] = utils.extract_experience(entities['experience'])
        nlp = spacy.load('en_core_web_sm')
        e = nlp('\n'.join(entities['education']))
        self.__details['education'] = utils.extract_education([sent.string.strip() for sent in e.sents])
        self.__details['total_experience'] = utils.get_total_experience(entities['experience'])
        #self.__details['edu2'] = utils.extract_education2(entities['education'])
        return self
