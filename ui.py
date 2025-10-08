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
import pandas as pd
import streamlit as st
import time

import base
import utils

from streamlit import session_state as ss

ABOUT_TXT = "User Friendly KTH Innovation Readiness Level™ Assessment Tool\n\
            Copyright (c) Lodve Berre and NTNU Technology Transfer AS"

HIDE_TABLE_ROW_INDEX = """
                       <style>
                       thead tr th:first-child {display:none}
                       tbody th {display:none}
                       </style>
                       """

IRL_COLOR_MAP = {9: '#37953B',
                 8: '#37913B',
                 7: '#71AF34',
                 6: '#D5D311',
                 5: '#FDDE16',
                 4: '#FCB927',
                 3: '#F99B08',
                 2: '#D66016',
                 1: '#A8202F'}

# Default menu items.
menu_items = {"Get Help": "https://kthinnovationreadinesslevel.com/",
              "Report a Bug": "https://github.com/NTNU-TTO/rn_irl/issues",
              "About": ABOUT_TXT}


# Detailed IRL scale descriptions.
crl_desc = base.get_irl_table('CRL')[['Level', 'Aspects']]
trl_desc = base.get_irl_table('TRL')[['Level', 'Aspects']]
brl_desc = base.get_irl_table('BRL')[['Level', 'Aspects']]
iprl_desc = base.get_irl_table('IPRL')[['Level', 'Aspects']]
tmrl_desc = base.get_irl_table('TMRL')[['Level', 'Aspects']]
frl_desc = base.get_irl_table('FRL')[['Level', 'Aspects']]


def on_init_system():
    """
    Initialise essential system settings and add first user on first run.
    TODO: Should probably add some checks on orgs etc _but_ on the other hand,
          this function is only used once unless something is VERY wrong.

    Returns
    -------
    None.

    """

    fac_id = None
    dep_id = None
    pw1 = ss.new_pw1
    pw2 = ss.new_pw2

    if pw1 != pw2:

        # Passwords didn't match.
        ss.add_new_user_status = 0
        return

    permissions = ss.new_permissions.level
    org_id = base.add_org(ss.new_user_org)

    if ss.new_user_fac not in (None, ""):

        fac_id = base.add_fac(org_id, ss.new_user_fac)

    if ss.new_user_dep not in (None, ""):

        dep_id = base.add_dep(fac_id, ss.new_user_dep)

    user = base.User()
    user.actual_name = ss.new_name
    user.username = ss.new_username
    user.rights = permissions
    user.active = 1
    user.org_id = org_id
    user.fac_id = fac_id
    user.dep_id = dep_id

    user = base.add_user(user, pw1)

    if user is not None:

        # Yay! It worked!
        ss.add_new_user_status = 1
        settings = base.get_system_settings()
        settings.owner_org_id = org_id
        settings.logo_uri = ss.logo_uri
        settings.logo_uri_dark = ss.logo_uri_dark
        settings.logo_uri_light = ss.logo_uri_light
        settings.update()
        ss.status = 'verified'
        ss.user = user
        ss.user_settings = base.get_user_settings(user.user_id)
        ss.dark_mode = (st.context.theme.type == 'dark')
        ss.projects = base.get_projects(user, ss.user_settings.filter_on_user)
        ss.refresh = False

    else:

        # Dammit. Something went wrong and I don't know what.
        ss.add_new_user_status = 2

    user = base.validate_user(ss.new_username, pw1)


def on_add_new_user():

    pw1 = ss.new_pw1
    pw2 = ss.new_pw2

    if pw1 != pw2:

        # Passwords didn't match.
        ss.add_new_user_status = 0
        return

    permissions = ss.new_permissions.level
    org_id = ss.new_user_org.org_id

    if ss.new_user_fac is not None:

        fac_id = ss.new_user_fac.fac_id

    else:

        fac_id = None

    if ss.new_user_dep is not None:

        dep_id = ss.new_user_dep.dep_id

    else:

        dep_id = None

    user = base.User()
    user.actual_name = ss.new_name
    user.username = ss.new_username
    user.rights = permissions
    user.active = 1
    user.org_id = org_id
    user.fac_id = fac_id
    user.dep_id = dep_id

    user = base.add_user(user, pw1)

    if user is not None:

        # Yay! It worked!
        ss.add_new_user_status = 1

    else:

        # User already exists.
        ss.add_new_user_status = 2


def irl_color(irl):
    """
    Fecth the correct color to use for background based on irl level.

    Parameters
    ----------
    irl : Integer
        IRL Value from 1-9.

    Returns
    -------
    bg_color : TYPE
        DESCRIPTION.

    """

    color = IRL_COLOR_MAP[irl]
    bg_color = f'background-color: {color};'
    bg_color += 'color: black; font-weight: bold; text-align: center'

    return bg_color


def add_logo(dark_mode=True):
    """
    Function for adding a logo on top of the sidebar.
    Works best with svg files, which currently can't be stored locally.
    We currently must store these on-line somewhere.
    """
    if ss.get('system_settings', None) is None:

        ss.system_settings = base.get_system_settings()

    if dark_mode:

        luri = ss.system_settings.logo_uri_dark

    else:

        luri = ss.system_settings.logo_uri_light

    st.logo(luri, link=ss.system_settings.logo_uri)


def setup_page():
    """
    Default page setup.
    Sets wide layout, sets page title, page icon and default menu items.
    """

    st.set_page_config(layout="wide",
                       page_title="Really Nice IRL",
                       page_icon="static/really_nice_logo.png",
                       menu_items=menu_items)


def make_grid(cols, rows):
    """
    Implementation of grid layout using standard containers.
    NOTE: Does not work well with portrait mode on phones!
    """
    grid = [0]*rows

    for i in range(rows):

        with st.container():

            grid[i] = st.columns(cols)

    return grid


