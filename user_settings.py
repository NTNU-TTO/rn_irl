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
from streamlit import session_state as ss

import base
import ui


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


if ss.get("pm_map", None) is None:

    ss.pm_map = base.get_permission_level_map()

user_settings = ss['user_settings']
user = ss.user

# The user settings.
ui.user_settings(user_settings, on_save_user_settings)
st.divider()
ui.change_password(user)
