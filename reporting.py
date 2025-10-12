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
import data_viz
import ui
import report_engine

from streamlit import session_state as ss

# Currently no sensible way to get theme information.
# We assume dark as this is default until otherwise is proven by user.
dark_mode = (st.context.theme.type == 'dark')

ui.add_logo(dark_mode)

st.header("Really Nice Reporting")
help_text = "Welcome to the Really Nice Reporting Interface!  \n  \n"
help_text += "Please select a pre-defined report to generate below.  \n"
help_text += "Note that due to limitations within the Streamlit framework, "
help_text += "reports will be downloaded to your web browser's default download "
help_text += "directory.  \nThere is unfortunately currently no way to specify "
help_text += "any other folder to download to."
st.markdown(help_text)
user = ss.user
filt = ss.user_settings.filter_on_user

rep, proj = st.columns(2)

with rep:

    st.selectbox("Select Report",
                 options=report_engine.AVAILABLE_REPORTS.keys(),
                 key="selected_report")

portfolio = report_engine.AVAILABLE_REPORTS[ss.selected_report][1]
   
with proj:

    if portfolio:
        
        st.multiselect("Select Project(s)",
                       options=ss.projects,
                       key="selected_rep_projects")
    else:
        
        st.selectbox("Select Project",
                     options=ss.projects,
                     key="selected_rep_project")

if portfolio:

    with report_engine.AVAILABLE_REPORTS[ss.selected_report][0](ss.selected_rep_projects) as pdf_buffer:
        st.download_button(
            label="Save portfolio report to Downloads folder",
            data=pdf_buffer,
            file_name=f"Portfolio_report.pdf",
            mime="application/pdf"
        )
else:

    with report_engine.AVAILABLE_REPORTS[ss.selected_report][0](ss.selected_rep_project) as pdf_buffer:
        st.download_button(
            label="Save project report to Downloads folder",
            data=pdf_buffer,
            file_name=f"{ss.selected_rep_project.project_no}_{ss.selected_rep_project.project_name}_report.pdf",
            mime="application/pdf"
        )