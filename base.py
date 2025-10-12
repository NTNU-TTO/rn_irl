# -*- coding: utf-8 -*-
"""
Copyright (c) Lodve Berre and NTNU Technology Transfer AS 2024.

This file is part of Really Nice IRL.

Really Nice IRL is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
 any later version.

Really Nice IRL is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with Really Nice IRL. If not, see:
<https://www.gnu.org/licenses/agpl-3.0.html>.
"""

from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import create_engine, desc, func, Column, Integer, Text
from sqlalchemy import update, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, mapped_column
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm import relationship

import bcrypt
import pandas as pd
import streamlit as st

import utils

Base = declarative_base()

rights_map = {"Read Only": 0,
              "Read/Write": 1,
              "Read/Write/Create": 2,
              "Administrator": 9}


class SerializerMixin:
    """
    This class is used to make other classes iterable and enable easy
    conversion from database queries to Pandas Dataframes via dictionaries.
    """

    def __init__(self, data):

        for field in self.__table__.columns:

            if getattr(field, 'name'):
                setattr(self, field.name, data[field.name])

    def as_dict(self):
        return {column.name: getattr(self, column.name)
                for column in self.__table__.columns}

    def to_dict(self):
        return {column.name: getattr(self, column.name)
                for column in self.__table__.columns}


class IRL(Base, SerializerMixin):
    """
    Wrapper class around IRL texts and values in the database.
    """

    __tablename__ = 'IRL'

    Level = Column(Integer, primary_key=True)
    IRLType = Column(Text(3))
    Description = Column(Text)
    Aspects = Column(Text)
    StartupValue = Column(Integer)
    LicenseValue = Column(Integer)


