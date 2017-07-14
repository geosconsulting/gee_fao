#! /usr/bin/env python

import ee


class WaterProductivityCalc(object):

    ee.Initialize()

    _REGION = [[-25.0, -37.0], [60.0, -41.0], [58.0, 39.0], [-31.0, 38.0], [-25.0, -37.0]]
    _COUNTRIES = ee.FeatureCollection('ft:1ZDEMjtnWm_smu7l_z3fx91BbxyCRzP2A3cEMrEiP')
    _WSHEDS = ee.FeatureCollection('ft:1IXfrLpTHX4dtdj1LcNXjJADBB-d93rkdJ9acSEWK')

    def __init__(self):
        pass

class L1WaterProductivity(WaterProductivityCalc):

    """
        Create Water Productivity raster file for annual and dekadal timeframes for Level 1 (Countries and Basins
    """

    _L1_RET_DAILY = ee.ImageCollection("projects/fao-wapor/L1_RET")
    _L1_PCP_DAILY = ee.ImageCollection("projects/fao-wapor/L1_PCP")
    _L1_NPP_DEKADAL = ee.ImageCollection("projects/fao-wapor/L1_NPP")
    _L1_AET_DEKADAL = ee.ImageCollection("projects/fao-wapor/L1_AET")
    _L1_TFRAC_DEKADAL = ee.ImageCollection("projects/fao-wapor/L1_TFRAC")

    def __init__(self):

        ee.Initialize()

        self.L1_logger = logging.getLogger("wpWin.wpCalc")

        self.L1_AET_calc = self._L1_AET_DEKADAL
        self.L1_AGBP_calc = self._L1_NPP_DEKADAL

        self.VisPar_AGBPy = {"opacity": 0.85, "bands": "b1", "min": 0, "max": 850,
                             "palette": "f4ffd9,c8ef7e,87b332,566e1b",
                             "region": WaterProductivityCalc._REGION}

        self.VisPar_ETay = {"opacity": 1, "bands": "b1", "min": 0, "max": 2000,
                            "palette": "d4ffc6,beffed,79c1ff,3e539f",
                            "region": WaterProductivityCalc._REGION}

        self.VisPar_WPgb = {"opacity": 0.85, "bands": "b1", "min": 0, "max": 1.2,
                            "palette": "bc170f,e97a1a,fff83a,9bff40,5cb326",
                            "region": WaterProductivityCalc._REGION}