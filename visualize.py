"""Module to visualize model with parameters applied."""

import pathlib
import streamlit as st
from honeybee.model import Model as HBModel
from honeybee.boundarycondition import Outdoors
from typing import List


def get_design_options(design_combinations, abbreviations) -> List[dict]:
    """Generate design options based on the initial model and the input parameters."""

    design_options_folder = st.session_state.temp_folder.joinpath('design_options')
    design_options_folder.mkdir(exist_ok=True, parents=True)

    base_model = HBModel.from_hbjson(st.session_state.hb_model_path.as_posix())

    faces_with_aperture = [face for face in base_model.faces if face.apertures and isinstance(
        face.boundary_condition, Outdoors)]

    design_options = []

    for param in design_combinations:
        for face in faces_with_aperture:
            if 'Window to wall ratio' in param:
                face.apertures_by_ratio(param['Window to wall ratio'])

            for aperture in face.apertures:
                if 'Shade count' in param and 'Shade depth' in param:
                    aperture.louvers_by_count(param['Shade count'], param['Shade depth'])

                elif 'Shade count' in param:
                    aperture.louvers_by_count(param['Shade count'])

                elif 'Shade depth' in param:
                    aperture.louvers_by_depth(param['Shade depth'])

        name = '__'.join([f'{abbreviations[key]}_{param[key]}' for key in param])

        base_model.to_hbjson(design_options_folder.joinpath(f'{name}.hbjson').as_posix())
        design_options.append(
            {name: design_options_folder.joinpath(f'{name}.hbjson').as_posix()})

    return design_options
