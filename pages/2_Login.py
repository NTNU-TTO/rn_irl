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
import ui
import streamlit as st

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
        ss.dark_mode = ss.user_settings.dark_mode
        ss.projects = base.get_projects(user.user_id)
        ss.refresh = False

    # Safety measures.
    del ss['username']
    del ss['password']


def login_view():

    ss.status = ss.get("status", "unverified")

    if ss.get('user_settings', None) is None:

        dark_mode = True

    else:

        dark_mode = ss.user_settings.dark_mode

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

        else:

            ss['go_to_page'] = None
            st.switch_page(go_to_page)


def main():

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


if __name__ == '__main__':

    # Set up page style.
    ui.setup_page()
    # Currently no sensible way to get theme information.
    # We assume dark as this is default until otherwise is proven by user.
    if ss.get('user_settings', None) is None:

        dark_mode = True

    else:

        dark_mode = ss.user_settings.dark_mode

    ui.add_logo(dark_mode)

    main()
