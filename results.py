"""Visualize the results of a parametric study."""


import json
import zipfile
import shutil
import streamlit as st

from enum import Enum
from typing import List, Dict
from pathlib import Path
from plotly import graph_objects as go
from plotly.graph_objects import Figure
from pandas import DataFrame

from pollination_streamlit.api.client import ApiClient
from pollination_streamlit.interactors import Job
from queenbee.job.job import JobStatusEnum

from viewer import render


class SimStatus(Enum):
    NOTSTARTED = 0
    INCOMPLETE = 1
    COMPLETE = 2
    FAILED = 3
    CANCELLED = 4


def request_status(job: Job) -> SimStatus:

    if job.status.status in [
            JobStatusEnum.pre_processing,
            JobStatusEnum.running,
            JobStatusEnum.created,
            JobStatusEnum.unknown]:
        return SimStatus.INCOMPLETE

    elif job.status.status == JobStatusEnum.failed:
        return SimStatus.FAILED

    elif job.status.status == JobStatusEnum.cancelled:
        return SimStatus.CANCELLED

    else:
        return SimStatus.COMPLETE


def extract_eui(file_path: Path) -> float:
    """Extract EUI data from the eui.JSON file."""
    with open(file_path.as_posix(), 'r') as file:
        data = json.load(file)
        return data['eui']


def get_eui(job) -> List[float]:
    """Get a list of EUI data for each run of the job."""

    eui_folder = st.session_state.temp_folder.joinpath('eui')
    st.session_state.eui_folder = eui_folder
    if not eui_folder.exists():
        eui_folder.mkdir(parents=True, exist_ok=True)
    else:
        shutil.rmtree(eui_folder)
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
        eui.append(extract_eui(eui_file))

    return eui


def get_figure(df: DataFrame, eui: List[float]) -> Figure:
    """Prepare Plotly Parallel Coordinates plot."""

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


# @st.cache(allow_output_mutation=True)
def create_job(job_url: str) -> Job:
    """Create a Job object from a job URL."""
    url_split = job_url.split('/')
    job_id = url_split[-1]
    project = url_split[-3]
    owner = url_split[-5]

    return Job(owner, project, job_id, ApiClient(api_token=st.session_state.api_key))


@st.cache()
def download_models(job: Job) -> None:
    """Download HBJSON models from the job."""

    model_folder = st.session_state.temp_folder.joinpath('model')
    if not model_folder.exists():
        model_folder.mkdir(parents=True, exist_ok=True)
    else:
        shutil.rmtree(model_folder.as_posix())
        model_folder.mkdir(parents=True, exist_ok=True)

    artifacts = job.list_artifacts('inputs/model')
    for artifact in artifacts:
        hbjson_artifact = artifact.list_children()[0]
        hbjson_file = model_folder.joinpath(hbjson_artifact.name)
        hbjson_data = hbjson_artifact.download()
        hbjson_file.write_bytes(hbjson_data.read())

    st.session_state.model_folder = model_folder


def visualize_results(job_url):

    job = create_job(job_url)

    if request_status(job) != SimStatus.COMPLETE:
        clicked = st.button('Refresh to update status')
        if clicked:
            status = request_status(job)
            st.warning(f'Simulation is {status.name}.')

    else:
       # streamlit fails to hash a _json.Scanner object so we need to use a conditional
       # here to not run get_eui on each referesh
        if 'eui' not in st.session_state:
            eui = get_eui(job)
            st.session_state.eui = eui

        download_models(job)
        df = job.runs_dataframe.dataframe

        figure = get_figure(df, st.session_state.eui)
        st.plotly_chart(figure)

        option_num = st.text_input('Option number', value='0')
        try:
            render(st.session_state.post_viz_dict[int(
                option_num)], key='results-viewer')
        except (ValueError, KeyError):
            st.error('Not a valid option number.')
            return