def make_action_points(prefix, project_data, ap_cb, expanded=False):

    # Target levels and notes.
    header = "Targets and action points per %s:"
    header = header % ss.project.assessment_date
    irl_cats = ['CRL', 'TRL', 'BRL', 'IPRL', 'TMRL', 'FRL']
 
    with st.form(key=f"{prefix}_ap_form", border=False):
        
        st.checkbox("Show target levels in plot",
                    ss[prefix + "_plot_targets"],
                    key=prefix + "_plot_targets")
        st.text_area("Project notes",
                     ss[prefix + "_project_notes"],
                     key=prefix + "_project_notes")
        ats = st.tabs(irl_cats)

        for at, irl_cat in zip(ats, irl_cats):

            low_cat = irl_cat.lower()

            with at:

                at_col1, at_col2, at_col3 = st.columns(3)
                team = base.get_project_team(ss.project.project_no)

                with at_col1:

                    index = getattr(ss.project, '%s_target' % low_cat)-1
                    st.selectbox("%s Target Level" % irl_cat,
                                 options=[1, 2, 3, 4, 5, 6, 7, 8, 9],
                                 key='%s_%s_target' % (prefix, low_cat),
                                 index=index)

                with at_col2:

                    key = f"{prefix}_{low_cat}_target_lead"
                    lead = ss[key]                    
                    options = team.username.to_list()
                    st.selectbox("Lead:",
                                 options=options,
                                 key=key)

                with at_col3:

                    key = f"{prefix}_{low_cat}_target_duedate"
                    date = ss[key]
                    st.date_input("Due date:",
                                  key=key,
                                  format="YYYY-MM-DD",
                                  value=date)
                    
                key = f"{prefix}_{low_cat}_notes"
                st.text_area("%s general comments:" % irl_cat,
                             value=ss[key],
                             key=key)

                aps = base.get_action_points(ss.project.id, irl_cat)
                ss["%s_%s_df" % (prefix, low_cat)] = aps
                cc = {"action_point":
                      st.column_config.TextColumn(
                          "Action Point",
                          help="Action Point",
                          width="medium",
                          disabled=False,
                          required=True),
                      "username":
                      st.column_config.SelectboxColumn(
                          "Responsible",
                          help="Project member responsible for action point",
                          width="small",
                          options=team.username.to_list(),
                          disabled=False,
                          required=True,
                          ),
                      "progress":
                      st.column_config.SelectboxColumn(
                          "Progress",
                          options=list(range(0, 110, 10)),
                          help="Action point progress in percents",
                          width="small",
                          default=0),
                      "due_date":
                      st.column_config.DateColumn(
                          "Due date",
                          help="Action pooint due date",
                          width="small",
                          format="YYYY-MM-DD",
                          disabled=False,
                          required=True),
                      "comment":
                      st.column_config.TextColumn(
                          "Comment",
                          help="Comments to action point progress",
                          width="medium",
                          disabled=False,
                          required=False)}
                st.data_editor(aps,
                               column_order=['action_point',
                                             'username',
                                             'progress',
                                             'due_date',
                                             'comment'],
                               column_config=cc,
                               width='stretch',
                               hide_index=True,
                               num_rows="dynamic",
                               key='%s_%s_aps' % (prefix, low_cat))

        st.form_submit_button("Update action points", on_click=ap_cb)

        # mom = ss.get("mom", None)

        # # TODO: Make this work.
        # if mom is not None:

        #     team = ""
        #     project_team = base.get_project_team(project_data.id)

        #     for member in project_team.itertuples():

        #         user = base.get_user(team.user_id)
        #         email = user.username
        #         team += email + ";"

        #     st.write(team)
        #     href = f'<a href="mailto:{team}'
        #     href += '?subject=Minutes of Meeting'
        #     href += '">Send Minutes of Meeting</a>'
        #     st.markdown(href, unsafe_allow_html=True)


def show_action_points(prefix, project_data, ap_cb, expanded=False):

    # Target levels and notes.
    header = "Targets and action points per %s:"
    header = header % project_data.assessment_date
    irl_cats = ['CRL', 'TRL', 'BRL', 'IPRL', 'TMRL', 'FRL']

    st.text_area("Project notes",
                 project_data.project_notes,
                 key=prefix + "_project_notes",
                 disabled=True)
    ats = st.tabs(irl_cats)

    for at, irl_cat in zip(ats, irl_cats):

        low_cat = irl_cat.lower()

        with at:

            at_col1, at_col2, at_col3 = st.columns(3)
            team = base.get_project_team(project_data.project_no)

            with at_col1:

                index = getattr(project_data, '%s_target' % low_cat)-1
                st.selectbox("%s Target Level" % irl_cat,
                             options=[1, 2, 3, 4, 5, 6, 7, 8, 9],
                             key='%s_%s_target' % (prefix, low_cat),
                             index=index,
                             disabled=True)

            with at_col2:

                lead = getattr(project_data,
                               "%s_target_lead" % low_cat)
                key = "%s_%s_target_lead" % (prefix, low_cat)
                options = team.username.to_list()

                if lead is not None:

                    lead = options.index(lead)

                st.selectbox("Lead:",
                             options=options,
                             key=key,
                             index=lead,
                             disabled=True)

            with at_col3:

                date = getattr(project_data,
                               "%s_target_duedate" % low_cat)
                st.date_input("Due date:",
                              key='%s_%s_duedate' % (prefix, low_cat),
                              format="YYYY-MM-DD",
                              value=utils.dbdate2datetime(date),
                              disabled=True)

            st.text_area("%s general comments:" % irl_cat,
                         value=getattr(project_data,
                                       '%s_notes' % low_cat),
                         key='%s_%s_notes' % (prefix, low_cat),
                         disabled=True)

            aps = base.get_action_points(project_data.id, irl_cat)
            ss["%s_%s_df" % (prefix, low_cat)] = aps
            cc = {"action_point":
                  st.column_config.TextColumn(
                      "Action Point",
                      help="Action Point",
                      width="medium",
                      disabled=False,
                      required=True),
                  "username":
                  st.column_config.SelectboxColumn(
                      "Responsible",
                      help="Project member responsible for action point",
                      width="small",
                      options=team.username.to_list(),
                      disabled=False,
                      required=True,
                      ),
                  "progress":
                  st.column_config.SelectboxColumn(
                      "Progress",
                      options=list(range(0, 110, 10)),
                      help="Action point progress in percents",
                      width="small",
                      default=0),
                  "due_date":
                  st.column_config.DateColumn(
                      "Due date",
                      help="Action pooint due date",
                      width="small",
                      format="YYYY-MM-DD",
                      disabled=False,
                      required=True),
                  "comment":
                  st.column_config.TextColumn(
                      "Comment",
                      help="Comments to action point progress",
                      width="medium",
                      disabled=False,
                      required=False)}
            st.dataframe(aps,
                         column_order=['action_point',
                                       'username',
                                       'progress',
                                       'due_date',
                                       'comment'],
                         column_config=cc,
                         width='stretch',
                         hide_index=True,
                         key='%s_%s_aps' % (prefix, low_cat))


