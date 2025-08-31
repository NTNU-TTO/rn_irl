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
import base
import ui

from streamlit import session_state as ss

###################
# Event handlers. #
###################


def on_add_organisation():
    """
    Add organisations to the database.
    Optionally also adds faculties if present in the UI.

    Returns
    -------
    None.

    """
    org = ss.new_org
    org_id = base.add_org(org)

    for faculty in ss.new_fac.split("\n"):

        base.add_fac(org_id, faculty)

    ss.new_org = None
    ss.new_fac = None


def on_add_faculties():
    """
    Adds faculties to an existing organisation.

    Returns
    -------
    None.

    """
    org_id = ss.select_org.org_id

    for fac in ss.new_facs.split("\n"):

        base.add_fac(org_id, fac)

    ss.new_facs = None


def on_add_departments():
    """
    Returns
    -------
    None.

    """

    fac_id = ss.select_fac.fac_id

    for dep in ss.new_deps.split("\n"):

        base.add_dep(fac_id, dep)

    ss.new_deps = None

# The action starts here.
dark_mode = (st.context.theme.type == 'dark')
ui.add_logo(dark_mode)

user = ss.user
ui.add_user()
st.divider()
ui.change_password(user, True)
st.divider()
ui.change_user_rights()
st.divider()
ui.change_user_status()
st.divider()
ui.add_organisation(on_add_organisation)
st.divider()
ui.add_faculties(on_add_faculties)
st.divider()
ui.add_departments(on_add_departments)
