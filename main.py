from pyjooblaparser import ResumeParser


def main():
    resume = ResumeParser('./sample_cvs/nihad-azimli-resume.pdf')
    print(resume.get_full_raw_text())


if __name__ == '__main__':
    main()