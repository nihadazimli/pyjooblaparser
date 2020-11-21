from pyjooblaparser import ResumeParser
from pyjooblaparser import ListingParser

def main():
    resume = ResumeParser('./sample_cvs/nihad-azimli-resume.pdf')
    text ="./clusters/text.txt"
    listing = ListingParser(text)
    resume_skills = resume.get_details()['skills']

    dict_test = {'a':3,'b':3,'c':3}

    print(len(dict_test))

    print(listing.cluster_divider())


if __name__ == '__main__':
    main()
