"""Visualize the results of a parametric study."""

import streamlit as st
import json
import zipfile
from pollination_streamlit.selectors import job_selector
from pollination_streamlit.api.client import ApiClient
from plotly import graph_objects as go
from typing import List, Tuple
from pathlib import Path
from pollination_streamlit.interactors import Job, Run, Recipe
from queenbee.job.job import JobStatusEnum
from enum import Enum
from viewer import render


class SimStatus(Enum):
    NOTSTARTED = 0
    INCOPLETE = 1
    COMPLETE = 2
    FAILED = 3
    CANCELLED = 4


def request_status(job: Job) -> SimStatus:

    if job.status.status in [
            JobStatusEnum.pre_processing,
            JobStatusEnum.running,
            JobStatusEnum.created,
            JobStatusEnum.unknown]:
        return SimStatus.INCOPLETE

    elif job.status.status == JobStatusEnum.failed:
        return SimStatus.FAILED

    elif job.status.status == JobStatusEnum.cancelled:
        return SimStatus.CANCELLED

    else:
        return SimStatus.COMPLETE


@st.cache()
def get_eui(job) -> List[float]:
    eui_folder = st.session_state.temp_folder.joinpath('eui')
    if not eui_folder.exists():
        eui_folder.mkdir(parents=True, exist_ok=True)

    runs = job.runs
    eui = []

    for run in runs:
        res_zip = run.download_zipped_output('eui')

        run_folder = eui_folder.joinpath(run.id)
        if not run_folder.exists():
            run_folder.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(res_zip) as zip_folder:
            zip_folder.extractall(run_folder.as_posix())

        eui_file = run_folder.joinpath('eui.json')
        with open(eui_file.as_posix(), 'r') as file:
            data = json.load(file)
            eui.append(data['eui'])

    return eui


@st.cache()
def get_figure(job, eui):
    df = job.runs_dataframe.dataframe
    dimension = [
        dict(label='Option-no', values=df['option-no']),
        dict(label='EUI', values=eui)
    ]

    if 'window-to-wall-ratio' in df.columns:
        dimension.append(
            dict(label='WWR', values=df['window-to-wall-ratio'].values, range=[0, 1]))
    if 'louver-count' in df.columns:
        dimension.append(
            dict(label='Louver count', values=df['louver-count'].values))
    if 'louver-depth' in df.columns:
        dimension.append(
            dict(label='Louver depth', values=df['louver-depth'].values))

    figure = go.Figure(data=go.Parcoords(
        line=dict(color='rgb(228, 61, 106)'), dimensions=dimension))

    figure.update_layout(
        font=dict(size=15)
    )

    return figure


def get_job(job_url):

    return job_selector(
        ApiClient(api_token=st.session_state.api_key),
        default=job_url)


def visualize_results(job_url):

    job = get_job(job_url)

    clicked = st.button(label='Refresh to check status')

    if clicked:
        status = request_status(job)
        if status != SimStatus.COMPLETE:
            st.warning(f'Simulation is {status.name}. Refresh to check again'
                       f' or monitor [here]({job_url})')

    if request_status(job) == SimStatus.COMPLETE:

        eui = get_eui(job)

        fig = get_figure(job, eui)

        st.session_state.fig = fig
        st.plotly_chart(st.session_state.fig)

        option_num = st.text_input('Option number', value='')
        if option_num:
            try:
                render(st.session_state.post_viz_dict[int(option_num)])
            except (ValueError, KeyError):
                st.error('Not a valid option number.')
