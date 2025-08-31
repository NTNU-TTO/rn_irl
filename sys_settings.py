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
    settings.noreply_address = ss.noreply_address
    settings.noreply_body = ss.noreply_body
    settings.show_valuations = int(ss.show_valuations)
    settings.update()
    edited_rows = ss.startup_value_matrix['edited_rows']
    base.update_startup_values(edited_rows)
    edited_rows = ss.license_value_matrix['edited_rows']
    base.update_license_values(edited_rows)


#
# The actual UI.
#
dark_mode = (st.context.theme.type == 'dark')
ui.add_logo(dark_mode)

sys_settings = base.get_system_settings()
cols1 = st.columns(3)
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

cols3 = st.columns(2, vertical_alignment="top")
cols3[0].text_input("noreply e-mail to use when e-mailing new users",
                    key="noreply_address",
                    value=sys_settings.noreply_address)
cols3[1].text_area("Welcome text to use in e-mail to new users",
                   key="noreply_body",
                   value=sys_settings.noreply_body)
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
