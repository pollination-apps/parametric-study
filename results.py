import json
import zipfile
import shutil
from pandas import DataFrame
import streamlit as st

from enum import Enum
from typing import List
from pathlib import Path

from pollination_streamlit.api.client import ApiClient
from pollination_streamlit.interactors import Job
from queenbee.job.job import JobStatusEnum


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


def create_job(job_url: str) -> Job:
    """Create a Job object from a job URL."""
    url_split = job_url.split('/')
    job_id = url_split[-1]
    project = url_split[-3]
    owner = url_split[-5]

    st.session_state.job = Job(owner, project, job_id, ApiClient(
        api_token=st.session_state.api_key))


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


def results(job_url):

    df = DataFrame()
    eui = []

    create_job(job_url)

    job = st.session_state.job

    if request_status(job) != SimStatus.COMPLETE:
        status = request_status(job)
        st.warning(f'Simulation is {status.name}.')
        st.experimental_rerun()

    else:
        eui = get_eui(job)
        download_models(job)
        df = job.runs_dataframe.dataframe
        st.success('Result downloaded. Move to the next tab.')

    return df, eui