def show_action_points_table(project_data, expanded=False):

    text = "Targets and action points per %s:" % project_data.assessment_date

    # Extract the relevant subset of the project data.
    data = []
    data.append(['CRL',
                 project_data.crl,
                 project_data.crl_target,
                 project_data.crl_notes,
                 project_data.crl_target_lead,
                 project_data.crl_target_duedate])
    data.append(['TRL',
                 project_data.trl,
                 project_data.trl_target,
                 project_data.trl_notes,
                 project_data.trl_target_lead,
                 project_data.trl_target_duedate])
    data.append(['BRL',
                 project_data.brl,
                 project_data.brl_target,
                 project_data.brl_notes,
                 project_data.brl_target_lead,
                 project_data.brl_target_duedate])
    data.append(['IPRL',
                 project_data.iprl,
                 project_data.iprl_target,
                 project_data.iprl_notes,
                 project_data.iprl_target_lead,
                 project_data.iprl_target_duedate])
    data.append(['TMRL',
                 project_data.tmrl,
                 project_data.tmrl_target,
                 project_data.tmrl_notes,
                 project_data.tmrl_target_lead,
                 project_data.tmrl_target_duedate])
    data.append(['FRL',
                 project_data.frl,
                 project_data.frl_target,
                 project_data.frl_notes,
                 project_data.frl_target_lead,
                 project_data.frl_target_duedate])

    overview = pd.DataFrame(data,
                            columns=['',
                                     'Current',
                                     'Target',
                                     'Action Points',
                                     'Lead',
                                     'Due Date'])

    if expanded is None:

        st.subheader(text)
        st.markdown(HIDE_TABLE_ROW_INDEX, unsafe_allow_html=True)
        st.markdown(overview.
                    style.applymap(irl_color,
                                   subset=['Current', 'Target']).
                    to_html(),
                    unsafe_allow_html=True)

    else:

        action_points = st.expander(text, expanded=expanded)

        with action_points:

            st.markdown(HIDE_TABLE_ROW_INDEX, unsafe_allow_html=True)
            st.markdown(overview.
                        style.applymap(irl_color,
                                       subset=['Current', 'Target']).
                        to_html(),
                        unsafe_allow_html=True)


def show_progress(project_data0, project_data1, expanded=False):

    d0 = project_data0.assessment_date
    d1 = project_data1.assessment_date
    text = "Progress between %s and %s:" % (d0, d1)

    # Extract the relevant subset of the project data.
    data = []
    data.append(['CRL',
                 project_data0.crl,
                 project_data1.crl,
                 project_data0.crl_notes,
                 project_data0.crl_target_lead,
                 project_data0.crl_target_duedate])
    data.append(['TRL',
                 project_data0.trl,
                 project_data1.trl,
                 project_data0.trl_notes,
                 project_data0.trl_target_lead,
                 project_data0.trl_target_duedate])
    data.append(['BRL',
                 project_data0.brl,
                 project_data1.brl,
                 project_data0.brl_notes,
                 project_data0.brl_target_lead,
                 project_data0.brl_target_duedate])
    data.append(['IPRL',
                 project_data0.iprl,
                 project_data1.iprl,
                 project_data0.iprl_notes,
                 project_data0.iprl_target_lead,
                 project_data0.iprl_target_duedate])
    data.append(['TMRL',
                 project_data0.tmrl,
                 project_data1.tmrl,
                 project_data0.tmrl_notes,
                 project_data0.tmrl_target_lead,
                 project_data0.tmrl_target_duedate])
    data.append(['FRL',
                 project_data0.frl,
                 project_data1.frl,
                 project_data0.frl_notes,
                 project_data0.frl_target_lead,
                 project_data0.frl_target_duedate])

    progress = pd.DataFrame(data,
                            columns=['',
                                     'Previous',
                                     'Current',
                                     'Action Points',
                                     'Lead',
                                     'Due Date'])

    if expanded is None:

        st.subheader(text)
        st.markdown(HIDE_TABLE_ROW_INDEX, unsafe_allow_html=True)
        st.markdown(progress.style.applymap(irl_color,
                                            subset=['Previous',
                                                    'Current']).to_html(),
                    unsafe_allow_html=True)

    else:

        action_points = st.expander(text, expanded=expanded)

        with action_points:

            st.subheader(text)
            st.markdown(HIDE_TABLE_ROW_INDEX, unsafe_allow_html=True)
            st.markdown(progress.style.applymap(irl_color,
                                                subset=['Previous',
                                                        'Current']).to_html(),
                        unsafe_allow_html=True)


