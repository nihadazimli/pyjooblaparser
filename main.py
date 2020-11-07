from pyjooblaparser import ResumeParser


def main():
    resume = ResumeParser('./sample_cvs/Ismayil\'s Resume.pdf')

    print(resume.get_details())


if __name__ == '__main__':
    main()
