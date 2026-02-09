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
import time
import ui
import utils

from streamlit import session_state as ss

DEBUG = False

@st.dialog("You have incomplete action points!")
def override_dlg():
    ss.override_dlg_done = False
    ss.keep_ass = None
    lbl = "Not all action points defined to increase the IRL are complete.  \n"
    lbl += "What do you want to do with these action points?"
    action = st.radio(lbl, ["Keep unfinished action points",
                            "Discard all action points"])
    cols = st.columns(2)

    with cols[0]:

        if st.button("Save assessment"):

            ss.keep_ass = (action == "Keep unfinished action points")
            ss.override_dlg_done = True
            st.rerun()

    with cols[1]:

        if st.button("Cancel"):

            st.keep_ass = None
            ss.override_dlg_done = True
            st.rerun()


def history_formatter(revision):

    return revision.assessment_date


def create_mom():
    """
    Creates Minutes of Meeting based on action points and comments.

    Returns
    -------
    str
    """
    project = ss.project
    project_id = ss.project.project_no
    project_name = ss.project.project_name
    ass_date = ss.project.assessment_date
    mom = f"Minutes of Meeting {project_id} {project_name} {ass_date}\n\n"

    for irl in ['CRL', 'TRL', 'BRL', 'IPRL', 'TMRL', 'FRL']:

        no_notes = f"No specific notes agreed for {irl}"
        irl_low = irl.lower()
        target_level = getattr(project, f"{irl_low}_target")
        mom += f"{irl} target level: {target_level}\n"
        mom += f"{irl} notes:\n"
        irl_notes = getattr(project, f"{irl_low}_notes")

        if irl_notes is None:

            irl_notes = no_notes

        irl_notes += "\n"
        mom += irl_notes
        mom += f"{irl} Action Points:\n"
        aps = base.get_action_points(project.id, irl)

        for ap in aps.itertuples():

            lead = base.get_user(ap.responsible)
            dd = f"{ap.due_date}"[:10]
            mom += f"* {ap.action_point}\n"
            mom += f"\t- Responsible: {lead}\n"
            mom += f"\t- Due date: {dd}\n"

        if len(aps) == 0:

            mom += f"No specific action points agreed for {irl}.\n\n"

    return mom


def on_IRL_val_changed():
    """
    Callback used for all IRL Level sliders.
    Update the session state values.
    Does not save these values to the database.
    """
    ss.project.crl = ss.crl
    ss.project.trl = ss.trl
    ss.project.brl = ss.brl
    ss.project.iprl = ss.iprl
    ss.project.tmrl = ss.tmrl
    ss.project.frl = ss.frl
    ss.project.project_description = ss.project_description


def on_IRL_ap_changed():
    """
    Callback used for updating IRL targets and action points.

    Returns
    -------
    None.

    """
    # Just update these values for now.
    ss.project.plot_targets = int(ss.ass_plot_targets)
    ss.project.project_notes= ss.ass_project_notes
    ss.project.crl_notes = ss.ass_crl_notes
    ss.project.trl_notes = ss.ass_trl_notes
    ss.project.brl_notes = ss.ass_brl_notes
    ss.project.iprl_notes = ss.ass_iprl_notes
    ss.project.tmrl_notes = ss.ass_tmrl_notes
    ss.project.frl_notes = ss.ass_frl_notes
    ss.project.crl_target = ss.ass_crl_target
    ss.project.trl_target = ss.ass_trl_target
    ss.project.brl_target = ss.ass_brl_target
    ss.project.iprl_target = ss.ass_iprl_target
    ss.project.tmrl_target = ss.ass_tmrl_target
    ss.project.frl_target = ss.ass_frl_target
    ss.project.crl_target_lead = ss.ass_crl_target_lead
    ss.project.trl_target_lead = ss.ass_trl_target_lead
    ss.project.brl_target_lead = ss.ass_brl_target_lead
    ss.project.iprl_target_lead = ss.ass_iprl_target_lead
    ss.project.tmrl_target_lead = ss.ass_tmrl_target_lead
    ss.project.frl_target_lead = ss.ass_frl_target_lead
    ss.project.crl_target_duedate = ss.ass_crl_target_duedate
    ss.project.trl_target_duedate = ss.ass_trl_target_duedate
    ss.project.brl_target_duedate = ss.ass_brl_target_duedate
    ss.project.iprl_target_duedate = ss.ass_iprl_target_duedate
    ss.project.tmrl_target_duedate = ss.ass_tmrl_target_duedate
    ss.project.frl_target_duedate = ss.ass_frl_target_duedate
    ss.project.update(overwrite=True)

    for irl in ['CRL', 'TRL', 'BRL', 'IPRL', 'TMRL', 'FRL']:

        aps_changes = ss.get("ass_%s_aps" % irl.lower())
        ap_df = ss.get("ass_%s_df" % irl.lower())
        edited_rows = aps_changes["edited_rows"]
        added_rows = aps_changes["added_rows"]
        deleted_rows = aps_changes["deleted_rows"]

        for row in edited_rows:

            ap_id = int(ap_df.at[row, "ap_id"])
            ap = base.get_ap(ap_id)

            for attr, val in edited_rows[row].items():

                if attr == "username":

                    attr = "responsible"
                    val = base.get_user_id(val)

                if attr == "progress":

                    val = int(val)

                if attr == "due_date":

                    val = val[:10]

                setattr(ap, attr, val)

            ap.update()
            # Need to delete the action point to avoid an error message later.
            del ap

        for row in added_rows:

            ap = base.ActionPoint()
            ap.assessment_id = ss.project.id
            ap.irl_type = irl
            ap.active = 1

            for attr, val in row.items():

                if attr == "username":

                    attr = "responsible"
                    val = base.get_user_id(val)

                if attr == "progress":

                    val = int(val)

                if attr == "due_date":

                    val = val[:10]

                setattr(ap, attr, val)

            ap.insert()

        for row in deleted_rows:

            ap_id = int(ap_df.at[row, "ap_id"])
            ap = base.get_ap(ap_id)
            setattr(ap, "active", 0)
            ap.update()
            del ap

    ss.refresh = True


