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


def get_eui_and_run_ids(runs: List[Run], output: str,
                        target_folder: Path) -> Tuple[List[float], List[str]]:
    run_ids = []
    eui = []

    for run in runs:
        res_zip = run.download_zipped_output(output)

        run_folder = target_folder.joinpath(run.id)
        if not run_folder.exists():
            run_folder.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(res_zip) as zip_folder:
            zip_folder.extractall(run_folder.as_posix())

        eui_file = run_folder.joinpath('eui.json')
        with open(eui_file.as_posix(), 'r') as file:
            data = json.load(file)
            eui.append(data['eui'])
        run_ids.append(run.id)

    return eui, run_ids


def visualize_results():

    job = job_selector(
        ApiClient(api_token='AB865760.820F423C86287E847DCB2467'),
        default='https://app.pollination.cloud/devang/projects/demo/jobs/e3f3f847-f84c-475f-b1a1-67b44f8288aa',
        help='Copy and paste the URL of your job on pollination.')

    if not job:
        return

    if job.recipe.name != 'annual-energy-use':
        st.error('This app currently only supports annual energy use recipe.')
        return

    # write eui results and get the eui number and run ids
    target_folder = Path(r"C:\Users\devan\OneDrive\Desktop\target_folder")
    eui, run_ids = get_eui_and_run_ids(job.runs, 'eui', target_folder)

    df = job.runs_dataframe.dataframe
    dimension = [dict(label='EUI', values=eui)]
    if 'window-to-wall-ratio' in df.columns:
        dimension.append(
            dict(label='WWR', values=df['window-to-wall-ratio'].values, range=[0, 1]))
    if 'louver-count' in df.columns:
        dimension.append(
            dict(label='Louver count', values=df['louver-count'].values))
    if 'louver-depth' in df.columns:
        dimension.append(
            dict(label='Louver depth', values=df['louver-depth'].values))

    fig = go.Figure(data=go.Parcoords(dimensions=dimension))

    st.plotly_chart(fig)
