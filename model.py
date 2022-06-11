"""A module to provide options for input model.

    To start, It supports
    1. uploading an HBJSON file
    2. Choose from an option of box models from the geometry wizard
    3. link to the model from inside Rhino.

"""

import tempfile
from pathlib import Path
import json
import viewer
import streamlit as st
from pollination_streamlit_io import button
from honeybee.model import Model as HBModel


def set_defaults():
    st.session_state.temp_folder = Path(tempfile.mkdtemp())


def set_model():
    """Render the UI for uploading an input HBJSON model."""

    hb_model_path = st.session_state.get('hb_model_path', None)

    default_index = 0
    options = ['Upload a File', 'Use Geometry Wizard']

    if st.session_state.host.lower() == 'rhino':
        options.append('Link to Model in Rhino')
        default_index = len(options) - 1

    option = st.selectbox(
        'Select a method to input the analytic model', options=options,
        index=default_index
    )

    if 'temp_folder' not in st.session_state:
        st.session_state.temp_folder = Path(tempfile.mkdtemp())

    if option == 'Upload a File':
        uploaded_file = st.file_uploader(
            'Upload an HBJSON file.', type=['hbjson', 'json'],
            accept_multiple_files=False, key='upload_hbjson'
        )

        if uploaded_file:
            hb_model_path = st.session_state.temp_folder.joinpath(uploaded_file.name)
            hb_model_path.write_bytes(uploaded_file.read())
            hb_model = HBModel.from_dict(json.loads(hb_model_path.read_text()))
            st.session_state.hb_model_path = hb_model_path

    elif option == 'Link to Model in Rhino':
        model_data = button.get(is_pollination_model=True, key='pollination-model')

        if model_data:
            hb_model = HBModel.from_dict(model_data)
            hb_model_path = st.session_state.temp_folder.joinpath(
                f'{hb_model.identifier}.hbjson')
            hb_model_path.write_text(json.dumps(model_data))
            st.session_state.hb_model_path = hb_model_path

    elif option == 'Use Geometry Wizard':
        st.session_state.hb_model_path = None
        st.warning('The geometry wizard is not supported yet. 😔')
