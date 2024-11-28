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


def on_save_user_settings():
    """
    Event handler for saving the current user settings to the database.

    Returns
    -------
    None.

    """

    settings = ss.user_settings
    settings.smooth_irl = int(ss.smooth_irl)
    settings.filter_on_user = int(ss.filter_on_user)
    settings.remember_project = int(ss.remember_project)
    settings.ascending_irl = int(ss.ascending_irl)
    settings.dark_mode = int(ss.dark_mode)
    settings.ap_table_view = int(ss.ap_table_view)
    settings.update()
    ss.refresh = True


def on_save_system_settings():
    """
    Event handler for saving the current system settings to the database.

    Returns
    -------
    None.

    """

    settings = ss.system_settings
    settings.logo_uri = ss.logo_uri
    settings.logo_uri_dark = ss.logo_uri_dark
    settings.logo_uri_light = ss.logo_uri_light
    settings.show_valuations = int(ss.show_valuations)
    settings.update()
    edited_rows = ss.startup_value_matrix['edited_rows']
    base.update_startup_values(edited_rows)
    edited_rows = ss.license_value_matrix['edited_rows']
    base.update_license_values(edited_rows)


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


def main():

    if ss.get("pm_map", None) is None:

        ss.pm_map = base.get_permission_level_map()

    user_settings_exp = st.expander("User Settings", expanded=False)
    user_settings = ss['user_settings']
    user = ss.user

    # The user settings.
    with user_settings_exp:

        ui.user_settings(user_settings, on_save_user_settings)

    # Project changes are allowed for only some user rights.
    if user.rights >= 2:

        project_tools = st.expander("Project tools")
        users = base.get_users()

        with project_tools:

            ui.add_new_project(users, on_add_new_project)
            st.divider()
            st.subheader("Edit project team")
            ui.edit_project_team(users,
                                 on_project_team_edit_change,
                                 on_apply_project_team_changes)

            if user.rights >= 3:

                st.divider()
                ui.change_project_status(user)

    admin_tools = st.expander("Admin tools")

    with admin_tools:

        if user.rights == 9:
            ui.add_user()
            st.divider()

        ui.change_password(user)

        if user.rights == 9:

            st.divider()
            ui.change_user_status()

        if user.rights == 9:

            st.divider()
            ui.add_organisation(on_add_organisation)
            ui.add_faculties(on_add_faculties)
            ui.add_departments(on_add_departments)

    if user.rights == 9:

        sys_settings = st.expander("System Settings")

        with sys_settings:

            sys_settings = base.get_system_settings()
            cols1 = st.columns(2)
            cols1[0].text_input("Dark mode logo URI",
                                key="logo_uri_dark",
                                value=sys_settings.logo_uri_dark)
            cols1[1].text_input("Light mode logo URI",
                                key="logo_uri_light",
                                value=sys_settings.logo_uri_light)

            cols2 = st.columns(2, vertical_alignment="bottom")
            cols2[0].text_input("Logo web page link",
                                key='logo_uri',
                                value=sys_settings.logo_uri)
            cols2[1].checkbox("Show valuations",
                              key="show_valuations",
                              value=sys_settings.show_valuations)
            st.markdown("Startup Valuation Matrix")
            st.data_editor(base.get_irl_startup_value_matrix(),
                           use_container_width=True,
                           hide_index=True,
                           key="startup_value_matrix")
            st.markdown("License Valuation Matrix")
            st.data_editor(base.get_irl_license_value_matrix(),
                           use_container_width=True,
                           hide_index=True,
                           key="license_value_matrix")
            st.button("Apply system settings",
                      on_click=on_save_system_settings)


if __name__ == '__main__':

    ui.setup_page()
    # Currently no sensible way to get theme information.
    # We assume dark as this is default until otherwise is proven by user.
    if ss.get('user_settings', None) is None:

        dark_mode = True

    else:

        dark_mode = ss.user_settings.dark_mode

    ui.add_logo(dark_mode)

    if ss.get('user', None) is None:

        ss['go_to_page'] = 'pages/5_Settings.py'
        st.switch_page('pages/2_Login.py')

    else:

        main()
