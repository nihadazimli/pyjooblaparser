import io
import os
import re
from . import utils
from . import config
import spacy

nlp = spacy.load('en_core_web_sm')


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
            'education': None,
            'experience': None,
            'total_experience': None,
            'top100':None
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


        global nlp
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
        global nlp
        # personal_information_seperator_regex = config.PERSONAL_INFORMATION_SEPERATOR
        # personal_information_raw_text = re.split(personal_information_seperator_regex, self.__text_raw.lower())
        #this = self.__nlp
        entities = utils.extract_entity_sections_grad(self.__text_raw)
        #entities = utils.entity_grad_2(self.__text_raw)
        self.__details['email'] = utils.extract_email(self.__text_raw)
        self.__details['mobile_number'] = utils.extract_number(self.__text_raw)
        self.__details['skills'] = utils.extract_skills(self.__nlp,self.__noun_chunks,None)
        ex = utils.extract_experience(entities['experience'])

        e = nlp('\n'.join(entities['education']))
        print('exprert',ex)
        self.__details['education'] = utils.extract_education([sent.string.strip() for sent in e.sents])
        self.__details['total_experience'] = utils.get_total_experience(entities['experience'])
        print(self.__details['total_experience'])
        self.__details['experience'] = utils.get_skill_months(ex,'\n'.join(entities['experience']),nlp)
        self.__details['top100'] = utils.top100(self.__text_raw)

        return self

    def extract_entities_wih_custom_model(custom_nlp_text):
        '''
        Helper function to extract different entities with custom
        trained model using SpaCy's NER
        :param custom_nlp_text: object of `spacy.tokens.doc.Doc`
        :return: dictionary of entities
        '''
        entities = {}
        for ent in custom_nlp_text.ents:
            if ent.label_ not in entities.keys():
                entities[ent.label_] = [ent.text]
            else:
                entities[ent.label_].append(ent.text)
        for key in entities.keys():
            entities[key] = list(set(entities[key]))
        return entities
