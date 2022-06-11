"""A module to create a UI for generating a collection of analysis parameters."""


import streamlit as st
import itertools
from typing import List, Tuple


ABBREVIATIONS = {
    'Window to wall ratio': 'wwr',
    'Louver count': 'lc',
    'Louver depth': 'ld',
    'Wall R value': 'wr',
    'Roof R value': 'rr'
}


@st.cache()
def calculate_design_combinations(params: dict) -> Tuple[List[dict], int]:

    total_runs = 1
    for d in params.values():
        total_runs *= len(d)

    keys = params.keys()
    values = (params[key] for key in keys)
    design_combinations = [dict(zip(keys, combination))
                           for combination in itertools.product(*values)]

    # TODO this can be captured in a unit test
    assert len(design_combinations) == total_runs, 'Calulating design combinations failed.'

    return design_combinations, len(design_combinations)


def get_params() -> Tuple[List[dict], dict]:
    params = {}
    default_value = list(params.keys())

    values = st.multiselect(
        'Select several parameters for parametric studies.',
        options=list(ABBREVIATIONS.keys()),
        default=default_value or ['Window to wall ratio']
    )
    if 'Window to wall ratio' in values:
        with st.container():
            st.header('Window to wall ratio')
            min, max, increment = st.columns(3)

            min_wwr = min.slider('Minimum WWR (%)', min_value=10,
                                 max_value=80, step=5, value=40)
            max_wwr = max.slider('Maximum WWR (%)', min_value=20,
                                 max_value=90, step=5, value=80)
            wwr_increment = increment.slider(
                'Increment', min_value=5, max_value=20, step=5, value=10)
            if max_wwr < min_wwr:
                st.error('Minimum WWR must be smaller than Maximum WWR.')
            wwr_options = list(range(min_wwr, max_wwr + wwr_increment, wwr_increment))
            st.write(f'WWR values: {wwr_options}')
            params['Window to wall ratio'] = [
                wwr*0.01 for wwr in wwr_options]

    if 'Louver count' in values:
        with st.container():
            st.header('Louver count')
            min, max, increment = st.columns(3)
            min_sc = min.selectbox('Minimum number', [0, 1, 2, 3, 4], index=0)
            max_sc = max.selectbox(
                'Maximum number', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], index=0)
            sc_increment = increment.selectbox('Increment', [1, 2, 3], index=0)

            if max_sc % sc_increment != 0:
                add = 0
            else:
                add = sc_increment
            sc_options = list(range(min_sc, max_sc + add, sc_increment))

            st.write(f'Louver count values: {sc_options}')
            params['Louver count'] = sc_options

    if 'Louver depth' in values:
        with st.container():
            st.header('Louver depth')
            min, max, increment = st.columns(3)
            min_sd = min.selectbox('Minimum depth', [0, 0.5, 1], index=0)
            max_sd = max.selectbox(
                'Maximum depth', [0, 0.5, 1, 1.5, 2, 2.5, 3], index=0)
            sd_increment = increment.selectbox(
                'Increment', [0.1, 0.2, 0.5], index=0, key='shade_depth_step')

            remainder = int(str(max_sd / sd_increment).split('.')[-1])
            if remainder == 0:
                add = sd_increment
            else:
                add = 0

            sd_options = [
                x / 10 for x in
                range(int(min_sd * 10), int((max_sd + add) * 10),
                      int(sd_increment * 10))
            ]

            st.write(f'Louver depth values: {sd_options}')
            params['Louver depth'] = sd_options

    if 'Wall R value' in values or 'Roof R value' in values:
        st.error('Changing R value is not supported yet.')

    design_combinations, total_runs = calculate_design_combinations(params)

    st.subheader(f'Total number of runs: {total_runs}')

    return design_combinations, ABBREVIATIONS