def add_user():

    # BUGFIX: Need to reset an enironmental variable after adding.
    # Can currently only add one user at the time.
    st.subheader("Add new user")
    btn_text = "Add new user"

    top = st.columns(4)
    btm = st.columns(4)
    status = ss.get("add_new_user_status", None)
    orgs = base.get_orgs()

    if status == 1:

        ss.new_name = ""
        ss.new_username = ""
        ss.new_pw1 = ""
        ss.new_pw2 = ""
        ss.new_user_org = None

    top[0].text_input("Name",
                      key="new_name",
                      help="The users actual, full name")
    top[1].text_input("Username",
                      key="new_username",
                      help="Unique user name - we recommend that you use\
                          the user's company e-mail address")
    top[2].text_input("New password", key='new_pw1', type='password')
    top[3].text_input("Repeat new password", key='new_pw2', type='password')

    btm[0].selectbox("Organisation", orgs, index=None, key='new_user_org')
    org = ss.get("new_user_org", None)

    if org is None:

        facs = []

    else:

        facs = base.get_facs(org)

    btm[1].selectbox("Faculty", facs, index=None, key='new_user_fac')
    fac = ss.get("new_user_fac", None)

    if fac is None:

        deps = []

    else:

        deps = base.get_deps(fac)

    btm[2].selectbox("Department", deps, index=None, key='new_user_dep')
    btm[3].selectbox("Permission level",
                     base.get_permission_levels(),
                     index=1,
                     key="new_permissions")

    st.button(btn_text, on_click=on_add_new_user)

    if status == 0:

        st.error("Passwords don't match!")

    elif status == 1:

        st.success("New user successfully added!")
        time.sleep(2)
        status = ss.add_new_user_status = None
        st.rerun()

    elif status == 2:

        st.error("User already exists!")


def init_system():

    btn_text = "Initialise system and get started!"
    sys_settings = base.get_system_settings()

    top = st.columns(4)
    mdl = st.columns(4)
    st.markdown("This part relates to the logos.  \n\
                The logo is displayed in the top left corner (where it now\
                says 'NTNU | Technology Transfer as'), and you should provide\
                one  for both dark mode and ligth mode.  \n\
                It is highly recommended that you use SVG files for this,\
                and due to the way Streamlit is currenlty set up these SVG\
                fieles need to be stored on an external server.  \n\
                You can also add an URL to redirect the user to when the logo\
                is clicked.")
    btm = st.columns(3)
    status = ss.get("add_new_user_status", None)

    if status == 1:

        ss.new_name = ""
        ss.new_username = ""
        ss.new_pw1 = ""
        ss.new_pw2 = ""
        ss.new_user_org = None

    top[0].text_input("Name",
                      key="new_name",
                      help="The users actual, full name")
    top[1].text_input("Username",
                      key="new_username",
                      help="Unique user name - we recommend that you use\
                          the user's company e-mail address")
    top[2].text_input("New password", key='new_pw1', type='password')
    top[3].text_input("Repeat new password", key='new_pw2', type='password')

    mdl[0].text_input("Organisation name", key="new_user_org")
    mdl[1].text_input("Faculty (Optional)", key="new_user_fac")
    mdl[2].text_input("Department (Optional)", key="new_user_dep")
    mdl[3].selectbox("Permission Level",
                     [base.get_permission_levels()[-1]],
                     index=0,
                     key="new_permissions")

    btm[0].text_input("Logo web page link",
                      key='logo_uri',
                      value=sys_settings.logo_uri)
    btm[1].text_input("Dark mode logo URI",
                      key="logo_uri_dark",
                      value=sys_settings.logo_uri_dark)
    btm[2].text_input("Light mode logo URI",
                      key="logo_uri_light",
                      value=sys_settings.logo_uri_light)

    st.button(btn_text, on_click=on_init_system)

    if status == 0:

        st.error("User passwords don't match!")

    elif status == 1:

        st.success("System successfully initialized!")


def change_password(user, admin=False):

    with st.form("change_password", border=False):

        if admin:

            st.subheader("Change user password")
            cols = st.columns(4)

            with cols[-4]:

                username = st.text_input("Username", key='username')

            with cols[-3]:

                pw0 = st.text_input("Admin password",
                                    key='admin_pw',
                                    type='password')

        else:

            st.subheader("Change password")
            cols = st.columns(3)

            with cols[-3]:

                pw0 = st.text_input("Old password",
                                    key="old_pw",
                                    type="password")

        with cols[-2]:

            pw1 = st.text_input("New password",
                                key="ch_pw1",
                                type="password")

        with cols[-1]:
            pw2 = st.text_input("Repeat new password",
                                key="ch_pw2",
                                type="password")

        change_pw = st.form_submit_button("Change password")

        if change_pw:

            if pw1 == pw2:

                # Check that old password is correct if not admin.
                verified = base.validate_user(user.username, pw0)

                if verified:

                    if user.rights == 9:

                        pw_user = base.get_user(username)
                        success = base.change_user_password(pw_user, pw1)

                    else:

                        success = base.change_user_password(user, pw1)

                    if success:

                        st.success("Password successfully changed!")

                    else:

                        st.error("Unknown error changing password!")

                else:

                    st.error("Old password incorrect!")

            else:

                st.error("New passwords don't match!")


def change_user_rights():

    st.subheader("Change user rights")
    cols = st.columns(3)

    with cols[0]:

        active_users = base.get_users()
        st.selectbox("Select user to change permission level for",
                     active_users,
                     placeholder="Select user",
                     key="change_user_rights")

    old_user = ss.get("change_user_rights", None)

    if old_user is None:

        rights = 0

    else:

        rights = old_user.rights

    p_levels = base.get_permission_levels()
    p_index = [p_level.level for p_level in p_levels]
    index = p_index.index(rights)

    with cols[1]:

        st.selectbox("Old permission level",
                     p_levels,
                     index=index,
                     disabled=True,
                     key="old_permission_level")

    with cols[2]:

        st.selectbox("New permission level",
                     p_levels,
                     index=index,
                     key="new_permission_level")

    change_user_rights = st.button("Update user permissions")

    if change_user_rights:

        old_user = ss.get("change_user_rights", None)
        rights = ss.get("new_permission_level", None)

        if old_user is not None and rights is not None:

            success = base.change_user_rights(old_user, rights)

            if success:

                st.success("User permission changed!")

            else:

                st.error("Could not change user permissions!")

        with st.spinner("Updating database..."):

            time.sleep(1)

        st.rerun()


