from pyjooblaparser import ResumeParser
from pyjooblaparser import ListingParser

def main():
    resume = ResumeParser('./sample_cvs/Ismayil\'s Resume.pdf')
    text ="./clusters/text.txt"
    listing = ListingParser(text)
    print(resume.get_details())
    print(listing.cluster_divider(text,"./clusters/must_have.txt","./clusters/good_to_have.txt"))


if __name__ == '__main__':
    main()
