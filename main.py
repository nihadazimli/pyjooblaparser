from flask import Flask, render_template, request, abort, send_file, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import config
import xlsxwriter
import csv
from pyjooblaparser import ResumeParser
from pyjooblaparser import ListingParser

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
        file = request.files['file']
        file_type = request.form['Upload']
        print(file_type)
        filename = secure_filename(file.filename)
        if file_type == 'Listing':
            file.save(os.path.join(app.config['UPLOAD_FOLDER'] + config.LISTING_SUBFOLDER, filename))
        elif file_type == 'CV':
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
        skills_cv_list = skills_cv.keys()

        listing_data = ListingParser(config.UPLOAD_FILES_DIR + config.LISTING_SUBFOLDER + '/' + listing_name)\
            .cluster_divider("./clusters/must_have.txt", "./clusters/good_to_have.txt", "./clusters/soft_skills.txt")
        print(listing_data)

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

        print("skills_cv:", skills_cv_list)

        intersection_list_total_len = 0
        try:
            intersection_list_must = list(set(skills_cv) & set(skills_listing_must.keys()))
            intersection_list_total_len += len(intersection_list_must)
            score_must = len(intersection_list_must)*config.WEIGHT_MUST
            score += score_must
        except:
            intersection_list_must = {}

        try:
            intersection_list_good = list(set(skills_cv) & set(skills_listing_good.keys()))
            intersection_list_total_len += len(intersection_list_good)
            score_good = len(intersection_list_good)*config.WEIGHT_GOOD
            score += score_good

        except:
            intersection_list_good = {}

        try:
            intersection_list_soft = list(set(skills_cv) & set(skills_listing_soft))
            intersection_list_total_len += len(intersection_list_soft)
            score_soft = len(intersection_list_soft)*config.WEIGHT_SOFT
            score += score_soft

        except:
            intersection_list_soft = []


        matching_skills_must = intersection_list_must
        matching_skills_good = intersection_list_good
        matching_skills_soft = intersection_list_soft

        listing_skills_must = ", ".join((k + ' : ' + str(v)) for k, v in skills_listing_must.items())
        listing_skills_must = listing_skills_must.split(',')
        listing_skills_good = ", ".join((k + ' : ' + str(v)) for k, v in skills_listing_good.items())
        listing_skills_good = listing_skills_good.split(',')
        listing_skills_soft = ",".join(str(x)[2:-2] for x in skills_listing_soft)
        listing_skills_soft = listing_skills_soft.split(',')
        print(listing_skills_soft)
        cv_skills_result = ", ".join((k + ' : ' + str(v)) for k, v in skills_cv.items())
        cv_skills_result = cv_skills_result.split(',')

        print(cv_skills_result)

        workbook = xlsxwriter.Workbook('./excel_files/' + cv_name + '.xlsx')
        worksheet = workbook.add_worksheet()

        # Widen the first column to make the text clearer.
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 10)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 10)

        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': True})

        # Write some simple text.
        worksheet.write('A1', 'CV ID', bold)
        worksheet.write('B1', 'JOB LISTING ID', bold)
        worksheet.write('C1', 'EXPECTED SCORE', bold)
        worksheet.write('D1', 'SCORE', bold)
        worksheet.write('E1', 'CV KEYWORDS', bold)
        worksheet.write('F1', 'CLUSTER MUST HAVE MATCH', bold)
        worksheet.write('G1', 'CLUSTER MUST HAVE SCORE', bold)
        worksheet.write('H1', 'CLUSTER GOOD TO HAVE MATCH', bold)
        worksheet.write('I1', 'CLUSTER GOOD TO HAVE SCORE', bold)
        worksheet.write('J1', 'CLUSTER SOFT MATCH', bold)
        worksheet.write('K1', 'CLUSTER SOFT SCORE', bold)

        # Text with formatting.
        worksheet.write('A2', cv_name)
        worksheet.write('B2', listing_name)
        worksheet.write('C2', '')
        worksheet.write('D2', score)

        count = 1
        for k, v in skills_cv.items():
            count += 1
            worksheet.write('E'+str(count), k + ' : ' + str(v))

        count = 1
        for k, v in skills_listing_must.items():
            count += 1
            worksheet.write('F' + str(count), k + ' : ' + str(v))
        worksheet.write('G2', score_must)

        count = 1
        for k, v in skills_listing_good.items():
            count += 1
            worksheet.write('H' + str(count), k + ' : ' + str(v))
        worksheet.write('I2', score_good)

        count = 1
        for k, v in skills_listing_good.items():
            count += 1
            worksheet.write('J' + str(count), k + ' : ' + str(v))
        worksheet.write('K2', score_good)

        workbook.close()

        return render_template('test.html',
                               matching_skills_must=matching_skills_must,
                               matching_skills_good=matching_skills_good,
                               matching_skills_soft=matching_skills_soft,
                               cv_skills=cv_skills_result,
                               listing_skills_must=listing_skills_must,
                               listing_skills_good=listing_skills_good,
                               listing_skills_soft=listing_skills_soft,
                               matching_skills_len_total=intersection_list_total_len,
                               cv_skills_len=len(skills_cv_list),
                               listing_skills_len_total=listing_list_total_len,
                               score=score
                               )

    elif request.method == 'GET':
        return "Do not try to fool me :)\nYou should upload CV firstly"


@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory("./excel_files",
                               filename, as_attachment=True)

if __name__ == '__main__':
    app.run()