class IRLAssessment(Base, SerializerMixin):
    """
    Wrapper class around the IRL Data table in the database.
    Contains all the historical assessment values for all projects.
    """

    __tablename__ = 'IRL Data'

    id = Column(Integer, primary_key=True)
    project_no = Column(Integer)
    project_name = Column(Text)
    project_leader_id = mapped_column(ForeignKey('Users.user_id'))
    project_description = Column(Text)
    assessment_date = Column(Text(10))
    project_notes = Column(Text)
    crl = Column(Integer)
    trl = Column(Integer)
    brl = Column(Integer)
    iprl = Column(Integer)
    tmrl = Column(Integer)
    frl = Column(Integer)
    crl_notes = Column(Text)
    trl_notes = Column(Text)
    brl_notes = Column(Text)
    iprl_notes = Column(Text)
    tmrl_notes = Column(Text)
    frl_notes = Column(Text)
    crl_target = Column(Integer)
    trl_target = Column(Integer)
    brl_target = Column(Integer)
    iprl_target = Column(Integer)
    tmrl_target = Column(Integer)
    frl_target = Column(Integer)
    crl_target_lead = Column(Text(64))
    trl_target_lead = Column(Text(64))
    brl_target_lead = Column(Text(64))
    iprl_target_lead = Column(Text(64))
    tmrl_target_lead = Column(Text(64))
    frl_target_lead = Column(Text(64))
    crl_target_duedate = Column(Text(10))
    trl_target_duedate = Column(Text(10))
    brl_target_duedate = Column(Text(10))
    iprl_target_duedate = Column(Text(10))
    tmrl_target_duedate = Column(Text(10))
    frl_target_duedate = Column(Text(10))
    plot_targets = Column(Integer)
    active = Column(Integer)

    def __str__(self):
        return str(self.project_no) + " " + str(self.project_name)

    def __repr__(self):
        return str(self.project_no) + " " + str(self.project_name)

    def _getDate(self):
        """
        Convenience method to convert from datetime.date to ISO standard
        date string which we store in the database.

        Returns
        -------
        date : str
            ISO standard date (YYYY-MM-DD).
        """

        date = datetime.now()
        date = '%d-%02d-%02d' % (date.year, date.month, date.day)

        return date

    def calc_license_value(self):
        """
        Method to calculate ballpark license value based on IRL levels and
        the corresponding values in the database.
        WARNING: NOT CALIBRATED OUT OF THE BOX!
        VALUES MUST BE SET ACCORDING TO LOCAL CURRENCY AND EXPERIENCE!

        Returns
        -------
        value : int
             Sum of license values set in database for the IRL.
        """

        engine = create_engine(st.secrets.db_details.db_path)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        value = session.query(func.sum(IRL.LicenseValue)).filter(
                ((IRL.IRLType == 'CRL') & (IRL.Level == self.crl)) |
                ((IRL.IRLType == 'TRL') & (IRL.Level == self.trl)) |
                ((IRL.IRLType == 'BRL') & (IRL.Level == self.brl)) |
                ((IRL.IRLType == 'IPRL') & (IRL.Level == self.iprl)) |
                ((IRL.IRLType == 'TMRL') & (IRL.Level == self.tmrl)) |
                ((IRL.IRLType == 'FRL') & (IRL.Level == self.frl)))\
            .scalar()
        session.close()
        engine.dispose()

        return value

    def calc_license_target_value(self):
        """
        Method to calculate ballpark license value based on IRL levels and
        the corresponding target values in the database.
        WARNING: NOT CALIBRATED OUT OF THE BOX!
        VALUES MUST BE SET ACCORDING TO LOCAL CURRENCY AND EXPERIENCE!

        Returns
        -------
        value : int
             Sum of license values set in database for the target IRL.
        """

        engine = create_engine(st.secrets.db_details.db_path)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        value = session.query(func.sum(IRL.LicenseValue)).filter(
                ((IRL.IRLType == 'CRL') & (IRL.Level == self.crl_target)) |
                ((IRL.IRLType == 'TRL') & (IRL.Level == self.trl_target)) |
                ((IRL.IRLType == 'BRL') & (IRL.Level == self.brl_target)) |
                ((IRL.IRLType == 'IPRL') & (IRL.Level == self.iprl_target)) |
                ((IRL.IRLType == 'TMRL') & (IRL.Level == self.tmrl_target)) |
                ((IRL.IRLType == 'FRL') & (IRL.Level == self.frl_target)))\
            .scalar()
        session.close()
        engine.dispose()

        return value

    def calc_startup_value(self):

        engine = create_engine(st.secrets.db_details.db_path)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        value = session.query(func.sum(IRL.StartupValue)).filter(
                ((IRL.IRLType == 'CRL') & (IRL.Level == self.crl)) |
                ((IRL.IRLType == 'TRL') & (IRL.Level == self.trl)) |
                ((IRL.IRLType == 'BRL') & (IRL.Level == self.brl)) |
                ((IRL.IRLType == 'IPRL') & (IRL.Level == self.iprl)) |
                ((IRL.IRLType == 'TMRL') & (IRL.Level == self.tmrl)) |
                ((IRL.IRLType == 'FRL') & (IRL.Level == self.frl)))\
            .scalar()
        session.close()
        engine.dispose()

        return value

    def calc_startup_target_value(self):

        engine = create_engine(st.secrets.db_details.db_path)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        value = session.query(func.sum(IRL.StartupValue)).filter(
                ((IRL.IRLType == 'CRL') & (IRL.Level == self.crl_target)) |
                ((IRL.IRLType == 'TRL') & (IRL.Level == self.trl_target)) |
                ((IRL.IRLType == 'BRL') & (IRL.Level == self.brl_target)) |
                ((IRL.IRLType == 'IPRL') & (IRL.Level == self.iprl_target)) |
                ((IRL.IRLType == 'TMRL') & (IRL.Level == self.tmrl_target)) |
                ((IRL.IRLType == 'FRL') & (IRL.Level == self.frl_target)))\
            .scalar()
        session.close()
        engine.dispose()

        return value

    def insert(self):

        self.assessment_date = self._getDate()
        engine = create_engine(st.secrets.db_details.db_path)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()

        exists = (session.query(IRLAssessment).filter(
            IRLAssessment.project_no == self.project_no).first() is not None)
        error = None

        if exists:

            error = "Project already exists in the database!"

        else:

            session.add(self)
            session.commit()

        session.close()
        engine.dispose()

        return error

    def update(self, overwrite=False):

        error = None
        engine = create_engine(st.secrets.db_details.db_path)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        mapped_values = {}
        date = self._getDate()

        # If the date on record is today, we overwrite.
        if overwrite or date == self.assessment_date:

            for item in IRLAssessment.__dict__.items():

                field_name = item[0]
                field_type = item[1]
                is_column = isinstance(field_type, InstrumentedAttribute)

                if is_column:

                    mapped_values[field_name] = getattr(self, field_name)

            session.query(IRLAssessment).filter(
                IRLAssessment.id == self.id).update(mapped_values)

        # If not, we insert a new assessment and keep the historical one.
        else:

            # This is probably not the best way to do this. But hey, it works.
            new_irl = IRLAssessment()
            new_irl.project_no = self.project_no
            new_irl.project_name = self.project_name
            new_irl.project_leader_id = self.project_leader_id
            new_irl.project_description = self.project_description
            new_irl.assessment_date = date
            new_irl.project_notes = self.project_notes
            new_irl.crl = self.crl
            new_irl.trl = self.trl
            new_irl.brl = self.brl
            new_irl.iprl = self.iprl
            new_irl.tmrl = self.tmrl
            new_irl.frl = self.frl
            new_irl.crl_notes = self.crl_notes
            new_irl.trl_notes = self.trl_notes
            new_irl.brl_notes = self.brl_notes
            new_irl.iprl_notes = self.iprl_notes
            new_irl.tmrl_notes = self.tmrl_notes
            new_irl.frl_notes = self.frl_notes
            new_irl.crl_target = self.crl_target
            new_irl.trl_target = self.trl_target
            new_irl.brl_target = self.brl_target
            new_irl.iprl_target = self.iprl_target
            new_irl.tmrl_target = self.tmrl_target
            new_irl.frl_target = self.frl_target
            new_irl.crl_target_lead = self.crl_target_lead
            new_irl.trl_target_lead = self.trl_target_lead
            new_irl.brl_target_lead = self.brl_target_lead
            new_irl.iprl_target_lead = self.iprl_target_lead
            new_irl.tmrl_target_lead = self.tmrl_target_lead
            new_irl.frl_target_lead = self.frl_target_lead
            new_irl.crl_target_duedate = self.crl_target_duedate
            new_irl.trl_target_duedate = self.trl_target_duedate
            new_irl.brl_target_duedate = self.brl_target_duedate
            new_irl.iprl_target_duedate = self.iprl_target_duedate
            new_irl.tmrl_target_duedate = self.tmrl_target_duedate
            new_irl.frl_target_duedate = self.frl_target_duedate
            new_irl.plot_targets = self.plot_targets
            new_irl.active = self.active

            session.add(new_irl)

        try:

            session.commit()

        except BaseException:

            # tb = sys.exception().__traceback__
            error = "Could not save assessment to the database."

        session.close()
        engine.dispose()

        return error

    def __eq__(self, other):

        if isinstance(other, IRLAssessment):

            if other.id == self.id:

                return True

        return False


