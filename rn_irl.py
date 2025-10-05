# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 12:36:46 2024

@author: Lodve
"""
import streamlit as st

import base
import ui

from streamlit import session_state as ss

admin_tools_pg = st.Page("admin_tools.py",
                         title="Admin Tools",
                         icon=":material/admin_panel_settings:")
intro_pg = st.Page("Introduction.py",
                   title="Introduction to KTH IRL",
                   icon=":material/info:")
irl_ass_pg = st.Page("IRL_Assessment.py",
                     title="Project Assessment",
                     icon=":material/analytics:")
login_pg = st.Page("Login.py",
                   title="Login",
                   icon=":material/login:")
logout_pg = st.Page("Login.py",
                    title="Logout",
                    icon=":material/login:")
port_pg = st.Page("Project_Portfolio.py",
                  title="Project Portfolio",
                  icon=":material/database:")
project_tools_pg = st.Page("project_tools.py",
                           title="Project Tools",
                           icon=":material/construction:")
reporting_pg = st.Page("reporting.py",
                       title="Reports",
                       icon=":material/lab_profile:")
sys_settings_pg = st.Page("sys_settings.py",
                          title="System Settings",
                          icon=":material/settings:")
user_settings_pg = st.Page("user_settings.py",
                           title="User Settings",
                           icon=":material/manage_accounts:")



def get_tools_n_settings(user):

    if user.rights < 2:

        return [user_settings_pg]

    elif user.rights == 2:

        return [project_tools_pg, reporting_pg, user_settings_pg]
    
    elif user.rights == 6:

        return [user_settings_pg]

    elif user.rights == 7:

        return [user_settings_pg]
  
    elif user.rights == 8:

        return [project_tools_pg, reporting_pg, user_settings_pg]
  
    elif user.rights == 9:

        return [project_tools_pg,
                reporting_pg,
                admin_tools_pg,
                user_settings_pg,
                sys_settings_pg]


owner_org_id = base.get_system_settings().owner_org_id

if owner_org_id is None:

    st.subheader("It looks like you're running Really Nice IRL for the\
                 very first time.")
    st.write("Don't worry, I will help you set things up.  \n\
             We just need to create an administrator and an owner\
             organisation and we're good to go!")
    ui.init_system()

else:

    ss.status = ss.get("status", "unverified")

    if ss.status != 'verified':

        pg = st.navigation(
            {
             "Account": [login_pg],
             "About": [intro_pg]
             }
            )

    else:

        user = ss.user
        pg = st.navigation(
            {
             "Account": [logout_pg],
             "Projects": [irl_ass_pg, port_pg],
             "Tools & Settings": get_tools_n_settings(user),
             "About": [intro_pg]
             }
            )

    ui.setup_page()
    pg.run()
