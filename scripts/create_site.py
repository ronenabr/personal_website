# -*- coding: utf-8 -*-

from jinja2 import Environment, FileSystemLoader
import os
import markdown

import codecs


md = markdown.markdown

TEMPLATE_DIR = "../templates"
CONTENT_DIR = "../content"
PROJECT_SUBDIR = "Projects"
NOTES_SUBDIR = "Notes"

READ_LIMIT = 1000000

OUT_DIR = ".."



loader = FileSystemLoader(TEMPLATE_DIR)
env = Environment(loader=loader)


def build_project_page():
    global env

    #Process projects
    projects_info = []
    project_dir = os.path.join(CONTENT_DIR, PROJECT_SUBDIR)
    for project_cat in os.listdir(project_dir):
        project_cat = os.path.join(project_dir, project_cat)
        if os.path.isdir(project_cat):
            project_info = {}
            sub_projects = []
            for project in os.listdir(project_cat):
                project_file = os.path.join(project_cat, project)
                if project == "meta.txt":
                    f = codecs.open(project_file, "r", encoding="utf-8")
                    project_info["title"] = f.readline().strip()
                    project_info["description"] = md(f.read(READ_LIMIT))
                    f.close()
                elif project.endswith(".txt"):
                    f = codecs.open(project_file, "r", encoding="utf-8")
                    subproject_info = {}
                    subproject_info["title"] = f.readline().strip()
                    subproject_info["description"] = md(f.read(READ_LIMIT))
                    sub_projects.append(subproject_info)
                    f.close()
            if sub_projects:
                project_info["subprojects"] = sub_projects
            projects_info.append(project_info)

    intro_file = os.path.join(project_dir, "intro.txt")
    f = codecs.open(intro_file, "r", encoding="utf-8")
    intro = f.read(READ_LIMIT)
    intro = md(intro)
    f.close()


    proj_template = env.get_template('projects.html')
    out_file = os.path.join(OUT_DIR, "projects.html")
    project_page = proj_template.render(projects_info=projects_info,
                                        projects_active="active",
                                        intro=md(intro),
                                        title="Projects")
    f = codecs.open(out_file, "w", encoding="utf-8")
    f.write(project_page)
    f.close()


def get_val(line):
    return line.split(":",1)[1].strip()


#Notes
def create_note_page(input_filename, output_filename):
    global env

    notes_dir = os.path.join(CONTENT_DIR, NOTES_SUBDIR)
    lecture_filename = os.path.join(notes_dir, input_filename)
    lecture_file = codecs.open(lecture_filename, "r", encoding='utf-8')
    semester = None
    title = None
    current = {}
    semesters = []
    current_semester = []
    get_intro_flag = False
    intro = ""
    pdf_dir = None
    lyx_dir = None
    for l in lecture_file:
        if l.startswith("End intro:"):
            get_intro_flag = False
        elif get_intro_flag:
            intro += l
        elif l.startswith("title"):
            title = get_val(l)
        elif l.startswith("Intro:"):
            get_intro_flag = True
        elif l.startswith("PDF source"):
            pdf_dir = get_val(l)
        elif l.startswith("LyX source"):
            lyx_dir = get_val(l)
        elif l.startswith("Semester:"):
            if current:
                current_semester.append(current)
                current = {}
            if current_semester and semester:
                semesters.append({"name": semester, "topics": current_semester})
                current_semester = []
            semester = get_val(l)
        elif l.startswith("Name:"):
            if current:
                current_semester.append(current)
                current = {}
            current["name"] = get_val(l)
            print current["name"]
        elif l.startswith("HName:"):
            current["hname"] = get_val(l)
        elif l.startswith("Description:"):
            current["description"] = get_val(l)
        elif l.startswith("Proffesor:"):
            current["prof"] = get_val(l)
        elif l.startswith("PDF:"):
            filename = get_val(l)
            if filename:
                current["pdf"] = os.path.join(pdf_dir,filename)
        elif l.startswith("LyX:"):
            filename = get_val(l)
            if filename:
                current["lyx"] = os.path.join(lyx_dir, filename)
        elif l.startswith("Lang:"):
            current["lang"] = get_val(l)
    if current:
        current_semester.append(current)
        current = {}
    if current_semester and semester:
        semesters.append({"name": semester, "topics": current_semester})
        current_semester = []
    intro = md(intro)

    proj_template = env.get_template('notes.html')
    out_file = os.path.join(OUT_DIR, output_filename)
    project_page = proj_template.render(semesters=semesters,
                                        title=title,
                                        intro=intro,
                                        notes_active="active")
    f = codecs.open(out_file, "w", encoding="utf-8")
    f.write(project_page)
    f.close()


def create_default_page(input_filename, output_filename, more_data):
    input_file = codecs.open(input_filename, "r", encoding='utf-8')
    title = input_file.readline().strip()
    intro = input_file.read(READ_LIMIT)
    intro = md(intro)
    input_file.close()

    template = env.get_template('base.html')
    out_file = os.path.join(OUT_DIR, output_filename)
    page = template.render(title=title,
                           intro=intro,
                           **more_data)
    f = codecs.open(out_file, "w", encoding="utf-8")
    f.write(page)
    f.close()



create_note_page("lectures.txt", "lecture_notes.html")
create_note_page("recitations.txt", "recitation_notes.html")
build_project_page()
create_default_page(os.path.join(CONTENT_DIR, "home.txt"), "index.html", {"home_active" : "active"})
create_default_page(os.path.join(CONTENT_DIR, "publications.txt"), "publications.html", {"publications_active" : "active"})

