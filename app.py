from flask import Flask, render_template, jsonify, request, redirect
import requests
from flask_cors import CORS
from helpers import is_valid_course, get_ecp_details, get_paper_data, get_number_questions, update_questions, get_data, add_new_paper
import os

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#Default error response
def error(message="Something went wrong! Let's try that again."):
    return render_template("error.html", message=message)

@app.route("/", methods = ["GET", "POST"])
def homepage():
    if request.method == "GET":
        return render_template("homepage.html")
    else:
        course_code = request.form["course_code"].lower()
        print(course_code)
        print(is_valid_course(course_code))
        if is_valid_course(course_code):
            return redirect("/loft?course=" + course_code)
        else:
            return error("Hmmm, looks like we don't have that course yet!")

@app.route("/add_paper", methods=["GET", "POST"])
def add_paper():
    if request.method == "GET":
        return render_template("add_paper.html")
    else:
        code = request.form.get("course_code").lower()
        year = request.form.get("year")
        semester = request.form.get("semester")
        number = request.form.get("number")
        uploaded_file = request.files['paper']
        if uploaded_file.filename != '':
            uploaded_file.save(f"./static/papers/{code.lower()}_{year}_sem{semester}.pdf")
        add_new_paper(code, year, semester, number)
        return render_template("success.html")

@app.route("/loft", methods = ["GET", "POST"])
def loft():
    if request.method == "GET":
        code = request.args.get("course")
        url, course_name, course_description = get_ecp_details(code)
        print(course_name, course_description)
        papers = get_paper_data(code)
        message_papers = [(f"/paper?det={code}_{paper['year']}_sem{paper['semester']}" ,f"{paper['year']} Semester {paper['semester']}") for paper in papers]
        print(message_papers)
        return render_template("loft.html", url=url, course_code=code, course_name=course_name, course_description=course_description, papers=message_papers)

@app.route("/paper", methods = ["GET", "POST"])
def papers():
    code = request.args.get("det")
    file = f"../static/papers/{code}.pdf"
    course, year, sem = code.split('_')
    paper_description = f"{course.upper()} - {year}, Semester {sem[-1]}"
    question_num = get_number_questions(course.lower(), int(year), int(sem[-1]))
    if request.method == "GET":
        return render_template("papers.html", code=code, file=file, description=paper_description, num=question_num)
    else:
        new_question_data = []
        for i in range(question_num):
            new_question_data.append(request.form.get(str(i+1)))
        print(new_question_data)
        update_questions(code, new_question_data)
        return redirect("/solutions?paper=" + code)

@app.route("/solutions", methods = ["GET", "POST"])
def solutions():
    code = request.args.get("paper")
    course, year, sem = code.split('_')
    paper_description = f"{course.upper()} - {year}, Semester {sem[-1]}"
    data = get_data(code)
    return render_template("solutions.html", code=code, description=paper_description, data=data)

@app.route("/courses", methods = ["GET", "POST"])
def courses():
    return render_template("courses.html")

@app.route("/about", methods = ["GET", "POST"])
def about():
    return render_template("about.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

@app.route("/is_course_valid", methods = ["GET", "POST"])
def is_course_valid():
    code = request.json["courseCode"]
    return jsonify(is_valid_course(code))


@app.route("/get_course_info", methods = ["GET", "POST"])
def get_papers():
    code = request.json["courseCode"]
    url, course_name, course_description = get_ecp_details(code)
    papers = get_paper_data(code)
    data = {
        "ecp_link" : url,
        "course_name": course_name,
        "course_description": course_description,
        "papers": papers
    }
    return jsonify(data)

@app.route("/serve_paper", methods = ["GET", "POST"])
def serve_paper():
    file = "/papers/" + request.args.get("file")
    print(os.path.join(THIS_FOLDER, file))
    return send_file(THIS_FOLDER + file, mimetype="application/pdf", cache_timeout=0)

if __name__ == '__main__':
    os.environ['FLASK_ENV'] = 'development'
    app.run(debug=True)
