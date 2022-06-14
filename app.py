"""Pollination parametric study app."""

import tempfile
from pathlib import Path
import streamlit as st
from submit import submit
import extra_streamlit_components as stx
from model import set_model
from params import get_design_combinations
from results import visualize_results
from options import get_design_options
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
    st.session_state.status = None

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
            design_combination, param_abbrevs = get_design_combinations()
            st.session_state.design_combinations = design_combination
            st.session_state.param_abbrevs = param_abbrevs

    elif step == 2:
        if 'design_combinations' not in st.session_state or \
                'param_abbrevs' not in st.session_state:
            st.error('You must set the input parameters for the study.'
                     'Go back to step 2 to set the parameters.'
                     )
        else:
            design_options, post_viz_dict = get_design_options(
                st.session_state.design_combinations, st.session_state.param_abbrevs)
            st.session_state.design_options = design_options
            st.session_state.post_viz_dict = post_viz_dict

    elif step == 3:
        if 'design_options' not in st.session_state or \
                'post_viz_dict' not in st.session_state:
            st.error(
                'You should take a look list of design options and visualize a few of them'
                ' before you submit them to Pollination.'
                ' Go back to step 2 to set the parameters.'
            )
        else:
            job_url = submit(st.session_state.design_options)
            st.session_state.job_url = job_url

    elif step == 4:
        st.write(st.session_state)
        if 'job_url' not in st.session_state:
            st.error(
                'Go back to step 3 to submit the job to Pollination first.'
            )
        else:
            visualize_results(st.session_state.job_url)


if __name__ == '__main__':
    main()