class User(Base, SerializerMixin):
    """
    Rights: 0: read-only, #1: read/write, #2, read/write/create, #9: admin
    Active: # 0: inactive, #1: active
    """
    __tablename__ = 'Users'

    user_id = Column(Integer, primary_key=True)
    actual_name = Column(Text)
    username = Column(Text(100), unique=True)
    password = Column(Text(100))
    rights = Column(Integer)
    active = Column(Integer)
    org_id = Column(Integer)
    fac_id = Column(Integer)
    dep_id = Column(Integer)

    def __hash__(self):
        return int(self.user_id)

    def __str__(self):
        return str(self.actual_name) + " (" + self.username + ")"

    def __repr__(self):
        return str(self.actual_name) + " (" + self.username + ")"


class UserSettings(Base):

    __tablename__ = 'User Settings'

    id = Column(Integer, primary_key=True)
    user_id = mapped_column(ForeignKey('Users.user_id'))
    smooth_irl = Column(Integer)
    filter_on_user = Column(Integer)
    remember_project = Column(Integer)
    last_project_no = Column(Integer)
    ascending_irl = Column(Integer)
    ap_table_view = Column(Integer)
    dark_mode = Column(Integer)

    def update(self):

        engine = create_engine(st.secrets.db_details.db_path)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        mapped_values = {}

        for item in UserSettings.__dict__.items():

            field_name = item[0]
            field_type = item[1]
            is_column = isinstance(field_type, InstrumentedAttribute)

            if is_column:

                mapped_values[field_name] = getattr(self, field_name)

        success = True

        try:

            session.query(UserSettings).filter(UserSettings.id == self.id).\
                update(mapped_values)
            session.commit()
            session.close()
            engine.dispose()

        except BaseException:

            success = False

        return success


class SystemSettings(Base):

    __tablename__ = 'System Settings'

    id = Column(Integer, primary_key=True)
    logo_uri = Column(Text)
    logo_uri_dark = Column(Text)
    logo_uri_light = Column(Text)
    force_email_users = Column(Integer)
    owner_org_id = mapped_column(ForeignKey('Organisations.org_id'))
    show_valuations = Column(Integer)
    noreply_address = Column(Text)
    noreply_body = Column(Text)
    irl_revision = Column(Text)

    def update(self):

        engine = create_engine(st.secrets.db_details.db_path)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        mapped_values = {}

        for item in SystemSettings.__dict__.items():

            field_name = item[0]
            field_type = item[1]
            is_column = isinstance(field_type, InstrumentedAttribute)

            if is_column:

                mapped_values[field_name] = getattr(self, field_name)

        session.query(SystemSettings).filter(SystemSettings.id == self.id).\
            update(mapped_values)
        session.commit()
        session.close()
        engine.dispose()


class Organisation(Base):

    __tablename__ = 'Organisations'

    org_id = Column(Integer, primary_key=True)
    org_name = Column(Text)
    active = Column(Integer)

    def __str__(self):
        return self.org_name

    def __repr__(self):
        return self.org_name


class Faculty(Base):

    __tablename__ = 'Faculties'

    fac_id = Column(Integer, primary_key=True)
    fac_name = Column(Text)
    org_id = mapped_column(ForeignKey('Organisations.org_id'))
    active = Column(Integer)

    def __str__(self):
        return self.fac_name

    def __repr__(self):
        return self.fac_name


class Department(Base):

    __tablename__ = 'Departments'

    dep_id = Column(Integer, primary_key=True)
    dep_name = Column(Text)
    fac_id = mapped_column(ForeignKey('Faculties.fac_id'))
    active = Column(Integer)

    def __str__(self):
        return self.dep_name

    def __repr__(self):
        return self.dep_name


class ProjectTeam(Base, SerializerMixin):

    __tablename__ = "Project Teams"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    project_rights = Column(Integer, ForeignKey('Permission Levels.level'))
    active = Column(Integer)

    user = relationship("User", backref="ProjectTeam")

    def update(self):

        errors = None
        engine = create_engine(st.secrets.db_details.db_path)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        uv = {'project_rights': self.project_rights, 'active': self.active}

        try:

            session.query(ProjectTeam).filter(
               ProjectTeam.id == self.id).update(uv)
            session.commit()

        except BaseException:

            errors = "Could not update project team member with user id "
            errors += f"{self.user_id}"

        session.close()
        engine.dispose()

        return errors

    def __str__(self):
        return self.user.actual_name

    def __repr__(self):
        return self.user.actual_name


