from flask import Flask, render_template, request, abort, send_file, url_for
from werkzeug.utils import secure_filename
import os
import config
import csv
from pyresparser import ResumeParser

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
        cv_data = ResumeParser(config.UPLOAD_FILES_DIR + config.CV_SUBFOLDER + '/' + cv_name).get_extracted_data()
        skills_cv = cv_data['skills']
        skills_cv = map(lambda x: x.lower(), skills_cv)
        skills_cv = list(skills_cv)

        listing_data = ResumeParser(
            config.UPLOAD_FILES_DIR + config.LISTING_SUBFOLDER + '/' + listing_name).get_extracted_data()
        skills_listing = listing_data['skills']
        skills_listing = map(lambda x: x.lower(), skills_listing)
        skills_listing = list(skills_listing)

        print("skills_listing:", skills_listing)
        print("skills_cv:", skills_cv)

        intersection_list = list(set(skills_cv) & set(skills_listing))
        print(intersection_list)

        matching_skills = ", ".join(str(x) for x in intersection_list)
        listing_skills_result = ", ".join(str(x) for x in list(skills_listing))
        cv_skills_result = ", ".join(str(x) for x in list(skills_cv))

        print(matching_skills)
        print(listing_skills_result)
        print(cv_skills_result)
        return render_template('test.html',
                               matching_skills=matching_skills,
                               cv_skills=cv_skills_result,
                               listing_skills=listing_skills_result,
                               matching_skills_len=len(intersection_list),
                               cv_skills_len=len(skills_cv),
                               listing_skills_len=len(skills_listing)
                               )

    elif request.method == 'GET':
        return "Do not try to fool me :)\nYou should upload CV firstly"


if __name__ == '__main__':
    app.run()

