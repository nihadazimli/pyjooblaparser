import io
import os
from . import utils


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
            'skills': None
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

        self.__text_raw = utils.extract_text(self.__resume, ext)

        self.__populate_details()

    def get_details(self):
        return self.__details

    def get_full_raw_text(self):
        return self.__text_raw

    def __populate_details(self):
        # To be populated
        pass
