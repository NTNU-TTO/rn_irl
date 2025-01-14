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


def on_project_team_edit_change():
    """
    Event handler for changing the team to edit.

    Returns
    -------
    None.

    """

    project = ss.project_team_to_edit
    ss.team_df = base.get_project_team(project.project_no, False)


def on_add_new_project():
    """
    Event handler for adding new projects to the database.

    Returns
    -------
    None.

    """

    project_no = ss.new_project_no
    project_name = ss.new_project_name
    project_members = ss.new_project_members
    project_leader = ss.new_project_leader

    if not project_no.isdigit():

        ss.add_new_project_status = 2
        return

    if base.is_project(project_no):

        ss.add_new_project_status = 6
        return

    if not project_name.isascii():

        ss.add_new_project_status = 3
        return

    if len(project_members) == 0:

        ss.add_new_project_status = 4
        return

    if project_leader is None:

        ss.add_new_project_status = 5
        return

    project = base.IRLAssessment()
    project.project_no = project_no
    project.project_name = project_name
    project.project_leader_id = project_leader.user_id
    project.crl = 1
    project.trl = 1
    project.brl = 1
    project.iprl = 1
    project.tmrl = 1
    project.frl = 1
    project.crl_target = 1
    project.trl_target = 1
    project.brl_target = 1
    project.iprl_target = 1
    project.tmrl_target = 1
    project.frl_target = 1
    project.active = 1
    proj_error = project.insert()
    team_error = base.add_project_team(project_no, project_members)
    ss.refresh = True
    error = None

    if proj_error is not None:

        error = proj_error

    if team_error is not None:

        if error is None:

            error = team_error

        else:

            error + " " + team_error

    if error is None:

        ss.add_new_project_status = 1


def on_apply_project_team_changes():
    """
    Event handler for saving project team changes to the database.

    Returns
    -------
    None.

    """
    project_no = ss.project_team_to_edit.project_no
    new_members = ss.add_new_project_members

    # Add new project members.
    # TODO: Add status variable on succes and failure.
    if len(new_members) > 0:

        base.add_project_team(project_no, new_members)

    new_pl = ss.change_project_leader

    if new_pl is not None:

        ss.project_team_to_edit.project_leader_id = new_pl.user_id
        ss.project_team_to_edit.update()

    team_changes = ss.project_team_editor['edited_rows']

    for row in team_changes.keys():

        team_member = ss.team_df.loc[row]['team_obj']
        df_row = team_changes[row]

        for col, val in df_row.items():

            if col == 'access_level':

                val = ss.pm_map[val]
                col = 'project_rights'

            setattr(team_member, col, val)

        team_member.update()

    ss.team_df = None

# The action starts here.
if ss.get('user_settings', None) is None:

    dark_mode = True

else:

    dark_mode = ss.user_settings.dark_mode

ui.add_logo(dark_mode)

user = ss.user
users = base.get_users()

ui.add_new_project(users, on_add_new_project)
st.divider()
st.subheader("Edit project team")
ui.edit_project_team(users,
                     on_project_team_edit_change,
                     on_apply_project_team_changes)
st.divider()
ui.change_project_status(user)