def on_history_changed():

    revision = ss.revision
    ss.revision_r = revision


def on_progress_changed():

    r0, r1 = ss.progress_delta
    ss.progress_r0 = r0
    ss.progress_r1 = r1


def on_project_changed():
    """
    Callback for project change.
    Updates current project number and saves to database.
    """

    project_no = ss.project.project_no
    ss.user_settings.last_project_no = int(project_no)
    ss.user_settings.update()
    ss.revision_r = None
    ss.progress_r0 = None
    ss.progress_r1 = None
    sync_session_state()


def sync_session_state():
    # Streamlit does not work well with actual objects between reruns anymore.
    # We need to sync all information from the project explicitly to the session state.
    ss["project_description"] = ss.project.project_description
    ss["ass_project_notes"] = ss.project.project_notes
    ss["ass_plot_targets"] = ss.project.plot_targets

    irl_cats = ['crl', 'trl', 'brl', 'iprl', 'tmrl', 'frl']

    team = base.get_project_team(ss.project.project_no)
    team_options = team.username.to_list()

    for cat in irl_cats:

        ss[f"ass_{cat}_target"] = getattr(ss.project, f"{cat}_target")
        ss[f"ass_{cat}_target_lead"] = getattr(ss.project, f"{cat}_target_lead")
        date = getattr(ss.project, f"{cat}_target_duedate")
        ss[f"ass_{cat}_target_duedate"] = utils.dbdate2datetime(date)
        ss[f"ass_{cat}_notes"] = getattr(ss.project, f"{cat}_notes")

def on_save_assessment():
    """
    Save updated assessment values to database.
    """
    irl_cats = ['crl', 'trl', 'brl', 'iprl', 'tmrl', 'frl']
    keep_ass = ss.get('keep_ass', None)
    irl_ass = ss.project
    old_ass_id = irl_ass.id

    if keep_ass is None:

        ss.save_ass_state = None

        return

    # Update all values from UI values.
    irl_ass.project_description = ss.project_description
    irl_ass.crl = ss.crl
    irl_ass.trl = ss.trl
    irl_ass.brl = ss.brl
    irl_ass.iprl = ss.iprl
    irl_ass.tmrl = ss.tmrl
    irl_ass.frl = ss.frl

    # Save assessment comments if set.
    keep_ass_comments = ss.system_settings.forward_ass_comments

    if keep_ass_comments:

        irl_ass.project_notes = ss.ass_project_notes

        for cat in irl_cats:

            setattr(irl_ass, f"{cat}_notes", ss[f"ass_{cat}_notes"])

    # ...and save to database...
    error = irl_ass.update(keep_ass_notes=keep_ass_comments)

    if keep_ass:

        new_ass_id = base.get_irl_ass_id(irl_ass.project_no)
        base.copy_aps(old_ass_id, new_ass_id)

    ss.refresh = True
    ss.keep_ass = None

    if error is None:

        ss.save_ass_state = 1

    else:
        
        ss.save_ass_state = 0
        ss.save_ass_error = error