def change_user_status():

    with st.form("change_user_status", border=False):

        de, re = st.columns(2)

        with de:

            st.subheader("Deactivate user(s):")
            active_users = base.get_users()
            active_users = [user.username for user in active_users]
            st.multiselect("Select users to deactivate",
                           active_users,
                           placeholder="Select users",
                           key="deactivate_users")

        with re:

            st.subheader("Reactivate user(s):")
            inactive_users = base.get_users(False)
            inactive_users = [user.username for user in inactive_users]
            st.multiselect("Select users to reactivate",
                           inactive_users,
                           placeholder="Select users",
                           key="reactivate_users")

        change_user_status = st.form_submit_button("Update user status")

        if change_user_status:

            des, res = st.columns(2)

            if len(ss.deactivate_users) > 0:

                success = base.change_user_status(
                    ss.deactivate_users,
                    False)

                with des:

                    if success:

                        st.success("Selected user(s) detctivated!")

                    else:

                        st.error("Could not deactivate user(s)!")

            if len(ss.reactivate_users) > 0:

                success = base.change_user_status(
                    ss.reactivate_users,
                    True)

                with res:

                    if success:

                        st.success("Selected user(s) reactivated!")

                    else:

                        st.error("Could not reactivate user(s)!")

            with st.spinner("Updating database..."):

                time.sleep(1)

            st.rerun()


def add_organisation(callback):

    st.subheader("Add new organisation")
    org_c, fac_c = st.columns(2)
    status = ss.get("add_new_org_status", None)

    with org_c:

        if status == 1:

            ss.new_org = None

        st.text_input("Organisation", key='new_org')

    with fac_c:

        st.text_area("Faculties (optional)",
                     key='new_fac',
                     help="Will add one faculty per line")

    st.button("Add new organisation",
              key="btn_add_org",
              on_click=callback)


def add_faculties(callback):

    st.subheader("Add new faculties")
    org_c, fac_c = st.columns(2)

    with org_c:

        st.selectbox("Organisation",
                     options=base.get_orgs(),
                     key='select_orgs')

    with fac_c:

        st.text_area("Faculties",
                     key="new_facs",
                     help="Will add one faculty per line")

    st.button("Add new faculties",
              key="btn_add_fac",
              on_click=callback)


def add_departments(callback):

    st.subheader("Add new departments")
    org_c, fac_c, dep_c = st.columns(3)

    with org_c:

        st.selectbox("Organisation",
                     options=base.get_orgs(),
                     key='select_org')

    with fac_c:

        org = ss.select_org
        disabled = True

        if org is not None:

            faculties = base.get_facs(org)
            disabled = False

        st.selectbox("Faculty",
                     options=faculties,
                     key="select_fac",
                     disabled=disabled)

    with dep_c:

        st.text_area("Departments",
                     key="new_deps",
                     help="Will add one deparatment per line")

    st.button("Add new departments",
              key="btn_add_dep",
              on_click=callback)