@dataclass
class PermissionLevel(Base):

    __tablename__ = "Permission Levels"

    level = Column(Integer, primary_key=True)
    level_text = Column(Text)

    def __hash__(self):
        return int(self.level)

    def __repr__(self):

        return self.level_text

    def __str__(self):

        return self.level_text


class ActionPoint(Base, SerializerMixin):

    __tablename__ = "Action Points"

    ap_id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey('IRL Data.id'))
    irl_type = Column(Text(4))
    action_point = Column(Text)
    responsible = Column(Integer, ForeignKey('Users.user_id'))
    due_date = Column(Text(10))
    progress = Column(Integer)
    comment = Column(Text)

    user = relationship("User", backref="ActionPoint")

    def copy(self, ass_id):
        """
        Makes a copy of the action point, but assigns it to a new assessment.

        Parameters
        ----------
        ass_id : Integer
            The IRL Assessment ID to attach the action point to.

        Returns
        -------
        None.

        """

        new_self = ActionPoint()
        new_self.assessment_id = ass_id
        new_self.irl_type = self.irl_type
        new_self.action_point = self.action_point
        new_self.responsible = self.responsible
        new_self.due_date = self.due_date
        new_self.progress = self.progress
        new_self.comment = self.comment
        new_self.insert()

    def insert(self):

        engine = create_engine(st.secrets.db_details.db_path)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        session.add(self)
        session.commit()
        session.close()
        engine.dispose()

    def update(self):

        engine = create_engine(st.secrets.db_details.db_path)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        uv = {'action_point': self.action_point,
              'responsible': self.responsible,
              'due_date': self.due_date,
              'progress': self.progress,
              'comment': self.comment}
        session.query(ActionPoint).filter(
                ActionPoint.ap_id == self.ap_id).update(uv)
        session.commit()
        session.close()
        engine.dispose()

    def __repr__(self):

        ap_txt = self.irl_type
        ap_txt += " action point: " + self.action_point
        ap_txt += "\tProgress: " + str(self.progress) + " %"
        ap_txt += "\tDue date: " + self.due_date
        ap_txt += "\tComment: " + self.comment
        return ap_txt

    def __str__(self):

        return self.__repr__()


"""
IRL methods.
"""


def get_irl(irl_ass_id):

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    irl_ass = session.query(IRLAssessment).filter(
        (IRLAssessment.id == irl_ass_id)).first()
    session.close()
    engine.dispose()

    return irl_ass


def get_irl_ass_id(project_id):

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    irl_ass = session.query(IRLAssessment).filter(
                   IRLAssessment.project_no == project_id).order_by(
                       (IRLAssessment.assessment_date)).all()[-1]
    new_ass_id = irl_ass.id
    session.close()
    engine.dispose()

    return new_ass_id


def irl_ass_changed(irl_ass):
    """
    Check if the assessment is currently different from the one saved in
    the database.

    Parameters
    ----------
    irl_ass_id : TYPE
        DESCRIPTION.
    irl_ass : TYPE
        DESCRIPTION.

    Returns
    -------
    Bool

    """
    db_irl_ass = get_irl(irl_ass.id)
    attrs = ('crl', 'trl', 'brl', 'iprl', 'tmrl', 'frl', 'project_description')

    for attr in attrs:

        db_attr = getattr(db_irl_ass, attr)
        irl_attr = getattr(irl_ass, attr)

        if db_attr != irl_attr:

            return True

    return False


def delete_assessments(irl_asses):
    """
    Convenience method for deleted IRL assessments permanently.
    Also cleans up action points related to the assessment.

    Parameters
    ----------
    irl_ass_ids: list of ids

    Returns
    -------
    True if delections were successful, False if errors.
    """

    success = True
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    irl_ass_ids = []

    for irl_ass in irl_asses:

        irl_ass_ids.append(irl_ass.id)        
        aps = session.query(ActionPoint).filter(
            ActionPoint.assessment_id == irl_ass.id).all()
        ap_ids = [ap.ap_id for ap in aps]
        ap_dc = session.query(ActionPoint).filter(ActionPoint.ap_id.in_(ap_ids)).delete(synchronize_session=False)

        if ap_dc != len(ap_ids):

            success = False

    irl_ass_dc = session.query(IRLAssessment).filter(IRLAssessment.id.in_(irl_ass_ids)).delete(synchronize_session=False)
    session.commit()
    session.close()

    if irl_ass_dc != len(irl_ass_ids):

        success = False

    return success


def get_irl_table(irl_type, ascending=False):
    """
    Convenience method for grabbing IRL levels and descriptions from DB.

    Parameters
    ----------
    irl_type : string
        One of 'CRL', 'TRL', 'BRL', 'IPRL', 'TRL' 'FRL'.
    ascending : bool
        Returns table in ascdescending IRL level order if True,
        returns table in descending IRL level order if False (default).

    Returns
    -------
    irl_table : Pandas DataFrame
        DESCRIPTION.

    """
    assert irl_type in ['CRL', 'TRL', 'BRL', 'IPRL', 'TMRL', 'FRL']

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    if ascending:

        irl_orm = session.query(IRL).\
            filter(IRL.IRLType == irl_type).\
            order_by(IRL.Level).all()
    else:

        irl_orm = session.query(IRL).\
            filter(IRL.IRLType == irl_type).\
            order_by(desc(IRL.Level)).all()

    session.close()
    engine.dispose()
    irl_df = pd.DataFrame([item.to_dict() for item in irl_orm])

    return irl_df


