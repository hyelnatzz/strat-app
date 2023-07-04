# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Python modules
import os
from datetime import datetime

# Flask modules
from flask import render_template, request, url_for, redirect, send_from_directory, flash, send_file
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort
from jinja2 import TemplateNotFound

# App modules
from app import app, lm, db, bc
from app.models import Project, ActionItem, Deliverable, Users, Division
from app.forms import LoginForm, RegisterForm
from app.constants import DATE_FORMAT, create_event_status_css

# provide login manager with load_user callback

#logging.basicConfig(level=logging.DEBUG)

@lm.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Logout user
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# # Register a new user
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     # declare the Registration Form
#     form = RegisterForm(request.form)
#     msg = None
#     success = False

#     if request.method == 'GET':
#         return render_template('register.html', form=form, msg=msg)

#     # check if both http method is POST and form is valid on submit
#     if form.validate_on_submit():

#         # assign form data to variables
#         username = request.form.get('username', '', type=str)
#         password = request.form.get('password', '', type=str)
#         email = request.form.get('email', '', type=str)

#         # filter User out of database through username
#         user_by_email = Users.query.filter_by(email=email).first()

#         if user_by_email:
#             msg = 'Error: User exists!'

#         else:

#             pw_hash = bc.generate_password_hash(password)

#             user = Users(username, email, pw_hash)

#             user.save()

#             msg = 'User created, please <a href="' + \
#                 url_for('login') + '">login</a>'
#             success = True

#     else:
#         msg = 'Input error'

#     return render_template('register.html', form=form, msg=msg, success=success)

# Authenticate user
@app.route('/login', methods=['GET', 'POST'])
def login():

    # Declare the login form
    form = LoginForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str)

        # filter User out of database through username
        user = Users.query.filter_by(user=username).first()

        if user:
            if bc.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unknown user"

    return render_template('login.html', form=form, msg=msg)

# App main route + generic routing
#@app.route('/', defaults={'path': 'index'})
@app.route('/', methods=["GET","POST"])
def index():
    # if not current_user.is_authenticated:
    #    return redirect(url_for('login'))
    if current_user.is_authenticated:
        return redirect(url_for('projects', division_id=current_user.Division.id))


    if request.method == "POST":
        # assign form data to variables
        email = request.form.get('email', '', type=str).strip()
        division_short_name = request.form.get('division', '', type=str)
        try:
                # filter User out of database through username
            user = Users.query.filter_by(email=email).first()
            division = Division.query.filter_by(short_name=division_short_name).first()

            if user is None:
                new_user = Users(email)
                new_user.Division = division
                new_user.save()
                return redirect(url_for('projects', division_id = division.id))

            if user:
                login_user(user)
                return redirect(url_for('projects', division_id = user.Division.id))
            else:
                flash("Something went wront. Please try again.")
        except:
            return "something went wrong"

    return render_template('index.html')


# Return projects page
@app.route('/divisions/<int:division_id>', methods=["GET", "POST"])
def projects(division_id):
    if division_id == 0:
        projects = Project.query.all()
        division = {'name':"All Commission's", 'id': 0}
    else:
        div =  Division.query.get(division_id)
        division = {'name': div.name, 'id': div.id}
        projects = div.projects

    data = []
    if len(projects) > 0:
        for project in projects:
            project_data = {}
            project_data['id'] = project.id
            project_data['title'] = project.title
            action_items = project.action_items
            project_data['action_items'] = len(action_items)
            count_of_deliverables = 0

            for item in action_items:
                count_of_deliverables += len(item.deliverables)
            project_data['deliverable_count'] = count_of_deliverables
            data.append(project_data)

    def add_support(div_short_name):
        division = Division.query.filter_by(short_name = div_short_name).first()
        new_project.supporting_divisions.append(division)

    if request.method == "POST":
        form_data = dict(request.form)
        new_project = Project()
        new_project.title = form_data.get('title')
        new_project.description = form_data.get('description')
        new_project.date_expected = datetime.strptime(form_data.get('date_expected'), DATE_FORMAT)

        division = Division.query.filter_by(short_name="PRS").first()
        new_project.division = division
        new_project.save()

        # Add supporting divisions
        if form_data.get('CO') == "on":
            add_support('CO')

        if form_data.get('PRS') == "on":
            add_support('PRS')

        if form_data.get('MCR') == "on":
            add_support('MCR')

        if form_data.get('LLC') == "on":
            add_support('LLC')

        if form_data.get('EPM') == "on":
            add_support('EPM')

        if form_data.get('CA') == "on":
            add_support('CA')

        if form_data.get('FMS') == "on":
            add_support('FMS')

        new_project.update()


        flash("Project Added Success fully")
    return render_template('projects.html', division=division, data=data)