def assessment_view(read_only=False):

    # IRL Level Sliders
    st.sidebar.slider("Customer Readiness Level [CRL]",
                      min_value=1,
                      max_value=9,
                      step=1,
                      value=ss.project.crl,
                      key="crl", on_change=on_IRL_val_changed,
                      disabled=read_only)
    st.sidebar.slider("Technology Readiness Level [TRL]",
                      min_value=1,
                      max_value=9,
                      step=1,
                      value=ss.project.trl,
                      key="trl",
                      on_change=on_IRL_val_changed,
                      disabled=read_only)
    st.sidebar.slider("Busines Model Readiness Level [BRL]",
                      min_value=1,
                      max_value=9,
                      step=1,
                      value=ss.project.brl,
                      key="brl",
                      on_change=on_IRL_val_changed,
                      disabled=read_only)
    st.sidebar.slider("IPR Readiness Level [IPRL]",
                      min_value=1,
                      max_value=9,
                      step=1,
                      value=ss.project.iprl,
                      key="iprl",
                      on_change=on_IRL_val_changed,
                      disabled=read_only)
    st.sidebar.slider("Team Readiness Level [TMRL]",
                      min_value=1,
                      max_value=9,
                      step=1,
                      value=ss.project.tmrl,
                      key="tmrl",
                      on_change=on_IRL_val_changed,
                      disabled=read_only)
    st.sidebar.slider("Funding Readiness Level [FRL]",
                      min_value=1,
                      max_value=9,
                      step=1,
                      value=ss.project.frl,
                      key="frl",
                      on_change=on_IRL_val_changed,
                      disabled=read_only)

    # Embed slider values in list for plotting purposes.
    ss['irl_targets'] = [ss.project.crl_target,
                         ss.project.trl_target,
                         ss.project.brl_target,
                         ss.project.iprl_target,
                         ss.project.tmrl_target,
                         ss.project.frl_target]

    # Set up the UI. Viz on the left, descriptions on the right.
    col1, col2 = st.columns([0.5, 0.5])

    if DEBUG:

        st.write(f"Project ID: {ss.project.project_no}")

    with col1:

        plot_h = "Visualization"
        target_h = "Targets and action points per %s:"
        target_h = target_h % ss.project.assessment_date
        plot, targets = st.tabs([plot_h, target_h])

        with plot:

            header = "<h3 style='text-align: center;'>\
                      KTH Innovation Readiness Level™<br>%s</h3>"
            st.markdown(header % ss.project, unsafe_allow_html=True)

            if ss.project is not None:

                smooth = ss.user_settings.smooth_irl
                dark_mode = (st.context.theme.type == 'dark')
                fig = data_viz.plot_irl(ss.project,
                                        smooth,
                                        dark_mode)
                st.pyplot(fig)
                st.text_area("Project description",
                             key='project_description',
                             on_change=on_IRL_val_changed)

        with targets:

            if DEBUG:

                st.write("FROM IRL_ASSESSMENT.PY:")
                st.write(f"Project ID: {ss.project.project_no}")
                st.write(ss.project.project_notes)

            # Target levels and notes.
            ass_changed = base.irl_ass_changed(ss.project)

            if read_only:

                ui.show_action_points('ass', ss.project, None)

            elif ass_changed:

                st.warning("You have unsaved assessment changes.\
                           Please save these first.")
                ui.show_action_points('ass', ss.project, None)

            else:

                ui.make_action_points('ass',
                                      ss.project,
                                      on_IRL_ap_changed)

            if not read_only:

                read_only = not ass_changed

    # Set up all the descriptions and tables.
    with col2:

        con = st.container(border=False)

        with con:

            ui.irl_explainer()

    if st.button("Save assessment", key='save_ass', disabled=read_only):

        # Check for incomplete action points.
        ap_complete = base.ap_completed(ss.project.id)

        if ap_complete:

            ss.override_dlg_done = False
            ss.keep_ass = False
            on_save_assessment()

        else:

            override_dlg()

    odd = ss.get("override_dlg_done", False)

    if odd:

        on_save_assessment()

    state = ss.get("save_ass_state", None)

    if state == 1:

        st.success("Assessment saved!")
        ss.save_ass_state = None
        time.sleep(2)
        st.rerun()

    elif state == 0:

        error = "There was a problem saving the assessment:\n  "
        error += st.save_ass_error
        st.error(error)


