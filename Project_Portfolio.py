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
import data_viz
import numpy as np
import ui
import utils

from streamlit import session_state as ss


irl_labels = ['Customer Readiness Level',
              'Technology Readiness Level',
              'Business Model Readiness Level',
              'IPR Readiness Level',
              'Team Readiness Level',
              'Funding Readiness Level']

# Currently no sensible way to get theme information.
# We assume dark as this is default until otherwise is proven by user.
dark_mode = (st.context.theme.type == 'dark')

ui.add_logo(dark_mode)

if ss.get('user', None) is None:

    ss['go_to_page'] = 'pages/4_Project_Portfolio.py'
    st.switch_page('pages/2_Login.py')

else:

    user = ss.user
    utils.get_IRL_data(user)

    portfolio = st.sidebar.multiselect("Select your portfolio",
                                       ss.projects,
                                       placeholder="Select projects")
    max_cols = st.sidebar.slider("Max columns",
                                 min_value=1,
                                 max_value=9,
                                 step=1,
                                 value=3)
    ss['project_portfolio'] = portfolio
    cells = len(ss['project_portfolio'])

    # If we have less selected projects than the maximum cols, then...
    if cells < max_cols:

        max_cols = cells

    # Find the number of rows.
    if cells == 0:

        rows = 0

    else:

        rows = int(np.ceil(cells/max_cols))

    # Create the grid for headers and plots.
    grid = ui.make_grid(max_cols, rows*2)
    cell = 0
    row = 0
    col = 0

    # Loop through the selected projects and put headers, plots and
    # assessments where they belong.
    for cell in range(cells):

        if (cell != 0) and (cell % max_cols == 0):

            row += 2
            col = 0

        project = ss['project_portfolio'][cell]
        header = "<h4 style='text-align: center;'>%s</h4>" % project
        grid[row][col].markdown(header, unsafe_allow_html=True)
        project_no = project.project_no
        smooth = ss.user_settings.smooth_irl
        dark_mode = (st.context.theme.type == 'dark')

        irl_plot = data_viz.plot_irl(project,
                                     smooth,
                                     dark_mode)

        with grid[row+1][col]:

            st.pyplot(irl_plot)
            prefix = 'port' + str(project_no)

            if ss.user_settings.ap_table_view:

                ui.show_action_points_table(project)

            else:

                exp = st.expander("Targets and Action Points")

                with exp:

                    ui.show_action_points(prefix, project, None)

            if ss.system_settings.show_valuations and \
               (ss.user.org_id == ss.system_settings.owner_org_id):

                ui.display_valuation(project)

        col += 1

