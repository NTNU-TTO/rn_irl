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

import base
import streamlit as st
import ui
import utils

from streamlit import session_state as ss


def onLogout():
    """
    Clear all previous user states and settings.

    Returns
    -------
    None.

    """

    ss.status = 'unverified'
    ss.user = None
    ss.username = None
    ss.user_settings = None
    ss.project = None
    ss.projects = None
    ss.project_history = None
    ss.progress_r0 = None
    ss.progress_r1 = None
    ss.revision_index = None
    ss.revision_index0 = None
    ss.revision_index1 = None
    ss.revision_r = None
    ss.projects = None
    ss.add_new_user_status = None
    ss.refresh = True


def onSetPassword():

    if ss.pw1 != ss.pw2:

        ss.status = "no_match"

    else:

        username = ss.username
        user = base.get_user(username)
        base.change_user_password(user, ss.pw1)


def checkPwd():

    username = ss.username
    password = ss.password
    user = base.validate_user(username, password)
    ss.password = None

    if user is None:

        ss.status = 'incorrect'

    else:

        ss.status = 'verified'
        ss.user = user
        ss.user_settings = base.get_user_settings(user.user_id)
        ss.dark_mode = (st.context.theme.type == 'dark')
        ss.projects = base.get_projects(user, ss.user_settings.filter_on_user)
        ss.refresh = False

    # Safety measures.
    del ss['username']
    del ss['password']


def login_view():

    ss.status = ss.get("status", "unverified")
    dark_mode = (st.context.theme.type == 'dark')

    img, hl = st.columns([1, 20])

    with img:

        if dark_mode:

            st.image("static/really_nice_logo.png", width=66)

        else:

            st.image("static/really_nice_logo_inv.png", width=66)

    with hl:

        st.header("Really Nice IRL Login")

    if ss.status != 'verified':

        st.text_input("Username:",
                      key="username")
        username = ss.get("username", None)
        go_ahead = True

        if username != "":

            exists = base.is_user(username)

            if exists:

                has_pw = base.has_password(username)

                if not has_pw:

                    go_ahead = False
                    welcome_str = "Looks like you are logging in for the \
                    first time! I've generated a random password for you \
                    and forwarded it to your e-mail address. Please check \
                    your inbox and spam folder. I recommend that you change \
                    the automagically generated password when you log in."
                    st.write(welcome_str)
                    user = base.get_user(username)
                    pw = utils.gen_pw()
                    success = base.change_user_password(user, pw)
                    se = utils.sendmail(username, pw)

                    if success and se:

                        st.success("Password set and e-mail sent!")

        if go_ahead:

            st.text_input("Password:",
                          key="password",
                          type='password',
                          on_change=checkPwd)

        if ss.status == 'unverified':

            st.warning("Please provide username and password to log in.")

        elif ss.status == 'incorrect':

            st.error("Wrong username or password!")

    if ss.status == 'verified':

        go_to_page = ss.get('go_to_page', None)

        if go_to_page is None:

            st.success("Logged in as " + ss.user.username)
            st.button("Log out", on_click=onLogout)
            ss.system_settings = base.get_system_settings()

        else:

            ss['go_to_page'] = None
            st.switch_page(go_to_page)


# Currently no sensible way to get theme information.
# We assume dark as this is default until otherwise is proven by user.
dark_mode = (st.context.theme.type == 'dark')

ui.add_logo(dark_mode)

owner_org_id = base.get_system_settings().owner_org_id

if owner_org_id is None:

    st.subheader("It looks like you're running Really Nice IRL for the\
                 very first time.")
    st.write("Don't worry, I will help you set things up.  \n\
             We just need to create an administrator and an owner\
             organisation and we're good to go!")
    ui.init_system()

else:

    login_view()