def get_irl_license_value_matrix():

    df_dict = {'Level': list(range(1, 10, 1))}
    irl_types = ['CRL', 'TRL', 'BRL', 'IPRL', 'TMRL', 'FRL']
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    for irl_type in irl_types:

        irl_values = session.query(IRL.LicenseValue).\
            filter(IRL.IRLType == irl_type).\
            order_by(IRL.Level).all()
        irl_values = list(map(lambda irl_value: irl_value[0], irl_values))
        df_dict[irl_type] = irl_values

    session.close()
    engine.dispose()
    irl_df = pd.DataFrame(df_dict)

    return irl_df


def get_irl_startup_value_matrix():

    df_dict = {'Level': list(range(1, 10, 1))}
    irl_types = ['CRL', 'TRL', 'BRL', 'IPRL', 'TMRL', 'FRL']
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    for irl_type in irl_types:

        irl_values = session.query(IRL.StartupValue).\
            filter(IRL.IRLType == irl_type).\
            order_by(IRL.Level).all()
        irl_values = list(map(lambda irl_value: irl_value[0], irl_values))
        df_dict[irl_type] = irl_values

    session.close()
    engine.dispose()
    irl_df = pd.DataFrame(df_dict)

    return irl_df


def update_license_values(edited_rows):

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    for row in edited_rows.keys():

        for irl, value in edited_rows[row].items():

            session.query(IRL).filter(IRL.Level == row+1,
                                      IRL.IRLType == irl).\
                update({'LicenseValue': value})

    session.commit()
    session.close()
    engine.dispose()


def update_startup_values(edited_rows):

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    for row in edited_rows.keys():

        for irl, value in edited_rows[row].items():

            session.query(IRL).filter(IRL.Level == row+1,
                                      IRL.IRLType == irl).\
                update({'StartupValue': value})

    session.commit()
    session.close()
    engine.dispose()


"""
User methods.
"""


def add_user(new_user, password):
    """

    Parameters
    ----------
    username : TYPE
        DESCRIPTION.
    password : TYPE
        DESCRIPTION.
    rights : TYPE
        DESCRIPTION.

    Returns
    -------
    bool
        DESCRIPTION.

    """
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt).decode('utf-8')

    # Check if user doesn't already exist.
    exists = session.query(User).filter_by(username=new_user.username).first()

    if exists:

        return None

    else:

        new_user.password = hashed_password
        session.add(new_user)
        session.commit()
        new_user = session.query(User).filter(
            User.username == new_user.username).first()
        new_user_settings = UserSettings(user_id=new_user.user_id,
                                         smooth_irl=1,
                                         filter_on_user=1,
                                         remember_project=1,
                                         ascending_irl=1,
                                         ap_table_view=0,
                                         dark_mode=1)
        session.add(new_user_settings)
        session.commit()
        session.refresh(new_user)
        session.close()
        engine.dispose()

        return new_user


def get_users(active=True, org_id=None):
    """
    Fetch a list of users from the database.

    Parameters
    ----------
    active : TYPE, optional
        DESCRIPTION. The default is True.
    org_id : Integer, optional
        If not None, returns only users belonging to the organisation with the
        given org_id. The default is None.

    Returns
    -------
    users : List of User
        DESCRIPTION.

    """
    active = int(active)
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    if org_id is None:

        users = session.query(User).filter(User.active == int(active)).all()

    else:

        users = session.query(User).filter(
            (User.active == active) &
            (User.org_id == org_id)).all()

    session.close()
    engine.dispose()

    return users


def get_user_id(username):
    """
    Get the user ID of a specific username.

    Parameters
    ----------
    username : string
        DESCRIPTION.

    Returns
    -------
    user_id : integer
        DESCRIPTION.

    """

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user_id = None
    db_user = session.query(User).filter(User.username == username).first()

    if db_user is not None:

        user_id = db_user.user_id

    session.close()
    engine.dispose()

    return user_id


def has_password(username):
    """
    Convenience method to check if a user has a password.
    If password is not set, returns False.
    Can be used to ask for a password on first time login.

    Parameters
    ----------
    username : str
        Username provided from the UI.

    Returns
    -------
    has_pw : Bool
        True if user has a password, False else.

    """
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter(User.username == username).first()
    has_pw = (user.password is not None)

    session.close()
    engine.dispose()

    return has_pw


def is_user(username):
    """
    Convenience method to check if a user exists.

    Parameters
    ----------
    username : str
        Username provided from the UI.

    Returns
    -------
    has_pw : Bool
        True if user exists, False else.

    """
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter(User.username == username).first()
    is_user = user is not None

    session.close()
    engine.dispose()

    return is_user