def irl_explainer():
    ascending = True

    if ss.get("user_settings", None) is not None:

        ascending = ss.user_settings.ascending_irl

    crl_t, trl_t, brl_t, iprl_t, tmrl_t, frl_t = st.tabs(['CRL',
                                                          'TRL',
                                                          'BRL',
                                                          'IPRL',
                                                          'TMRL',
                                                          'FRL'])

    # CSS to inject contained in a string
    hide_table_row_index = """
                <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
                </style>
                """

    with crl_t:

        crl_h, crl_s, crl_ds = st.tabs(["Overview", "Scale", "Aspects"])
        crl_df = base.get_irl_table('CRL', ascending)

        with crl_h:

            st.header("Customer Readiness Level – CRL")
            st.markdown("CRL focus on getting your “solution” out into the market so that it is being used and creates value.")
            st.markdown("The CRL scale is divided in two main stages:")
            st.markdown("* CRL 1-4: Understanding your customers/users.\n* CRL 5-9: Getting your “solution” in the hands of the customer/user and trying to sell it.")
            st.markdown("In business models where the users don’t have to pay for the product/service, the CRL focusses on the user and not the paying customer (hence use the criteria in CRL 6-9 about “users” and “active users”). In these cases the paying customer and the payment willingness is covered in the BRL scale.")

        with crl_s:

            crl_sdesc = crl_df[['Level', 'Description']]
            st.markdown(hide_table_row_index,
                        unsafe_allow_html=True)
            st.markdown(crl_sdesc.style.applymap(irl_color,
                                                 subset=['Level']).
                        to_html(escape=False),
                        unsafe_allow_html=True)

        with crl_ds:

            crl_desc = crl_df[['Level', 'Aspects']]
            st.markdown(hide_table_row_index,
                        unsafe_allow_html=True)
            st.markdown(crl_desc.style.applymap(irl_color,
                                                subset=['Level']).
                        to_html(escape=False),
                        unsafe_allow_html=True)

    with trl_t:

        trl_h, trl_s, trl_ds = st.tabs(["Overview", "Scale", "Aspects"])
        trl_df = base.get_irl_table('TRL', ascending)

        with trl_h:

            st.header("Technology Readiness Level – TRL")
            st.markdown("TRL focus on the functionality of the “technology” (se comment below) and that it is “fit for purpose”.")
            st.markdown("We are using the TRL scale originally developed by NASA with some small modifications to make it easier to understand and apply to different types of ideas. In particular, we have tried to add explanations to key words and concepts in the definitions of the levels in the scale.")
            st.markdown("We use the word “Technology” to stick to the terminology of the original TRL scale, but the word should be interpreted as the “solution” you want to develop regardless if it is strictly speaking a technology or not.")
            st.markdown("It can sometimes be difficult to differentiate between the steps in middle part of the TRL scale – TRL 4, 5, 6, 7. Some typical differentiating factors to consider could be:\n * Size or form factor\n* Level of integration of subcomponents\n* “Finish” of the prototype – closeness to appearance of final product\n * Level of reality in the “relevant environment”\n* Development phase of the technology and/or components\n* Etc.")

        with trl_s:

            trl_sdesc = trl_df[['Level', 'Description']]
            st.markdown(hide_table_row_index,
                        unsafe_allow_html=True)
            st.markdown(trl_sdesc.style.applymap(irl_color,
                                                 subset=['Level']).
                        to_html(escape=False),
                        unsafe_allow_html=True)

        with trl_ds:

            trl_desc = trl_df[['Level', 'Aspects']]
            st.markdown(hide_table_row_index,
                        unsafe_allow_html=True)
            st.markdown(trl_desc.style.applymap(irl_color,
                                                subset=['Level']).
                        to_html(escape=False),
                        unsafe_allow_html=True)

    with brl_t:

        brl_h, brl_s, brl_ds = st.tabs(["Overview", "Scale", "Aspects"])
        brl_df = base.get_irl_table('BRL', ascending)

        with brl_h:

            st.header("Business Model Readiness Level – BRL")
            st.markdown("BRL focus on creating a viable and sustainable business model around the idea. The business model can be commercial or non-commercial and for profit or non-profit.")
            st.markdown("In this Readiness Level, we use the following key definitions:\n* ”Business Model” = “A business model describes how an organization creates, delivers, and captures value”. This can be described in several different formats, e.g. a Business Model Canvas, but also many other ways.\n * “Sustainable Business Model” = A business model where the Revenue ≥ Cost (over time) AND Positive contribution to environment and society > Negative contribution to environment and society (over time).")
            st.markdown("We believe that going forward from now, you cannot have an economically viable business model over time without taking responsibility for your contribution to environmental and social sustainability as well.")
            st.markdown("The BRL scale is divided in three main stages:\n* BRL 1-3: Describe your sustainable business model in increasing level of detail.\n* BRL 4-6: Simulate/calculate if the sustainable business model is viable based on hypotheses, assumptions, and feedback.\n* BRL 7-9: Test the sustainable business model in reality and confirm that it is viable.")
            st.markdown("The term “_Key measures to increase positive and decrease negative environmental and social contribution_” in BRL 5 refers to the most important things you actively do to increase positive and decrease negative contribution. Examples could be choosing a bio based material instead of a fossil fuel based material, only working with suppliers with some relevant certification, paying workers better salaries, taking responsibility for recycling of you product, etc. The point is to verify that the business model is both practically feasible and economically viable when you take these measures into account.")

        with brl_s:

            brl_sdesc = brl_df[['Level', 'Description']]
            st.markdown(hide_table_row_index,
                        unsafe_allow_html=True)
            st.markdown(brl_sdesc.style.applymap(irl_color,
                                                 subset=['Level']).
                        to_html(escape=False),
                        unsafe_allow_html=True)

        with brl_ds:

            brl_desc = brl_df[['Level', 'Aspects']]
            st.markdown(hide_table_row_index,
                        unsafe_allow_html=True)
            st.markdown(brl_desc.style.applymap(irl_color,
                                                subset=['Level']).
                        to_html(escape=False),
                        unsafe_allow_html=True)

    with iprl_t:

        iprl_h, iprl_s, iprl_ds = st.tabs(["Overview", "Scale", "Aspects"])
        iprl_df = base.get_irl_table('IPRL', ascending)

        with iprl_h:

            st.header("IPR Readiness Level – IPRL")
            st.markdown("IPRL focusses on controlling and using Intellectual Property Rights to increase the likelihood of successfully taking the idea to the market and creating value.")
            st.markdown("It is very important to remember that all new ideas are based on, and contains, some sort of IPR, so IPRL is relevant for all types of ideas.")
            st.markdown("The IPRL scale is divided in two main stages:\n* IPRL 1-4: Identifying, describing, and assessing the potential to protect your IPR.\n* IPRL 5-9: Taking active steps to protect and control your IPR according to a thought through strategy.")
            st.markdown("When you have identified and defined the specific IPR in each particular project/idea, it is much easier to understand and interpret the criteria on all the higher levels of the IPRL scale.")

        with iprl_s:

            iprl_sdesc = iprl_df[['Level', 'Description']]
            st.markdown(hide_table_row_index,
                        unsafe_allow_html=True)
            st.markdown(iprl_sdesc.style.applymap(irl_color,
                                                  subset=['Level']).
                        to_html(escape=False),
                        unsafe_allow_html=True)

        with iprl_ds:

            iprl_desc = iprl_df[['Level', 'Aspects']]
            st.markdown(hide_table_row_index,
                        unsafe_allow_html=True)
            st.markdown(iprl_desc.style.applymap(irl_color,
                                                 subset=['Level']).
                        to_html(escape=False),
                        unsafe_allow_html=True)

    with tmrl_t:

        tmrl_h, tmrl_s, tmrl_ds = st.tabs(["Overview", "Scale", "Aspects"])
        tmrl_df = base.get_irl_table('TMRL', ascending)

        with tmrl_h:

            st.header("Team Readiness Level – TMRL")
            st.markdown("TMRL focus on getting the right people together to go from idea to market and to make sure they have the best possibilities to perform well.")
            st.markdown("The TMRL scale primarily deals with:\n* Competencies – that there is the right knowledge, skills, experience, etc. at each stage of the idea development.\n* Capacity – that there is enough work capacity of people with the right competencies to do the work necessary at each stage of the idea development.\n* Team alignment – that the people in the team are sitting in the same boat and rowing in the same direction.")
            st.markdown("Competencies and capacity can be added by e.g. recruitment, training, consultants, partners, etc.")
            st.markdown("The term “diversity” should be understood to encompass gender, culture, age, background, and other relevant factors. An ample body of research shows that when you are taking new ideas to the market (i.e. creating innovations), diverse teams perform better.")
            st.markdown("The TMRL scale is divided in two main stages:\n* TMRL 1-4: The initial team to verify and develop the potential of the idea.\n* TMRL 5-9: The team to build a startup/organisation to realize the idea and take it to the market, where:\n\t- TMRL 5-6: putting the founding team in place to start building the startup, and\n\t- TMRL 7-9: building and scaling the organisation.")
            st.markdown("The word “startup” typically refers to a commercial independent company, but it can also be non-commercial entities or other types of organisations. The point is that you want to build a team and an organisation to develop the idea and take it to the market (or at least closer to the market), and not primarily transfer the idea to another party (e.g. existing business/organisation) that develops it and takes it to the market.")
            st.markdown("It is not necessarily the same persons validating the idea (TMRL 1-4) and building a startup (TMRL 5-9).")

        with tmrl_s:

            tmrl_sdesc = tmrl_df[['Level', 'Description']]
            st.markdown(hide_table_row_index,
                        unsafe_allow_html=True)
            st.markdown(tmrl_sdesc.style.applymap(irl_color,
                                                  subset=['Level']).
                        to_html(escape=False),
                        unsafe_allow_html=True)

        with tmrl_ds:

            tmrl_desc = tmrl_df[['Level', 'Aspects']]
            st.markdown(hide_table_row_index,
                        unsafe_allow_html=True)
            st.markdown(tmrl_desc.style.applymap(irl_color,
                                                 subset=['Level']).
                        to_html(escape=False),
                        unsafe_allow_html=True)

    with frl_t:

        frl_h, frl_s, frl_ds = st.tabs(["Overview", "Scale", "Aspects"])
        frl_df = base.get_irl_table('FRL', ascending)

        with frl_h:

            st.header("Funding Readiness Level – FRL")
            st.markdown("FRL focus on securing enough funding to develop the idea and to reach an economically viable and sustainable business model for the idea over time.")
            st.markdown("The FRL is based on two core assumptions:\n* Successful innovation (taking new ideas to the market) depends on finding a viable and sustainable business model for the idea so that it can create value and impact over time on the market.\n* New ideas always require input in the form of people’s time, money, and other resources to be developed before they can be sold or generate revenue/value in other ways, so there will always be a need for some sort of funding to cover the resource need before you reach a viable business model.")
            st.markdown("There are many different possible sources of funding – e.g., internal funding from yourself or your organisation; external funding from investors, banks, funding agencies, etc.; customer funding from sales, pre-sales, joint development, etc.; and so on.")
            st.markdown("The FRL scale primarily deals with:\n* What are you funding? – the idea/concept/project/business/activities you need funding for\n* How much funding do you need?\n* How much funding have you secured?")
            st.markdown("The FRL scale is divided in two main stages:\n* FRL 1-4: Primary focus on funding to verify and develop the potential of the idea so that you can identify a viable business model.\n* FRL 5-9: Primary focus on being able to realise the business model and reach economic viability and sustainability over time.")
            st.markdown("From FRL 5 and upwards there is a lot of focus on funding from external sources. In cases where external funding is not the chosen strategy, you can ignore the criteria that specifically relate to external funding (pitches for funding, discussions with investors, etc.), but still use the criteria that relate to keeping track of your funding need (budget, accounting, financial forecasting, etc.)")

        with frl_s:

            frl_sdesc = frl_df[['Level', 'Description']]
            st.markdown(hide_table_row_index,
                        unsafe_allow_html=True)
            st.markdown(frl_sdesc.style.applymap(irl_color,
                                                 subset=['Level']).
                        to_html(escape=False),
                        unsafe_allow_html=True)

        with frl_ds:

            frl_desc = frl_df[['Level', 'Aspects']]
            st.markdown(hide_table_row_index,
                        unsafe_allow_html=True)
            st.markdown(frl_desc.style.applymap(irl_color,
                                                subset=['Level']).
                        to_html(escape=False),
                        unsafe_allow_html=True)


