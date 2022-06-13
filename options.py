"""Module to visualize model with parameters applied."""

import shutil
import streamlit as st
from pathlib import Path
from honeybee.model import Model as HBModel
from honeybee.boundarycondition import Outdoors
from typing import List, Dict, Tuple
from viewer import render


def generate_design_options(design_combinations, abbreviations) -> Tuple[Dict[str, Path], List[Dict]]:

    design_options_folder = st.session_state.temp_folder.joinpath('design_options')
    if design_options_folder.exists():
        shutil.rmtree(design_options_folder)
    design_options_folder.mkdir(exist_ok=True, parents=True)

    base_model = HBModel.from_hbjson(st.session_state.hb_model_path.as_posix())

    faces_with_aperture = [face for face in base_model.faces if face.apertures and isinstance(
        face.boundary_condition, Outdoors)]

    viz_dict = {}  # Only used for visualization
    design_options = []  # Used for submission to pollination

    for design_combination in design_combinations:
        design_option = {}

        for face in faces_with_aperture:
            if 'Window to wall ratio' in design_combination:
                face.apertures_by_ratio(design_combination['Window to wall ratio'])
                design_option['Window to wall ratio'] = design_combination['Window to wall ratio']

            for aperture in face.apertures:
                if 'Louver count' in design_combination and design_combination['Louver count'] > 0 and \
                        'Louver depth' in design_combination and design_combination['Louver depth'] > 0:
                    louvers = aperture.louvers_by_count(
                        design_combination['Louver count'], design_combination['Louver depth'])
                    design_option['Louver count'] = design_combination['Louver count']
                    design_option['Louver depth'] = design_combination['Louver depth']

        # create names
        viz_name = ', '.join(
            [f'{key}:{design_combination[key]}' for key in design_combination])
        file_name = '__'.join(
            [f'{abbreviations[key]}_{design_combination[key]}' for key in design_combination])

        hbjson_file = design_options_folder.joinpath(f'{file_name}.hbjson')

        # write design option as HBJSON
        base_model.to_hbjson(hbjson_file.as_posix())

        viz_dict[viz_name] = hbjson_file
        design_option['model'] = hbjson_file.as_posix()
        design_options.append(design_option)

    return viz_dict, design_options


def get_design_options(design_combinations: List[dict], abbreviations: dict) -> List[Dict]:
    """Visualize a design option."""

    viz_dict, design_options = generate_design_options(
        design_combinations, abbreviations)

    viz_option = st.radio('Select design option to visualize',
                          list(viz_dict.keys()))

    render(viz_dict[viz_option])

    return design_options
