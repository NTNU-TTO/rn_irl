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

from streamlit import session_state as ss


# Set up page.
ui.setup_page()
# Currently no sensible way to get theme information.
# We assume dark as this is default until otherwise is proven by user.
if ss.get('user_settings', None) is None:

    dark_mode = True

else:

    dark_mode = ss.user_settings.dark_mode

ui.add_logo(dark_mode)

about, play = st.tabs(['About', 'Play Around'])

with about:

    st.header("The KTH Innovation Readiness Level™ – General Comments")
    st.markdown("* The KTH Innovation Readiness Level™ is primarily applicable when you have a new idea (product/service/technology/concept/etc.) that you want to realize and take to the market.")
    st.markdown("* The KTH IRL model measures and describes the progress in the development from an idea to a fully implemented innovation on the market. It does not measure the quality or potential of the idea.")
    st.markdown("* The KTH IRL model gives a snapshot of how far you have come in the development process. There is no valuation in being high or low on the scales, it just gives a more objective view of current status.")
    st.markdown("* It is common that you go both up and down (often several times) in the different scales during the development. This is typically due to: 1) actual progress or setbacks, and 2) new insights and understanding of the market, industry, etc. that makes you re-evaluate how far you have come.")
    st.markdown("* The six Readiness Levels can be measured separately but they are connected and interdependent. You do not have to be at the same level in all Readiness Levels at the same time or advance symmetrically. However, big differences (more than 2-3 steps) can become inhibiting to the development and increase the risk of failure.")
    st.markdown("* All Readiness Levels are important, but the order reflects a hierarchy of interdependence. The customer (CRL) and the business model (BRL) influence the product/service (TRL) and vice versa. These three factors influence the IPR strategy (IPRL), and all together influence the team (TmRL). Finally, all of these factors influence the funding needed to take the idea to the market (FRL).")
    st.markdown("* The criteria on the different levels in the KTH IRL model define what you should have achieved to be on that particular level. They do not prescribe how you should achieve it. How you achieve it will depend on the specific idea and the specific context.")
    st.markdown("* The first page of each Readiness Level contains a high-level description of the criteria. The second page contains more detailed criteria. Which level of detail you use depends on what you are using the model for, but the general rule is that you have to have achieved all the criteria on a particular level to be on that level.")
    st.markdown("* The KTH IRL model is designed to be applicable to all kinds of ideas, and different ways of taking the idea to the market. It is, however, challenging to make the definitions general enough to fit many different types of ideas while at the same time specific enough to be practically useful. This means that in some use cases you may have to translate the general definition to a more project specific definition. Some of the definitions may not be relevant for all cases and in those cases, you just skip the non-relevant points and keep the relevant ones.")
    st.markdown("* To calibrate the scales and definitions to your spefic case it is often useful to start thinking about, and defining, what level 9 on each Readiness Level means for your case.")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        st.write(" ")

    with c2:

        st.write(" ")

    with c3:

        if dark_mode:

            st.image('static/KTH_logo_RGB_vit.png', use_container_width="auto")

        else:

            st.image('static/KTH_logo_RGB.png', use_container_width="auto")

        st.markdown("""<a style='display: block; text-align: center;'
                    href="https://kthinnovationreadinesslevel.com/">
                    KTH Innovation Readiness Level™</a>
                    """,
                    unsafe_allow_html=True)

    with c4:

        st.write(" ")

    with c5:

        st.write(" ")

with play:

    irl, explainer = st.columns(2)

    with irl:

        scale = list(range(1, 10))
        crl = ss.get("pa_crl", 1)
        trl = ss.get("pa_trl", 1)
        brl = ss.get("pa_brl", 1)
        iprl = ss.get("pa_iprl", 1)
        tmrl = ss.get("pa_tmrl", 1)
        frl = ss.get("pa_frl", 1)
        pa_irl = ss.get("pa_irl", base.IRLAssessment())
        pa_irl.crl = crl
        pa_irl.trl = trl
        pa_irl.brl = brl
        pa_irl.iprl = iprl
        pa_irl.tmrl = tmrl
        pa_irl.frl = frl
        fig = data_viz.plot_irl(pa_irl, smooth=True)
        st.pyplot(fig)
        cols = st.columns(6)
        cols[0].selectbox("CRL", scale, index=crl-1, key="pa_crl")
        cols[1].selectbox("TRL", scale, index=trl-1, key="pa_trl")
        cols[2].selectbox("BRL", scale, index=brl-1, key="pa_brl")
        cols[3].selectbox("IPRL", scale, index=iprl-1, key="pa_iprl")
        cols[4].selectbox("TMRL", scale, index=tmrl-1, key="pa_tmrl")
        cols[5].selectbox("FRL", scale, index=frl-1, key="pa_frl")
        ss.pa_irl = pa_irl

    with explainer:

        ui.irl_explainer()