def history_view(project):
    """
    Display historical IRL assessment values.

    Parameters
    ----------
    project : TYPE
        DESCRIPTION.
    project_data : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    no_options = len(ss.project_history)
    revision = ss.get('revision_r', None)

    if revision is None or no_options == 1:

        revision = ss.project_history[-1]
        ss.revision_date = revision.assessment_date

    else:

        r = ss.revision_r
        r_index = ss.project_history.index(r)
        r = ss.project_history[r_index]

    if no_options > 1:

        revision = st.sidebar.select_slider("Slide to change project revision",
                                            ss.project_history,
                                            value=revision,
                                            key="revision",
                                            on_change=on_history_changed,
                                            format_func=history_formatter)

    else:

        st.sidebar.radio("Revision:",
                         [revision.assessment_date],
                         key="no_revision")

    if ss.project_history is not None:

        # Set up the UI. Viz on the left, descriptions on the right.
        col1, col2 = st.columns([0.5, 0.5])

        with col1:

            header = "<h3 style='text-align: center;'>KTH Innovation Readiness Level™<br>%s</h3>"
            st.markdown(header % ss.project,
                        unsafe_allow_html=True)

            smooth = ss.user_settings.smooth_irl
            dark_mode = (st.context.theme.type == 'dark')
            fig = data_viz.plot_irl(revision,
                                    smooth,
                                    dark_mode,
                                    True)
            st.pyplot(fig)

        # Set up all the descriptions and tables.
        with col2:

            ui.show_action_points_table(revision, None)


def progress_view(project):
    """
    Displays the delta between two revisions of a project.
    Parameters
    ----------
    project : TYPE
        DESCRIPTION.
    project_data : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    no_options = len(ss.project_history)
    r0 = ss.get('progress_r0', None)

    if r0 is None:

        if no_options > 1:

            r0 = ss.project_history[-2]

        else:

            r0 = ss.project_history[0]

        r1 = ss.project_history[-1]

    else:

        r0 = ss.progress_r0
        r1 = ss.progress_r1
        r0_index = ss.project_history.index(r0)
        r1_index = ss.project_history.index(r1)
        r0 = ss.project_history[r0_index]
        r1 = ss.project_history[r1_index]

    if no_options > 1:

        st.sidebar.select_slider(
            "Select revisions to view progress between",
            ss.project_history,
            value=(r0, r1),
            key="progress_delta",
            on_change=on_progress_changed,
            format_func=history_formatter)

    else:

        st.sidebar.radio("Revision:",
                         [r0.assessment_date],
                         key="no_progress_delta",
                         index=0)

    # Set up the UI. Viz on the left, descriptions on the right.
    col1, col2 = st.columns([0.5, 0.5])

    with col1:

        header = "<h3 style='text-align: center;'>\
                 KTH Innovation Readiness Level™<br>%s</h3>"
        st.markdown(header % ss.project,
                    unsafe_allow_html=True)

        smooth = ss.user_settings.smooth_irl
        dark_mode = (st.context.theme.type == 'dark')
        fig = data_viz.plot_irl_progress(r0,
                                         r1,
                                         smooth,
                                         dark_mode)
        st.pyplot(fig)

    # Set up all the descriptions and tables.
    with col2:

        ui.show_progress(r0, r1, None)

# We start here.
dark_mode = (st.context.theme.type == 'dark')
ui.add_logo(dark_mode)

# If no user has logged in, force login, remember which page we came from.
if ss.get('user', None) is None:

    ss['go_to_page'] = 'pages/3_IRL_Assessment.py'
    st.switch_page('pages/2_Login.py')

else:
    user = ss.user

    # Disable all submissions if user is only allowed to read.
    utils.get_IRL_data(user)

    # Select the last used project initially.
    index = 0
    i = 0
    last_project_no = ss.user_settings.last_project_no

    for project in ss.projects:

        if project.project_no == last_project_no:

            index = i
            break

        i += 1

    # Initialize view state variable.
    if ss.get('irl_view', None) is None:

        ss.irl_view = 'Assessment'

    if len(ss.projects) == 0:

        st.write("You currently do not have any projects. Lucky!")

    else:

        st.sidebar.selectbox("Select project:",
                             ss.projects,
                             index=index,
                             key='project',
                             on_change=on_project_changed)

        if ss.project is None:

            project = ss.projects[index]
            ss.project = project

        sync_session_state()

        project_no = ss.project.project_no
        utils.get_project_history(project_no)
        st.sidebar.radio("View",
                         ["Assessment", "History", "Progress"],
                         key="irl_view",
                         index=0)
        st.sidebar.divider()

        if ss.irl_view == 'Assessment':

            user_rights = ss.user.rights
            project_rights = base.get_project_rights(project_no,
                                                     ss.user.user_id)
            read_only = (user_rights in [0, 6, 7]) or (project_rights == 0)
            assessment_view(read_only)

        elif ss.irl_view == 'History':

            history_view(ss.project)

        elif ss.irl_view == 'Progress':

            progress_view(ss.project)
