"""A module to create the runs and submit the job to Pollination."""

import streamlit as st
import time

from pathlib import Path
from typing import Dict
from pollination_streamlit.api.client import ApiClient
from pollination_streamlit.interactors import Job, NewJob, Recipe


def _get_annual_energy_recipe(api_client):
    return Recipe('ladybug-tools', 'annual-energy-use', 'latest', api_client)


def create_job(design_options) -> NewJob:
    api_key = st.text_input('Enter your Pollination API key', type='password')
    st.session_state.api_key = api_key
    api_client = ApiClient(api_token=api_key)
    if not (api_key and api_client):
        return

    recipe = _get_annual_energy_recipe(api_client)

    st.subheader('Submission information')
    owner = st.text_input('Account name')
    project = st.text_input('Project name', value='demo')

    st.subheader('Location information')
    epw = st.file_uploader('Upload EPW file', type=['epw'])
    if epw:
        epw_file = st.session_state.temp_folder.joinpath(epw.name)
        epw_file.write_bytes(epw.read())
    ddy = st.file_uploader('Upload DDY file', type=['ddy'])
    if ddy:
        ddy_file = st.session_state.temp_folder.joinpath(ddy.name)
        ddy_file.write_bytes(ddy.read())
    if not (owner and epw and ddy):
        return

    new_job = NewJob(owner, project, recipe, client=api_client)

    epw_path = new_job.upload_artifact(epw_file, '.')
    ddy_path = new_job.upload_artifact(ddy_file, '.')

    arguments = []
    for num, design_option in enumerate(design_options):
        # TODO: find a better way to use the design_option dict
        argument = {}
        model_path = new_job.upload_artifact(Path(design_option['model']), '.')
        argument['model'] = model_path
        argument['epw'] = epw_path
        argument['ddy'] = ddy_path
        argument['viz-variables'] = '-v "Zone Mean Radiant Temperature"'
        argument['option-no'] = num
        if 'Window to wall ratio' in design_option:
            argument['window-to-wall-ratio'] = design_option['Window to wall ratio']
        if 'Louver count' in design_option:
            argument['louver-count'] = design_option['Louver count']
        if 'Louver depth' in design_option:
            argument['louver-depth'] = design_option['Louver depth']
        arguments.append(argument)

    new_job.arguments = arguments

    return new_job


def submit_job(job: NewJob) -> Job:
    running_job = job.create()
    return running_job


def submit(design_options: dict):

    new_job = create_job(design_options)

    if new_job:
        submit = st.button(label='Submit Job')
        if submit:
            running_job = submit_job(new_job)
            time.sleep(2)
            job_url = f'https://app.pollination.cloud/{running_job.owner}/projects/{running_job.project}/jobs/{running_job.id}'
            st.success('Job submitted to Pollination. Move to the next tab.')
            return job_url