def validate_user(user, password):
    """

    Parameters
    ----------
    user : TYPE
        DESCRIPTION.
    password : TYPE
        DESCRIPTION.

    Returns
    -------
    db_user : TYPE
        DESCRIPTION.

    """

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    password = password.encode('utf-8')
    db_user = session.query(User).filter(User.username == user).first()
    verified = (db_user and bcrypt.checkpw(
        password, db_user.password.encode('utf-8')))
    session.close()
    engine.dispose()

    if not verified:

        db_user = None

    return db_user


def change_user_password(user, password):
    """
    Change user password.

    Parameters
    ----------
    user : base.User
        DESCRIPTION.
    password : string
        DESCRIPTION.

    Returns
    -------
    bool
        True if change was successful, false if not.

    """

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt).decode('utf-8')
    stmt = (update(User).where(
        User.user_id == user.user_id).values(password=hashed_password))

    try:

        session.execute(stmt)
        success = True

    except BaseException:

        success = False

    session.commit()
    session.close()
    engine.dispose()

    return success


def change_user_rights(user, rights):
    """
    Change user permission level.

    Parameters
    ----------
    user : User
        DESCRIPTION.
    rights : Integer
        0-9.

    Returns
    -------
    success : Bool
        True if update was successful, False otherwise.

    """

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    stmt = (update(User).where(
        User.user_id == user.user_id).values(rights=rights.level))

    try:

        session.execute(stmt)
        success = True

    except BaseException:

        success = False

    session.commit()
    session.close()
    engine.dispose()
    return success


def change_user_status(users, active):
    """
    Change user status.

    Parameters
    ----------
    users : list of user names
        List of users to update.
    active : bool
        Set user active status. We don't delete users for historical resasons.

    Returns
    -------
    bool
        True if change was successful, false if not.

    """

    active = int(active)
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:

        session.query(User).filter(
            User.username.in_(users)).update({'active': active})
        success = True

    except BaseException:

        success = False

    session.commit()
    session.close()
    engine.dispose()

    return success


def get_user(name_or_id):
    """

    Parameters
    ----------
    username : string or int
        Must be a valid username or user id.

    Returns
    -------
    user : base.User
        DESCRIPTION.

    """
    assert type(name_or_id) in [str, int]

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    if type(name_or_id) is str:

        user = session.query(User).filter(User.username == name_or_id).first()

    else:

        user = session.query(User).filter(User.user_id == name_or_id).first()

    session.close()
    engine.dispose()

    return user


def get_user_settings(user_id):
    """


    Parameters
    ----------
    user : TYPE
        DESCRIPTION.

    Returns
    -------
    user_settings : TYPE
        DESCRIPTION.

    """

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user_settings = session.query(
        UserSettings).filter(UserSettings.user_id == user_id).first()
    session.close()
    engine.dispose()

    return user_settings


"""
System settings methods.
"""


def get_system_settings():
    """
    Convenience method for grabbing system settings from DB.

    Parameters
    ----------
    None

    Returns
    -------
    irl_table : Pandas DataFrame
        DESCRIPTION.

    """
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    sys_settings = session.query(
        SystemSettings).filter(SystemSettings.id == 1).first()
    session.close()
    engine.dispose()

    return sys_settings


"""
Project methods.
"""


def change_project_status(projects, active):
    """
    Change project status.

    Parameters
    ----------
    users : list of IRLAssessment
        List of projects to update.
    active : bool
        Set project active status.
        We don't delete projects for historical resasons.

    Returns
    -------
    bool
        True if change was successful, false if not.

    """

    active = int(active)
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    project_nos = [p.project_no for p in projects]

    try:

        session.query(IRLAssessment).filter(
            IRLAssessment.project_no.in_(
                project_nos)).update({'active': active})
        success = True

    except BaseException:

        success = False

    session.commit()
    session.close()
    engine.dispose()

    return success


def get_projects(user, filt=True, active=True):
    """
    Fetch IRL data from the database.

    Parameters
    ----------
    user : User
        The current user.
    filt : Bool, optional
        If True, will only display the projects the user is project leader on.
        If False, will display all projects where the user is part of the
        project team for access levels 0-3.
        For access level 8 (SuperUser) all projects for this SuperUser's
        organisation will be returned.
        For access level 9 (Administrator), all projects will be returned.
        The default is True.
    active : Bool, optional
        If True, returns only active projects.
        If False, returns only inactive projects.
        The default is True.

    Returns
    -------
    List of IRLData objects.

    """

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    active = int(active)

    irl_data = session.query(IRLAssessment).order_by(
        func.max(IRLAssessment.assessment_date)).group_by(
            IRLAssessment.project_no).where(
                IRLAssessment.active == active).all()

    filt_irl_data = []

    if user.rights == 9 and filt is True:
        
        for project in irl_data:

            if project.project_leader_id == user.user_id:

                filt_irl_data.append(project)

        irl_data = filt_irl_data

    elif user.rights == 8:

        users = get_users(True, org_id=user.org_id)
        user_ids = [user.user_id for user in users]

        for project in irl_data:

            if filt:

                if project.project_leader_id == user.user_id:

                    filt_irl_data.append(project)

            else:

                if project.project_leader_id in user_ids:

                    filt_irl_data.append(project)

        irl_data = filt_irl_data

    elif user.rights <= 3:

        irl_data = session.query(IRLAssessment).order_by(
            func.max(IRLAssessment.assessment_date)).group_by(
                IRLAssessment.project_no).filter(
                    (ProjectTeam.user_id == user.user_id) &
                    (ProjectTeam.active == 1) &
                    (IRLAssessment.project_no == ProjectTeam.project_id) &
                    (IRLAssessment.active == active)).all()

        if filt:

            for project in irl_data:

                if project.project_leader_id == user.user_id:

                    filt_irl_data.append(project)

            irl_data = filt_irl_data

    session.close()
    engine.dispose()

    return irl_data


