# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import datetime
from app import db
from flask_login import UserMixin


class CRUDMixin:
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Users(db.Model, UserMixin, CRUDMixin):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    division_id = db.Column(db.Integer, db.ForeignKey('Divisions.id'))
    #user = db.Column(db.String(64),  unique=True)
    email = db.Column(db.String(120), unique=True)
    #password = db.Column(db.String(500))

    def __init__(self, email):
        # self.user = user
        # self.password = password
        self.email = email

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.user)

    def save(self):
        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self



class Division(db.Model, CRUDMixin):
    __tablename__ = 'Divisions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(4), nullable=False)
    projects = db.relationship('Project', backref='Division')
    users = db.relationship('Users', backref='Division')

    def __repr__(self):
        return str(self.short_name)


collab_project = db.Table('collab_project', db.Column('project_id', db.Integer, db.ForeignKey('Projects.id')),\
                                            db.Column('division_id', db.Integer, db.ForeignKey('Divisions.id')),\
                                            db.Column('date_created', db.DateTime, default=datetime.datetime.now())
                                            )

class Project(db.Model, CRUDMixin):
    __tablename__ = 'Projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    division_id = db.Column(db.Integer, db.ForeignKey('Divisions.id'))
    status = db.Column(db.String(20), default="Not Started", nullable=False)

    date_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    date_modified = db.Column(db.DateTime, onupdate=datetime.datetime.now(), default=datetime.datetime.now())
    date_expected = db.Column(db.DateTime, nullable=False)

    action_items = db.relationship('ActionItem', backref='project')
    supporting_divisions = db.relationship('Division', secondary=collab_project, backref='projects_supporting')

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.title)




class ActionItem(db.Model, CRUDMixin):
    __tablename__ = "Action_items"
    id = db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    project_id = db.Column(db.Integer, db.ForeignKey('Projects.id'))
    status = db.Column(db.String(20), default="Not Started", nullable=False)

    date_created = db.Column(db.DateTime, default=datetime.datetime.now())
    date_modified = db.Column(db.DateTime, onupdate=datetime.datetime.now(), default=datetime.datetime.now())
    date_expected = db.Column(db.DateTime, nullable=False)

    deliverables = db.relationship('Deliverable', backref='action_item')

    dev_n_assigned_var = db.Column(db.Boolean, default=False)
    mgmt_approval = db.Column(db.Boolean, default=False)
    commissioner_approval = db.Column(db.Boolean, default=False)
    published_or_completed = db.Column(db.Boolean, default=False)

    reason_for_delay_div = db.Column(db.String)
    presented_at_comm_meeting = db.Column(db.Boolean, default=False)
    finalized_at_comm = db.Column(db.Boolean, default=False)
    reason_for_delay_comm = db.Column(db.String)

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.title)


class Deliverable(db.Model, CRUDMixin):
    __tablename__ = "Deliverables"
    id = db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    action_item_id = db.Column(db.Integer, db.ForeignKey('Action_items.id'))
    status = db.Column(db.String(20), default="Not Started", nullable=False)

    date_created = db.Column(db.DateTime, default=datetime.datetime.now())
    date_modified = db.Column(db.DateTime, onupdate=datetime.datetime.now(), default=datetime.datetime.now())
    date_expected = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.title)