# Return action items page
@app.route('/projects/<int:project_id>', methods=["GET", "POST", "PATCH"])
def action_items(project_id):
    if project_id == 0:
        #project = Project.query.get(project_id)
        action_items = ActionItem.query.all()
        #division =  project.Division

        data = {}
        data['division'] = "All Divisions"
        data['division_id'] = 0
        data['project'] = "All Projects"

    else:
        project = Project.query.get(project_id)
        action_items = project.action_items
        division =  project.Division

        data = {}
        data['division'] = division.name
        data['division_id'] = division.id
        data['project'] = project.title
        data['date_now'] = datetime.now()

    data['action_items'] = [{'id':item.id,
                             'title':item.title,
                             'status':item.status,
                             'date_expected':item.date_expected,
                              'status_class':create_event_status_css(item.status)} for item in action_items]

    if request.method == "POST":
        form_data = dict(request.form)
        project_id = project.id
        new_item= ActionItem(**form_data)
        new_item.date_expected = datetime.strptime(form_data.get('date_expected'), DATE_FORMAT)
        new_item.project_id = project_id
        new_item.save()
        return redirect(url_for('action_items', project_id=project_id))

    return render_template('action-items.html', data=data)


# Return action items page
@app.route('/action-items/<int:action_item_id>', methods=["GET", "POST"])
def deliverables(action_item_id):
    action_item = ActionItem.query.get(action_item_id)
    project = action_item.project
    division = action_item.project.Division
    deliverables = action_item.deliverables

    data = {}
    data['action_item'] = action_item.title
    data['project_title'] = project.title
    data['project_id'] = project.id
    data['division'] = division.name
    data['division_id'] = division.id
    data['description'] = action_item.description
    data['date_now'] = datetime.now()
    data['deliverables'] = [{'id':deliverable.id, \
                            'title':deliverable.title, \
                            'status': deliverable.status,
                            'date_expected': deliverable.date_expected,
                            'status_class': create_event_status_css(deliverable.status)} for deliverable in deliverables]
    data['action_item_stage'] = [{'text':"Yes" if action_item.dev_n_assigned_var else "No", 'passed':create_event_status_css(action_item.dev_n_assigned_var)},\
                                {'text':"Yes" if action_item.mgmt_approval else "No", 'passed':create_event_status_css(action_item.mgmt_approval)}, \
                                {'text':"Yes" if  action_item.commissioner_approval else "No", 'passed':create_event_status_css(action_item.commissioner_approval)}, \
                                {'text':"Yes" if action_item.published_or_completed else "No", 'passed':create_event_status_css(action_item.published_or_completed)}, \
                                {'text':action_item.reason_for_delay_div}, \
                                {'text':"Yes" if action_item.presented_at_comm_meeting else "No", 'passed':create_event_status_css(action_item.presented_at_comm_meeting)}, \
                                {'text':"Yes" if action_item.finalized_at_comm else "No", 'passed':create_event_status_css(action_item.finalized_at_comm)}, \
                                {'text': action_item.reason_for_delay_comm}
                                ]

    if request.method == "POST":
        form_data = dict(request.form)
        new_deliverable = Deliverable(**form_data)
        new_deliverable.date_expected = datetime.strptime(form_data.get('date_expected'), DATE_FORMAT)
        new_deliverable.action_item_id = action_item_id
        new_deliverable.save()
        return redirect(url_for('deliverables', action_item_id=action_item_id))
    return render_template('deliverables.html', action_item_id=action_item_id, data=data)

