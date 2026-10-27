"""Notebook setup that is not worth a slide: regions, colormap helpers, colour key.

live.py runs `from common import *` before any cell, so cells can use these names.
"""
from functools import partial

import numpy as np
import dask.dataframe as dd
import datashader as ds
import datashader.transfer_functions as tf
from datashader.colors import colormap_select, Greys9
from datashader.utils import lnglat_to_meters as webm

# Regions of interest (lon range, lat range), as in the notebook
USA          = ((-124.72, -66.95), (23.55, 50.06))
LakeMichigan = (( -91.68, -83.97), (40.75, 44.08))
Chicago      = (( -88.29, -87.30), (41.57, 42.00))
Chinatown    = (( -87.67, -87.63), (41.84, 41.86))
cities = {
    "New York":    (( -74.39, -73.44), (40.51, 40.91)),
    "Los Angeles": ((-118.53, -117.81), (33.63, 33.96)),
    "Houston":     (( -96.05, -94.68), (29.45, 30.11)),
    "Atlanta":     (( -84.88, -84.04), (33.45, 33.84)),
    "New Orleans": (( -90.37, -89.89), (29.82, 30.05)),
    "Austin":      (( -97.91, -97.52), (30.17, 30.37)),
}

plot_width = 900
plot_height = int(plot_width * 7.0 / 12)

background = "black"
cm = partial(colormap_select, reverse=(background != "black"))
# The notebook's export() also wrote a PNG to disk; on slides we only need the background
export = partial(tf.set_background, color=background)

if background == "black":
    color_key = {"w": "aqua", "b": "lime", "a": "red", "h": "fuchsia", "o": "yellow"}
else:
    color_key = {"w": "blue", "b": "green", "a": "red", "h": "orange", "o": "saddlebrown"}
races = {"w": "White", "b": "Black", "a": "Asian", "h": "Hispanic", "o": "Other"}

# HoloViews side, for the interactive cells at the end
import holoviews as hv
from holoviews.element import tiles
from holoviews.operation.datashader import datashade, dynspread, rasterize

hv.extension("bokeh")
# The notebook uses CartoDB's label layer, which now requires an API key;
# Esri's public reference layer pairs naturally with the Esri imagery instead.
labels = hv.Tiles("https://server.arcgisonline.com/ArcGIS/rest/services/Reference/"
                  "World_Boundaries_and_Places/MapServer/tile/{Z}/{Y}/{X}")