def get_project_history(project_id):
    """
    Get IRL assessments for all projects.
    If user is specified, returns only projects where the specified user is
    project leader.
    """

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    irl_data = session.query(IRLAssessment).order_by(
            IRLAssessment.assessment_date).where(
                    IRLAssessment.project_no == project_id).all()

    session.close()
    engine.dispose()

    return irl_data


def get_project_rights(project_id, user_id):

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    rights = session.query(ProjectTeam).where(
                    (ProjectTeam.project_id == project_id) &
                    (ProjectTeam.user_id == user_id)).first()
    session.close()
    engine.dispose()

    if rights is None:

        return 1

    else:

        return rights.project_rights


def get_project_team(project_id, active=True):
    """
    Convenience method for fetching the project team.

    Parameters
    ----------
    project_id : integer
        The unique project id from the database.
    active : bool, optional
        If True, only returns active project members.
        If False, will return all members that have been part of the project
        team at any point in its history.
        The default is True.

    Returns
    -------
    team_df : Pandas DataFrame
        DESCRIPTION.

    """

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    if active is True:

        team = session.query(ProjectTeam).order_by(
                ProjectTeam.user_id).where(
                        (ProjectTeam.project_id == project_id) &
                        (ProjectTeam.user_id == User.user_id) &
                        (ProjectTeam.active == active)).all()

    else:

        team = session.query(ProjectTeam).order_by(
                ProjectTeam.user_id).where(
                        (ProjectTeam.project_id == project_id) &
                        (ProjectTeam.user_id == User.user_id)).all()

    members = []
    user_objs = []

    for member in team:

        # This is hackish and the order matters as we have the active flag
        # for both users and team members. The latter overwrites the former.
        row = member.user.to_dict()
        row.update(member.to_dict())
        members.append(row)
        user_objs.append(member.user)

    team_df = pd.DataFrame(members)
    team_df['team_obj'] = team
    team_df['user_obj'] = user_objs
    session.close()
    engine.dispose()

    return team_df


def is_project(project_no):

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    exists = session.query(IRLAssessment).filter_by(
        project_no=project_no).first()
    session.close()
    engine.dispose()

    if exists:

        return True

    else:

        return False


def get_orgs():
    """
    Return all active organisations in the database.
    TODO: Implement active

    Returns
    -------
    orgs : TYPE
        DESCRIPTION.

    """
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    orgs = session.query(Organisation).order_by(
        Organisation.org_name).where(
            Organisation.active == 1).all()
    session.close()
    engine.dispose()

    return orgs


def get_facs(org):
    """
    Return all active organisations in the database.

    Returns
    -------
    orgs : TYPE
        DESCRIPTION.

    """
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    facs = session.query(Faculty).order_by(
        Faculty.fac_name).where(
            Faculty.org_id == org.org_id,
            Faculty.active == 1).all()
    session.close()
    engine.dispose()

    return facs


def get_deps(fac):
    """
    Return all active organisations in the database.

    Returns
    -------
    orgs : TYPE
        DESCRIPTION.

    """
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    deps = session.query(Department).order_by(
        Department.dep_name).where(
            Department.fac_id == fac.fac_id,
            Department.active == 1).all()
    session.close()
    engine.dispose()

    return deps


def get_permission_levels(user=None):
    """
    Get a list of all permission leveles in the database.

    Returns
    -------
    list : PermissionLevel
        DESCRIPTION.

    """
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    if user is None:

        pls = session.query(PermissionLevel).all()

    else:

        pls = session.query(PermissionLevel).where(
            PermissionLevel.level <= user.rights).all()

    session.close()
    engine.dispose()

    return pls


def get_permission_level_map():
    """
    Get a mapping from permission level texts to permission level ids.
    This is needed because I can't find a way to use the PermissionLevel
    object inside st.selectbox in st.data_editor. It is probably feasible,
    which would be ideal, but I don't know how to do it right now.

    Returns
    -------
    pm_map : dict
        Dictionary with permission level labels as keys and level ID as values.

    """
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    pms = session.query(PermissionLevel).all()
    session.close()
    engine.dispose()
    pm_map = {}

    for pm in pms:

        pm_map[pm.level_text] = pm.level

    return pm_map


def add_project_team(project_no, team):

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    errors = None

    try:

        for user in team:

            team_member = ProjectTeam()
            team_member.project_id = project_no
            team_member.user_id = user.user_id
            team_member.project_rights = user.rights
            team_member.active = 1
            session.add(team_member)

        session.commit()

    except BaseException:

        errors = "Error adding new team members!"

    session.close()
    engine.dispose()

    return errors


