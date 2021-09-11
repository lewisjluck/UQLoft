#Standard libraries
import sqlite3
import urllib.request
from requests_html import HTMLSession

#Dynamic pathing
from os import path
ROOT = path.dirname(path.realpath(__file__))

#Open database
def open_db():
    db = sqlite3.connect(path.join(ROOT, "UQLoft.db"))
    db.commit()
    return db

#Close database
def close_db(db):
    if db is not None:
        db.close()

#Check if any papers have this course title
def is_valid_course(query_course_code):
    db = open_db()
    papers =  db.execute("SELECT * FROM papers WHERE course_code LIKE ?", ("%" + query_course_code.lower() + "%",)).fetchall()
    if papers:
        return True
    else:
        return False

#Get paper with this course title
def get_paper_data(query_course_code):
    db = open_db()
    papers =  db.execute("SELECT * FROM papers WHERE course_code LIKE ?", ("%" + query_course_code.lower() + "%",)).fetchall()
    paper_list = []
    for paper in papers:
        paper_list.append({"course": paper[1], "year": paper[2], "semester": paper[3]})
    return paper_list

def get_number_questions(course, year, semester):
    db = open_db()
    matches = []
    papers =  db.execute("SELECT * FROM papers WHERE course_code LIKE ?", ("%" + course.lower() + "%",)).fetchall()
    for paper in papers:
        if paper[1] == course and paper[2] == year and paper[3] == semester:
            return paper[4]

def get_ecp_details(course_code):
    url = "https://my.uq.edu.au/programs-courses/course.html?course_code=" + course_code.upper()
#     if course_code.lower() == "csse1001":
#         return (url, 'Introduction to Software Engineering (CSSE1001)', '''Introduction to Software Engineering through programming with particular focus
# on the fundamentals of computing & programming, using an exploratory problem-based approach. Building abstractions with procedures, data & objects; data modelling; desig
# ning, coding & debugging programs of increasing complexity''')
#     elif course_code.lower() == "csse2002":
#         return (url, "Programming in the Large (CSSE2002)", '''Working on large and complex software systems and ensuring those systems
# remain maintainable requires disciplined, individual practices. Software must be well-specified, well-impleme
# nted and well-tested. This course covers concepts and techniques in modern programming languages that help su
# pport good practice (such as OO concepts, genericity and exception handling) with specific application to fil
# e IO and GUIs in Java.''')
    session = HTMLSession()
    r = session.get(url)
    course_name = r.html.find('#course-title', first=True).text
    course_description = r.html.find('#course-summary', first=True).text
    return (url, course_name, course_description)

#id - paper_code - question_num - a,b,c,d,e_count

def update_questions(paper_code, data):
    db = open_db()
    for (i, answer) in enumerate(data):
        res = db.execute("SELECT * FROM questions WHERE paper_code=? AND question_num=?", (paper_code,i+1)).fetchone()
        if res:
            res = list(res)
            if answer:
                res[ord(answer) - 62] += 1
                db.execute("UPDATE questions SET a = ?, b = ?, c = ?, d = ?, e = ? WHERE paper_code = ? AND question_num = ?", (res[3], res[4], res[5], res[6], res[7], paper_code, i+1))
        else:
            update = [0, 0, 0, 0, 0]
            if answer:
                update[ord(answer) - 65] += 1
            db.execute("INSERT INTO questions (paper_code, question_num, a, b, c, d, e) VALUES (?, ?, ?, ?, ?, ?, ?)", (paper_code, i+1, *update))
    db.commit()
    close_db(db)

def get_data(code):
    db = open_db()
    res = db.execute("SELECT * FROM questions WHERE paper_code=?", (code,)).fetchall()
    close_db(db)
    return res

#update_questions("csse1001_2019_sem2", ['B', 'C', 'B', 'A', 'C', None, 'D', 'E', 'B', 'B', 'A', 'C', 'D', 'E', 'B', 'C', 'C', 'D', 'D', None, 'A', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None])
