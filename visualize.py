"""Visualize the results of a parametric study."""


import streamlit as st

from typing import List
from plotly import graph_objects as go
from plotly.graph_objects import Figure
from pandas import DataFrame

from viewer import render


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


def visualize(viz_dict, df, eui):

    figure = get_figure(df, eui)
    st.plotly_chart(figure)

    option_num = st.text_input('Option number', value='0')

    try:
        viz_dict[int(option_num)]
    except (ValueError, KeyError):
        st.error('Not a valid option number.')
        return

    render(viz_dict[int(option_num)], key='results-viewer')
