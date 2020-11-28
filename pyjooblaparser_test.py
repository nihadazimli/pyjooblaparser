from pyjooblaparser import ResumeParser
from pyjooblaparser import ListingParser
import pprint
def main():
    resume = ResumeParser("./sample_cvs/BK_746_2-converted.pdf")
    text ="./clusters/text.txt"
    listing = ListingParser(text)
    resume_details = resume.get_details()
    resume_skills = resume.get_details()['skills']
    #print(resume_details)
    # dict_test = {'a':3,'b':3,'c':3}
    #
    # print(len(dict_test))
    #
    # print(listing.cluster_divider())
    pp = pprint.PrettyPrinter(width=41, compact=True)
    pp.pprint(resume_details)


if __name__ == '__main__':
    main()
