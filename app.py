"""Pollination parametric study app."""

import tempfile
from pathlib import Path
import streamlit as st
import submit_to_pollination
import extra_streamlit_components as stx
from model import set_model
from params import get_params

from visualize import get_design_options
from pollination_streamlit_io import special
from streamlit.server.server import Server
from helper import load_css


st.set_page_config(
    page_title='Parametric Study',
    page_icon='https://app.pollination.cloud/favicon.ico',
    initial_sidebar_state='collapsed',
)


def main():

    load_css('assets/style.css')

    host = special.get_host(key='get_host')
    if not host:
        host = 'web'
    st.session_state.host = host

    st.title('Parametric Study')

    step = stx.stepper_bar(
        steps=['Getting Started', 'Parameters', 'Visualize', 'Submit', 'Results'],
        is_vertical=False
    )

    if step == 0:
        set_model()

    elif step == 1:
        if 'hb_model_path' not in st.session_state:
            st.error(
                'You must load a valid model first. Go back to step 1 and load a model.'
            )
        else:
            design_combinations, param_abbrevs = get_params()
            st.session_state.design_combinations = design_combinations
            st.session_state.param_abbrevs = param_abbrevs
    elif step == 2:
        if not st.session_state.design_combinations or not st.session_state.param_abbrevs:
            st.error(
                'You must set the input parameters for the study. Go back to step 2 to set the parameters.'
            )
        else:
            design_options = get_design_options(
                st.session_state.design_combinations, st.session_state.param_abbrevs)

    elif step == 3:
        if 'params' not in st.session_state:
            st.error(
                'You must set the input parameters for the study before submitting it '
                'to Pollination. Go back to step 2 to set the parameters.'
            )
        job = submit_to_pollination.render(
            st.session_state.hb_model_path,
            st.session_state.params
        )


# current_server = Server.get_current()
# session_infos = Server.get_current()._session_info_by_id.values()

# for v in session_infos:
#     print(v.session._session_data)


if __name__ == '__main__':
    main()