def display_valuation(project):

    exp = st.expander("Show rudimentary valuation")
    sup_val = project.calc_startup_value()
    sup_t_val = project.calc_startup_target_value()
    lic_val = project.calc_license_value()
    lic_t_val = project.calc_license_target_value()

    with exp:

        txt = f"Startup value NOW: {sup_val:,}  \n"
        txt += f"Startup value IF targets are met: {sup_t_val:,}  \n\n"
        txt += f"License value NOW: {lic_val:,}  \n"
        txt += f"License value IF targets are met: {lic_t_val:,}"
        st.markdown(txt)


def add_new_project(users, handler):

    status = ss.get("add_new_project_status", None)
    st.subheader("Add new project")
    c1, c2, c3, c4 = st.columns(4)

    if status == 1:

        ss.new_project_no = ""
        ss.new_project_name = ""
        ss.new_project_members = []
        ss.new_project_leader = None
        ss.new_project_description = ""

    c1.text_input("Project Number",
                  key='new_project_no')
    c2.text_input("Project Name",
                  key='new_project_name')
    c3.multiselect("Project members",
                   users,
                   key="new_project_members")
    c4.selectbox("Project Leader",
                 ss.new_project_members,
                 index=None,
                 key='new_project_leader')
    st.text_area("Project description", 
                 key='new_project_description')

    if status == 2:

        st.error("Project number must be set and must be a number!")

    if status == 3:

        st.error("Project name must be set!")

    if status == 4:

        st.error("You must select at least one project member!")

    if status == 5:

        st.error("You must select a project leader!")

    if status == 6:

        st.error("Project already exists!")

    if status == 1:

        st.success("Project successfully added!")
        time.sleep(2)
        ss.add_new_project_status = None
        st.rerun()

    st.button("Add new project", on_click=handler)


