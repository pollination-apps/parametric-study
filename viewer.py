"""A module to add a Pollination 3D viewer to the app."""

import streamlit as st
from pathlib import Path
from honeybee_vtk.model import Model as VTKModel
from pollination_streamlit_viewer import viewer


@st.cache(suppress_st_warning=True)
def render(hb_model_path: Path, key='3d_viewer', subscribe=False):
    """Render HBJSON."""

    if not hb_model_path:
        return

    model = VTKModel.from_hbjson(hb_model_path.as_posix())

    vtkjs_folder = st.session_state.temp_folder.joinpath('vtkjs')
    vtkjs_folder.mkdir(parents=True, exist_ok=True)
    vtkjs_file = vtkjs_folder.joinpath(f'{hb_model_path.stem}.vtkjs')

    if not vtkjs_file.is_file():
        model.to_vtkjs(
            folder=vtkjs_folder.as_posix(),
            name=hb_model_path.stem
        )
    viewer(
        content=vtkjs_file.read_bytes(),
        key=key, subscribe=subscribe
    )
