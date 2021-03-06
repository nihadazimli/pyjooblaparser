from flask import Flask, render_template, request, abort, send_file, url_for, send_from_directory, after_this_request
from werkzeug.utils import secure_filename
import os
import config
import xlsxwriter
from pyjooblaparser import ResumeParser
from pyjooblaparser import ListingParser
from nltk import SnowballStemmer
from pyjooblaparser import utils

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FILES_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('file')

        file_type = request.form['Upload']
        print(file_type)
        if file_type == 'Listing':
            for file in files:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'] + config.LISTING_SUBFOLDER, filename))
        elif file_type == 'CV':
            for file in files:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'] + config.CV_SUBFOLDER, filename))
        return render_template("uploader.html")
    elif request.method == 'GET':
        return "Do not try to fool me :)\nYou should upload CV firstly"


@app.route('/list', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def dir_listing(req_path):
    CV_DIR = config.UPLOAD_FILES_DIR + config.CV_SUBFOLDER
    LISTING_DIR = config.UPLOAD_FILES_DIR + config.LISTING_SUBFOLDER

    # Joining the base and the requested path
    cv_abs_path = os.path.join(CV_DIR, req_path)
    listing_abs_path = os.path.join(LISTING_DIR, req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(cv_abs_path):
        return abort(404)
    if not os.path.exists(listing_abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(cv_abs_path):
        return send_file(cv_abs_path)
    if os.path.isfile(listing_abs_path):
        return send_file(listing_abs_path)

    # Show directory contents
    cv_files = os.listdir(cv_abs_path)
    listing_files = os.listdir(listing_abs_path)
    return render_template('files.html', cv_files=cv_files, listing_files=listing_files)


@app.route('/new_test')
def new_test():
    return render_template('new_test.html')


@app.route('/new_test_run', methods=['GET', 'POST'])
# def new_test_run():
#     if request.method == 'POST':
#
#         score = 0
#
#         files_cv = request.files.getlist('CV')
#
#         file_listing = request.files['LISTING']
#         filename_listing = secure_filename(file_listing.filename)
#         file_listing.save(os.path.join(app.config['UPLOAD_FOLDER'] + config.LISTING_SUBFOLDER, filename_listing))
#
#         listing_data = ListingParser(config.UPLOAD_FILES_DIR + config.LISTING_SUBFOLDER + '/' + filename_listing) \
#             .cluster_divider("./clusters/must_have.txt",
#                              "./clusters/good_to_have.txt",
#                              "./clusters/soft_skills.txt")
#
#         full_cv_score_list = []
#         for file_cv in files_cv:
#             score = 0
#             filename_cv = secure_filename(file_cv.filename)
#             file_cv.save(os.path.join(app.config['UPLOAD_FOLDER'] + config.CV_SUBFOLDER, filename_cv))
#
#             cv_data = ResumeParser(config.UPLOAD_FILES_DIR + config.CV_SUBFOLDER + '/' + filename_cv).get_details()
#             skills_cv = cv_data['skills']
#
#             if type(listing_data['Cluster 1']) is dict:
#                 skills_listing_must = listing_data['Cluster 1']
#             else:
#                 skills_listing_must = {}
#             if type(listing_data['Cluster 2']) is dict:
#                 skills_listing_good = listing_data['Cluster 2']
#             else:
#                 skills_listing_good = {}
#             if type(listing_data['Cluster 3']) is list:
#                 skills_listing_soft = listing_data['Cluster 3']
#             else:
#                 skills_listing_soft = []
#
#             try:
#                 intersection_list_must = list(set(skills_cv) & set(skills_listing_must.keys()))
#                 score_must = len(intersection_list_must) * config.WEIGHT_MUST
#                 score += score_must
#             except:
#                 intersection_list_must = {}
#
#             try:
#                 intersection_list_good = list(set(skills_cv) & set(skills_listing_good.keys()))
#                 score_good = len(intersection_list_good) * config.WEIGHT_GOOD
#                 score += score_good
#
#             except:
#                 intersection_list_good = {}
#
#             try:
#                 intersection_list_soft = list(set(skills_cv) & set(skills_listing_soft))
#                 score_soft = len(intersection_list_soft) * config.WEIGHT_SOFT
#                 score += score_soft
#             except:
#                 intersection_list_soft = []
#
#             total_score = len(skills_listing_must) * config.WEIGHT_MUST + len(
#                 skills_listing_good) * config.WEIGHT_GOOD + \
#                           len(skills_listing_soft) * config.WEIGHT_SOFT
#
#             final_score = str(score / total_score * 100)[:5]
#             full_cv_score_list.append(filename_cv + " is " + final_score)
#
#         return render_template('new_test_run.html',
#                                final_score_list=full_cv_score_list)
#     elif request.method == 'GET':
#         return "ASDASDASD"

@app.route('/tryAlgo')
def try_algo():
    CV_DIR = config.UPLOAD_FILES_DIR + config.CV_SUBFOLDER
    LISTING_DIR = config.UPLOAD_FILES_DIR + config.LISTING_SUBFOLDER

    cv_files = os.listdir(CV_DIR)
    listing_files = os.listdir(LISTING_DIR)

    return render_template('tryAlgo.html', cv_files=cv_files, listing_files=listing_files)


@app.route('/algorithm_result', methods=['GET', 'POST'])
def algorithm_result():
    if request.method == 'POST':
        cv_name = request.form['CV']
        listing_name = request.form['Listing']

        # Do your logic here
        cv_data = ResumeParser(config.UPLOAD_FILES_DIR + config.CV_SUBFOLDER + '/' + cv_name).get_details()
        skills_cv = cv_data['skills']
        experience = cv_data['experience']
        education = cv_data['education']

        experience_list = []
        experience_skills_list_total = []
        for x, y in experience.items():
            if len(y['Experience Name']) > 1:
                experience_list.append(y['Experience Name'] + " - " + str(y['Month']) + " month")
                experience_skills_str = ", ".join((k + ' : ' + str(v)) for k, v in y['Skills'].items())
                experience_skills_list_total.append(experience_skills_str.split(','))
            else:
                experience_list.append("Name cannot be parsed " + " - " + str(y['Month']) + " month")
                experience_skills_str = ", ".join((k + ' : ' + str(v)) for k, v in y['Skills'].items())
                experience_skills_list_total.append(experience_skills_str.split(','))
        skills_cv_list = skills_cv.keys()

        listing = ListingParser(config.UPLOAD_FILES_DIR + config.LISTING_SUBFOLDER + '/' + listing_name)

        listing_data = listing.cluster_divider("./clusters/must_have.txt", "./clusters/good_to_have.txt",
                                               "./clusters/soft_skills.txt")
        listing_d = listing.get_details()
        listing_exp_len = listing_d['years_of_exp']

        print("listing_exp_len", listing_exp_len)

        total_exp_month = 0
        for i in experience:
            total_exp_month = total_exp_month + experience[i]['Month']

        total_exp_year = total_exp_month / 12

        if 0 <= total_exp_year <= 3:
            candidate_level = 'junior'
        elif 4 <= total_exp_year <= 9:
            candidate_level = 'medior'
        elif 9 <= total_exp_year <= 100:
            candidate_level = 'senior'
        else:
            candidate_level = 'god'

        bonus_university = 0
        bonus_department = 0
        bonus_experience = 0

        bonus_university += utils.refine_score_by_education(cv_data, candidate_level, listing_d['education'])

        print("listing_exp_len", listing_exp_len)

        score = 0
        score_must = 0
        score_good = 0
        score_soft = 0

        listing_list_total_len = 0
        if type(listing_data['Cluster 1']) is dict:
            skills_listing_must = listing_data['Cluster 1']
            listing_list_total_len += len(skills_listing_must)
        else:
            skills_listing_must = {}
        if type(listing_data['Cluster 2']) is dict:
            skills_listing_good = listing_data['Cluster 2']
            listing_list_total_len += len(skills_listing_good)
        else:
            skills_listing_good = {}
        if type(listing_data['Cluster 3']) is list:
            skills_listing_soft = listing_data['Cluster 3']
            listing_list_total_len += len(skills_listing_soft)
        else:
            skills_listing_soft = []

        # skills_listing_must, skills_listing_good = utils.modify_cluster(skills_listing_must, skills_listing_good)
        intersection_list_total_len = 0
        experience_duration_totals_dict = {}
        skill_experience = 0.0
        listing_exp_month = int(listing_exp_len['min']) * 12
        try:
            intersection_list_must = list(set(skills_cv) & set(skills_listing_must.keys()))
            skills_listing_must, skills_listing_good, intersection_list_must = \
                utils.modify_cluster_favor(skills_listing_must, skills_listing_good,intersection_list_must)
            print("skills_listing_must", skills_listing_must)
            print("skills_listing_good", skills_listing_good)
            print("intersection_list_must", intersection_list_must)

            intersection_list_total_len += len(intersection_list_must)

            experience_duration_totals_dict = utils.experience_total_duration(experience, intersection_list_must)

            if total_exp_month - listing_exp_month > 0:
                for key, value in experience_duration_totals_dict.items():
                    if value - listing_exp_month > 0:
                        experience_value = float(value - listing_exp_month) / float(listing_exp_month)
                        if experience_value > 0.5:
                            skill_experience += 0.5
                        else:
                            skill_experience += experience_value
                print("skill_experience", skill_experience)

            if len(skills_listing_must.keys()) > len(intersection_list_must) + skill_experience:
                score_must = (len(intersection_list_must) + skill_experience) * config.WEIGHT_MUST
            else:
                score_must = len(skills_listing_must.keys()) * config.WEIGHT_MUST
            score += score_must
        except:
            intersection_list_must = {}

        try:
            intersection_list_good = list(set(skills_cv) & set(skills_listing_good.keys()))
            intersection_list_total_len += len(intersection_list_good)
            score_good = len(intersection_list_good) * config.WEIGHT_GOOD
            score += score_good

        except:
            intersection_list_good = {}

        try:
            intersection_list_soft = list(set(skills_cv) & set(skills_listing_soft))
            intersection_list_total_len += len(intersection_list_soft)
            score_soft = len(intersection_list_soft) * config.WEIGHT_SOFT
            score += score_soft
        except:
            intersection_list_soft = []

        print("experience_duration_totals_dict", experience_duration_totals_dict)
        matching_skills_must = intersection_list_must
        matching_skills_good = intersection_list_good
        matching_skills_soft = intersection_list_soft

        matching_skills_must_dict = {}
        for x in matching_skills_must:
            matching_skills_must_dict[x] = skills_listing_must[x]

        matching_skills_good_dict = {}
        for x in matching_skills_good:
            matching_skills_good_dict[x] = skills_listing_good[x]

        matching_skills_soft_dict = {}
        for x in matching_skills_soft:
            matching_skills_soft_dict[x] = skills_listing_soft[x]

        listing_skills_must = ", ".join((k + ' : ' + str(v)) for k, v in skills_listing_must.items())
        listing_skills_must = listing_skills_must.split(',')
        listing_skills_good = ", ".join((k + ' : ' + str(v)) for k, v in skills_listing_good.items())
        listing_skills_good = listing_skills_good.split(',')
        listing_skills_soft = ",".join(str(x)[2:-2] for x in skills_listing_soft)
        listing_skills_soft = listing_skills_soft.split(',')
        cv_skills_result = ", ".join((k + ' : ' + str(v)) for k, v in skills_cv.items())
        cv_skills_result = cv_skills_result.split(',')

        total_score = len(listing_skills_must) * config.WEIGHT_MUST + len(listing_skills_good) * config.WEIGHT_GOOD + \
                      len(listing_skills_soft) * config.WEIGHT_SOFT

        final_score_modified = score / total_score * 100

        bonus = bonus_department + bonus_university
        print("Bonus", bonus)
        final_score = final_score_modified + bonus
        final_score = str(final_score)[:5]

        score_must = str((score_must / (len(listing_skills_must) * config.WEIGHT_MUST)) * 100)[:5]
        score_good = str((score_good / (len(listing_skills_good) * config.WEIGHT_GOOD)) * 100)[:5]
        score_soft = str((score_soft / (len(listing_skills_soft) * config.WEIGHT_SOFT)) * 100)[:5]

        upload_folder_excel = app.config['UPLOAD_FOLDER']

        workbook_filename = utils.convert_to_excel(cv_name, listing_name, upload_folder_excel, final_score, skills_cv,
                                                   matching_skills_must_dict, matching_skills_good_dict,
                                                   matching_skills_soft_dict, score_must, score_good, score_soft)

        return render_template('test.html',
                               bonus_university=bonus_university,
                               bonus_department=bonus_department,
                               listing_month_of_exp=str(int(listing_exp_len['min']) * 12),
                               resume_month_of_exp=total_exp_month,
                               matching_skills_must=matching_skills_must,
                               matching_skills_good=matching_skills_good,
                               matching_skills_soft=matching_skills_soft,
                               matching_skills_must_count=len(matching_skills_must),
                               matching_skills_good_count=len(matching_skills_good),
                               matching_skills_soft_count=len(matching_skills_soft),
                               cv_skills=cv_skills_result,
                               listing_skills_must=listing_skills_must,
                               listing_skills_good=listing_skills_good,
                               listing_skills_soft=listing_skills_soft,
                               listing_skills_must_count=len(listing_skills_must),
                               listing_skills_good_count=len(listing_skills_good),
                               listing_skills_soft_count=len(listing_skills_soft),
                               matching_skills_len_total=intersection_list_total_len,
                               cv_skills_len=len(skills_cv_list),
                               listing_skills_len_total=listing_list_total_len,
                               score=score,
                               score_must=score_must,
                               score_good=score_good,
                               score_soft=score_soft,
                               excel_filename=workbook_filename,
                               experience_list=experience_list,
                               experience_list_len=len(experience_list),
                               experience_skills_list_total=experience_skills_list_total,
                               education=education,
                               final_score=final_score,
                               )

    elif request.method == 'GET':
        return "Do not try to fool me :)\nYou should upload CV firstly"


@app.route('/downloads/<filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = app.config['UPLOAD_FOLDER']
    file_handle = open(uploads + '/' + filename, 'r')

    @after_this_request
    def remove_file(response):
        try:
            os.remove(uploads + '/' + filename)
            file_handle.close()
        except Exception as error:
            app.logger.error("Error removing or closing downloaded file handle", error)
        return response

    return send_from_directory(directory=uploads, filename=filename)


if __name__ == '__main__':
    app.run()