# Return action items page
@app.route('/edit-action/<int:action_item_id>', methods=["GET", "POST"])
def edit_action(action_item_id):
    action_item = ActionItem.query.get(action_item_id)

    data = {}
    data['title'] = action_item.title
    data['description'] = action_item.description
    data['date_expected'] = datetime.strftime(action_item.date_expected, '%Y-%m-%d')
    data['dev_n_assigned_var'] = action_item.dev_n_assigned_var
    data['mgmt_approval'] = action_item.mgmt_approval
    data['commissioner_approval'] = action_item.commissioner_approval
    data['published_or_completed'] = action_item.published_or_completed
    data['reason_for_delay_div'] = action_item.reason_for_delay_div
    data['presented_at_comm_meeting'] = action_item.presented_at_comm_meeting
    data['finalized_at_comm'] = action_item.finalized_at_comm
    data['reason_for_delay_comm'] =  action_item.reason_for_delay_comm


    if request.method == "POST":
        form_data = request.form
        action_item.title = form_data['title']
        action_item.description = form_data['description']
        action_item.date_expected = datetime.strptime(form_data['date_expected'], DATE_FORMAT)
        action_item.dev_n_assigned_var = True if form_data['dev_n_assigned_var']  == 'Yes' else False
        action_item.mgmt_approval = True if  form_data['mgmt_approval']  == 'Yes' else False
        action_item.commissioner_approval = True if  form_data['commissioner_approval']  == 'Yes' else False
        action_item.published_or_completed = True if  form_data['published_or_completed']  == 'Yes' else False
        action_item.reason_for_delay_div = form_data['reason_for_delay_div']
        action_item.presented_at_comm_meeting = True if  form_data['presented_at_comm_meeting']  == 'Yes' else False
        action_item.finalized_at_comm = True if  form_data['finalized_at_comm']  == 'Yes' else False
        action_item.reason_for_delay_comm = form_data['reason_for_delay_comm']

        action_item.update()

        return redirect(url_for('deliverables', action_item_id=action_item.id))
    return render_template('item-status.html', action_item_id=action_item_id, data=data)

# Return action items page
@app.route('/deliverable/<int:deliverable_id>', methods=["GET", "POST"])
def deliverable(deliverable_id):
    deliverable = Deliverable.query.get(deliverable_id)
    action_item = deliverable.action_item
    project = action_item.project
    division = project.Division

    data = {}
    data['division'] = division.name
    data['division_id'] = division.id
    data['action_item'] = action_item.title
    data['action_item_id'] = action_item.id
    data['project'] = project.title
    data['project_id'] = project.id
    data['title'] = deliverable.title
    data['description'] = deliverable.description
    data['status'] = deliverable.status
    data['status_class'] = create_event_status_css(deliverable.status)
    data['date_expected'] = datetime.strftime(deliverable.date_expected, '%Y-%m-%d')
    data['date_expected_display'] = deliverable.date_expected
    data['date_now'] = datetime.now()
    data['date_created'] = datetime.strftime(deliverable.date_created, '%Y-%m-%d')

    if request.method == "POST":
        deliverable.title = request.form.get('title')
        deliverable.description = request.form.get('description')
        deliverable.date_expected = datetime.strptime(request.form.get('date_expected'), '%Y-%m-%d')
        deliverable.status = request.form.get('status')
        deliverable.update()
        return redirect(url_for('deliverable', deliverable_id=deliverable_id))
    return render_template('deliverable.html', deliverable_id=deliverable_id, data=data)

@app.route('/deliverable/delete/<int:deliverable_id>', methods=["GET", "POST"])
def delete_deliverable(deliverable_id):
    deliverable = Deliverable.query.get(deliverable_id)
    action_item_id = deliverable.action_item.id
    deliverable.delete()
    return redirect(url_for('deliverables', action_item_id = action_item_id))


@app.route('/download-all/')
def download_all():
    deliverables = Deliverable.query.all()
    if len(deliverables) > 0:
        create_xlsx(deliverables)
        return send_file('NERC_projects.xlsx', as_attachment=True)
    else:
        return "No record yet."

