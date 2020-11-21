import csv
from pyresparser import ResumeParser


def main():
    # csv_file = open("skills.csv")
    #
    # reader = csv.reader(csv_file, delimiter=',')
    # rows = list(reader)[0]
    # print(rows)
    data = ResumeParser('./CV_files/BegumUnver-CV2020_1').get_extracted_data()
    print(data)


if __name__ == '__main__':
    main()
