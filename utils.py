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

import streamlit as st
import pandas as pd
import base

from datetime import datetime
from streamlit import session_state as ss


BACKEND = 'sqlite'


def datetime2dbdate(datetime):
    """
    Convenience method to convert from datetime.date to ISO standard
    date string which we store in the database.

    Returns
    -------
    date : str
        ISO standard date (YYYY-MM-DD).
    """

    dbdate = '%d-%02d-%02d' % (datetime.year, datetime.month, datetime.day)

    return dbdate


def dbdate2datetime(date):

    if date is None:

        return datetime.now()

    else:

        yyyy, mm, dd = str(date).split('-')
        yyyy = int(yyyy)
        mm = int(mm)
        dd = int(dd)

    return datetime(yyyy, mm, dd)


def dbdates2datetimes(date_list):

    datetimes = []

    for dbdate in date_list:

        datetimes.append(dbdate2datetime(dbdate))

    return datetimes


def get_IRL_data(user):
    """
    Utility method for getting IRL data.
    Will only refresh from database when needed.

    Parameters
    ----------
    user : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    refresh = ss.get("refresh", True)
    # Fetch from database only when and if we need to do so.
    if refresh:

        filt = ss.user_settings.filter_on_user
        ss.projects = base.get_projects(user, filt)
        ss.refresh = False


def get_project_history(project_id):

    irl_data = base.get_project_history(project_id)
    ss.project_history = irl_data


def get_project_team(user):

    users = base.get_users()
    perms = base.get_permission_levels(user)
    project_team = pd.DataFrame(columns=["User", "Permission Level"])
    # project_team["User"] = pd.Series(users).astype("category")
    # project_team["Permission Level"] = pd.Series(perms).astype("category")
    column_config = {
        "User": st.column_config.SelectboxColumn(
            "User",
            help="Project team member",
            width="medium",
            options=users,
            required=True,
            ),
        "Permission Level": st.column_config.SelectboxColumn(
            "Permission Level",
            help="Permissio level",
            width="medium",
            options=perms,
            required=True,
            ),
        }

    return project_team, column_config