def edit_project_team(users, edit_cb, team_change_cb):

    user = ss.user
    pte_cols = st.columns(3)
    pte_cols[0].selectbox("Select project",
                          options=ss.projects,
                          key="project_team_to_edit",
                          on_change=edit_cb)
    project = ss.get("project_team_to_edit", None)

    if project is not None:

        if ss.get('team_df', None) is None:

            ss.team_df = base.get_project_team(project.project_no, False)

        team = ss.team_df
        all_perms = base.get_permission_levels()
        perm_map = {perm.level: perm.level_text for perm in all_perms}
        project_perms = team.project_rights.to_list()
        project_perms = [perm_map[pp] for pp in project_perms]
        team["access_level"] = project_perms
        non_members = []
        team_sans_lead = []
        members = team.user_id.to_list()
        active_members = team['user_id'].\
            where(team['active'] == 1).to_list()

        # TODO: Should probably be a query. Doesn't scale well.
        for u in users:

            if u.user_id not in members:

                non_members.append(u)

            else:

                if (u.user_id in active_members and
                   u.user_id != project.project_leader_id):

                    team_sans_lead.append(u)

        pte_cols[1].multiselect("Add project members",
                                non_members,
                                key="add_new_project_members")
        pte_cols[2].selectbox("Change project leader",
                              options=team_sans_lead,
                              index=None,
                              key="change_project_leader")
        allowed_perms = base.get_permission_levels(user)
        allowed_perms = [perm.level_text for perm in allowed_perms if
                         user.rights >= perm.level]

        with st.form("update_team_data_editor", border=False):

            st.data_editor(team,
                           column_order=['actual_name',
                                         'username',
                                         'access_level',
                                         'active'],
                           column_config={
                               "actual_name": st.column_config.TextColumn(
                                   "Name",
                                   help="Project member name",
                                   width="medium",
                                   disabled=True,
                                   required=True),
                               "username": st.column_config.TextColumn(
                                   "Username",
                                   help="Project member username",
                                   width="medium",
                                   disabled=True,
                                   required=True),
                               "access_level": st.column_config.SelectboxColumn(
                                   "Access Level",
                                   help="Project member access level",
                                   width="medium",
                                   options=allowed_perms,
                                   disabled=False,
                                   required=True,
                                   ),
                               "active": st.column_config.CheckboxColumn(
                                   "Active",
                                   help="Disable/enable project access",
                                   width="small",
                                   disabled=False,
                                   required=True,
                                   ),
                               },
                           width='stretch',
                           hide_index=True,
                           key="project_team_editor")
            submit = st.form_submit_button("Apply project team changes")

            if submit:

                errors = team_change_cb()

                if errors is None:

                    st.success("Project team changes successfully saved!")

                    with st.spinner("Updating database..."):

                        time.sleep(1)

                else:

                    st.error(errors)
                    time.sleep(1)

                st.rerun()


def change_project_status(user):

    st.subheader("Change project status")
    with st.form("change_project_status", border=False):

        de, re = st.columns(2)
        filt = ss.user_settings.filter_on_user

        with de:

            active_projs = base.get_projects(user, filt, True)
            st.multiselect("Select projects to deactivate",
                           active_projs,
                           placeholder="Select projects",
                           key="deactivate_projects")

        with re:

            inactive_projs = base.get_projects(user, filt, False)
            st.multiselect("Select projects to reactivate",
                           inactive_projs,
                           placeholder="Select projects",
                           key="reactivate_projects")

        change_proj_status = st.form_submit_button("Update project status")

        if change_proj_status:

            des, res = st.columns(2)

            if len(ss.deactivate_projects) > 0:

                success = base.change_project_status(
                    ss.deactivate_projects,
                    False)

                with des:

                    if success:

                        st.success("Selected project(s) detctivated!")

                    else:

                        st.error("Could not deactivate project(s)!")

            if len(ss.reactivate_projects) > 0:

                success = base.change_project_status(
                    ss.reactivate_projects,
                    True)

                with res:

                    if success:

                        st.success("Selected project(s) reactivated!")

                    else:

                        st.error("Could not reactivate project(s)!")

            with st.spinner("Updating database..."):

                time.sleep(1)

            st.rerun()


def user_settings(user_settings, handler):

    with st.form("change_user_settings", border=False):

        st.checkbox("Smooth IRL levels",
                    value=user_settings.smooth_irl,
                    key='smooth_irl',
                    help="When selected, smooths the curves between the\
                          diffrent IRL values to give what some people\
                          including the author thinks is more esthetically\
                          pleasing look")
        st.checkbox("Show only projects where I am project leader",
                    value=user_settings.filter_on_user,
                    key='filter_on_user',
                    help="When selected, only projects where you are\
                          the project leader will be visible in the user\
                          interface. When not selected, all projects\
                          where you are a part of the project team\
                          will be visible.")
        st.checkbox("Remember current project on next login",
                    value=user_settings.remember_project,
                    key='remember_project',
                    help="When selected, Really Nice IRL will remember the\
                          current project upon the next login.")
        st.checkbox("Display IRL in ascending order",
                    value=user_settings.ascending_irl,
                    key='ascending_irl',
                    help="When selected, will display IRL scales and aspects\
                          in ascending (1-9) order, when deselected IRL \
                          scales will be displayed in descending (9-1) order ")
        st.checkbox("Table view for action points in Portfolio View",
                    value=user_settings.ap_table_view,
                    key='ap_table_view',
                    help="When selected, will display a table view of\
                          targets, action points and lead instead of\
                          a read-only version of the input widget\
                          in portfolio mode")
        change_us_status = st.form_submit_button("Apply user settings")

        if change_us_status:

            success = handler()

            if success:

                st.success("User settings updated!")

                with st.spinner("Updating database..."):

                    time.sleep(1)

            else:

                st.error("Could not update user settings!")
                time.sleep(1)

            st.rerun()

