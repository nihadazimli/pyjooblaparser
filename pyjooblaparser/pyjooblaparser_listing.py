import io
import os
import re
from . import utils
from . import config
import spacy

class ListingParser(object):

    def __init__(
        self,
        listing,
        skills_file=None,
    ):
        self.__details = {
            'skills': None
        }
        self.__listing = listing

        if not isinstance(self.__listing, io.BytesIO):
            try:
                ext = os.path.splitext(self.__listing)[1]
            except:
                ext = '.txt'
                print("as you did not enter extension to file default value is set")
                print("default is " + ext)
        else:
            ext = '.' + self.__listing.name.split('.')[1]

        nlp = spacy.load('en_core_web_sm')

        self.__text_raw = utils.extract_text(self.__listing, ext)

        self.__text = ' '.join(self.__text_raw.split())
        self.__nlp = nlp(self.__text)
        self.__noun_chunks = list(self.__nlp.noun_chunks)

    def cluster_divider(self,__text_raw , file1,file2):
        nlp = spacy.load('en_core_web_sm')
        string_must, must_index = utils.cluster_finder(self.__text_raw, file1)
        string_good, good_index = utils.cluster_finder(self.__text_raw, file2)
        text = self.__text_raw
        if len(must_index) > 0 and len(good_index) > 0:
            must_index_i = min(must_index)
            good_index_i = min(good_index)
            nlp_must = nlp(text[must_index_i:good_index_i])
            noun_chunks_must = list(nlp_must.noun_chunks)
            must_skills = utils.extract_skills(nlp_must,noun_chunks_must)
            nlp_good = nlp(text[good_index_i:])
            noun_chunks_good = list(nlp_good.noun_chunks)
            good_skills = utils.extract_skills(nlp_good, noun_chunks_good)
            skills = {"Cluster 1": must_skills, "Cluster 2": good_skills}

        return skills

    def __populate_details(self):
        self.__details['skills'] = utils.extract_skills(self.__nlp,self.__noun_chunks,None)
        return self