# Export file creator
def create_xlsx(deliverables):
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active

    sheet["A1"] = "Division"
    sheet["B1"] = "Action Items"
    sheet["C1"] = "Deliverables"
    sheet["D1"] = "Development & Assignment of Deliverables"
    sheet["E1"] = "Management Approval"
    sheet["F1"] = "Commissioner's Approval"
    sheet["G1"] = "Published or Completed"
    sheet["H1"] = "Reason for Delay (Divisional)"
    sheet["I1"] = "Presented & Approved at the Commission's Meeting"
    sheet["J1"] = "Finalized at Commission Level"
    sheet["K1"] = "Reason for Delay (Commision)"

    row_count = 2

    for deliverable in deliverables:
        action_item = deliverable.action_item
        division = action_item.project.Division
        supporting_divisions = action_item.project.supporting_divisions

        div_output = division.short_name

        if len(supporting_divisions) > 0:
            div_output += ' SUPPORTED BY '
            for division in supporting_divisions:
                div_output += division.short_name + ','

        sheet['A' + str(row_count)] = div_output
        sheet['B' + str(row_count)] = action_item.title
        sheet['C' + str(row_count)] = deliverable.title
        sheet['D' + str(row_count)] = action_item.dev_n_assigned_var
        sheet['E' + str(row_count)] = action_item.mgmt_approval
        sheet['F' + str(row_count)] = action_item.commissioner_approval
        sheet['G' + str(row_count)] = action_item.published_or_completed
        sheet['H' + str(row_count)] = action_item.reason_for_delay_div
        sheet['I' + str(row_count)] = action_item.presented_at_comm_meeting
        sheet['J' + str(row_count)] = action_item.finalized_at_comm
        sheet['K' + str(row_count)] = action_item.reason_for_delay_comm

        row_count += 1
    workbook.save(filename="./app/NERC_projects.xlsx")


# @app.route('/download/', methods=['GET'])
# def download():
#     return send_file('file.txt', as_attachment=True)


@app.route('/populate-db/')
def populate_db():

    divisions = [{'name':"Chairman's Office", 'short_name':'CO'},
                 {'name':"Consumer Affairs", 'short_name':'CA'},
                 {'name':"Finance and Management Services",'short_name':'FMS'},
                 {'name':'Engineering Performance and Monitoring', 'short_name':'EPM'},
                 {'name':'Legal, Licensing and Compliance', 'short_name':'LLC'},
                 {'name':'Market Competition and Rate', 'short_name':'MCR'},
                 {'name':'Planning, Research and Strategy', 'short_name':'PRS'}]

    for division in divisions:
        new_division = Division()
        new_division.name = division['name']
        new_division.short_name = division['short_name']
        new_division.save()

    import csv

    with open('current_projects.csv', mode='r') as file:
        csv_file = csv.reader(file)
        date_now = datetime.now()
        is_header = True

        for line in csv_file:
            if is_header:
                is_header = False
                continue
            division = line[0]
            if " SUPPORTED BY " in division:
                division, support_division = division.split("SUPPORTED BY")

            division = Division.query.filter_by(short_name = division).first()
            support_division = Division.query.filter_by(short_name = support_division).first()

            project = Project.query.filter_by(title=line[1]).first()
            if project is None:
                project = Project()
                project.title = line[1]
                project.description = "No description"
                project.date_expected = date_now
                project.Division = division
                if support_division is not None:
                    project.supporting_divisions.append(support_division)
                project.save()

            action_item = ActionItem.query.filter_by(title=line[1]).first()
            if action_item is None:
                action_item = ActionItem()
                action_item.title = line[1]
                action_item.description = "No description"
                action_item.date_expected = date_now
                action_item.project = project
                action_item.save()

            deliverable = Deliverable.query.filter_by(title=line[1]).first()
            if deliverable is None:
                deliverable = Deliverable()
                deliverable.title = line[2]
                deliverable.description = "No description"
                deliverable.date_expected = date_now
                deliverable.action_item = action_item
                deliverable.save()
    return "Done Populating"



# Return sitemap
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')