""" Organisation, department and faculty methods."""


def add_org(org_name):

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    new_org = Organisation()
    new_org.org_name = org_name
    new_org.active = True
    session.add(new_org)
    session.commit()
    new_org = session.query(Organisation).filter(
        Organisation.org_name == org_name).first()
    session.close()
    engine.dispose()

    return new_org.org_id


def add_fac(org_id, fac_name):

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    new_fac = Faculty()
    new_fac.org_id = org_id
    new_fac.fac_name = fac_name
    new_fac.active = True
    session.add(new_fac)
    session.commit()
    new_fac = session.query(Faculty).filter(
        (Faculty.org_id == org_id) & (Faculty.fac_name == fac_name)).first()
    session.close()
    engine.dispose()

    return new_fac.fac_id


def add_dep(fac_id, dep_name):

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    new_dep = Department()
    new_dep.fac_id = fac_id
    new_dep.dep_name = dep_name
    new_dep.active = True
    session.add(new_dep)
    session.commit()
    new_dep = session.query(Department).filter(
        (Department.fac_id == fac_id) &
        (Department.dep_name == dep_name)).first()
    session.close()
    engine.dispose()

    return new_dep.dep_id


"""
Action points methods.
"""


def get_ap(ap_id):
    """
    Get the action point object corresponding to the action point id.

    Parameters
    ----------
    ap_id : Integer
        Unique action point database ID.

    Returns
    -------
    ap : ActionPoint
        DESCRIPTION.

    """
    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    ap = session.query(ActionPoint).filter(ActionPoint.ap_id == ap_id).first()
    session.close()
    engine.dispose()

    return ap


def get_action_points(irl_ass_id, irl_type=None):
    """
    Get all action points related to the project IRL assessment.

    Parameters
    ----------
    irl_ass_id : Integer
        IRL Assessment ID
    irl_type : String, optional
        If specified returns only action points for the indicated IRL type.
        Valid values are CRL, TRL, BRL, IPRL, TMRL, FRL.
        The default is None.

    Returns
    -------
    aps_df : Pandas DataFrame
        Pandas DataFrame containing all action points.
        If no action points exists, returns empty dataframe with correct
        columns.
    """
    if irl_type is not None:

        assert irl_type in ('CRL', 'TRL', 'BRL', 'IPRL', 'TMRL', 'FRL')

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    if irl_type is None:

        aps = session.query(ActionPoint).filter(
            ActionPoint.assessment_id == irl_ass_id).all()

    else:

        aps = session.query(ActionPoint).filter(
            (ActionPoint.assessment_id == irl_ass_id) &
            (ActionPoint.irl_type == irl_type)).all()

    points = []
    user_objs = []

    for ap in aps:

        # This is hackish and the order matters as we have the active flag
        # for both users and team members. The latter overwrites the former.
        row = ap.user.to_dict()
        row.update(ap.to_dict())
        points.append(row)
        user_objs.append(ap.user)

    aps_df = pd.DataFrame(points)

    if len(points) > 0:

        aps_df['aps'] = points
        aps_df['user_obj'] = user_objs
        aps_df['due_date'] = utils.dbdates2datetimes(aps_df['due_date'])

    session.close()
    engine.dispose()

    # If no action points exists, return empty dataframe but with correct cols.
    if len(aps_df.index) == 0:

        columns = ['user_id', 'actual_name', 'username', 'password', 'rights',
                   'active', 'org_id', 'fac_id', 'dep_id', 'id',
                   'assessment_id', 'irl_type', 'action_point', 'responsible',
                   'due_date', 'progress', 'comment', 'aps', 'user_obj']
        aps_df = pd.DataFrame(columns=columns)

    return aps_df


def ap_completed(irl_ass_id):
    """
    Check if all action points are completed before making a new assessment.
    ALSO - if today's date == irl_ass_id.assessment_date, return True.'

    Parameters
    ----------
    irl_ass_id : Integer
        IRL Assessment ID.

    Returns
    -------
    completed : Bool
        True if all action points completed, False is not.

    """
    date = utils.datetime2dbdate(datetime.now())
    irl = get_irl(irl_ass_id)
    ass_date = irl.assessment_date

    if date == ass_date:

        return True

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    aps = session.query(ActionPoint).filter(
            ActionPoint.assessment_id == irl_ass_id).all()
    completion = session.query(func.sum(ActionPoint.progress)).filter(
                (ActionPoint.assessment_id == irl_ass_id)).scalar()
    session.close()
    engine.dispose()

    completed = (len(aps)*100 == completion) or len(aps) == 0

    return completed


def copy_aps(old_ass_id, new_ass_id):
    """
    Copy unfinished action points from an old assessment to a new one.

    Parameters
    ----------
    old_ass_id : TYPE
        DESCRIPTION.
    new_ass_id : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    engine = create_engine(st.secrets.db_details.db_path)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    old_aps = session.query(ActionPoint).filter(
                           ActionPoint.assessment_id == old_ass_id).all()

    for old_ap in old_aps:

        old_ap.copy(new_ass_id)

    session.close()
    engine.dispose()
