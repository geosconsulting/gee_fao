#! /usr/bin/env python
# coding: utf-8
import ee

ee.Initialize()

_L1_NPP_DEKADAL_ROOT = "projects/fao-wapor/L1_"
_L1_AET_DEKADAL_ROOT = "projects/fao-wapor/L1_"
_L1_TFRAC_DEKADAL_ROOT = "projects/fao-wapor/L1_"
_L1_RET_DAILY_ROOT = "projects/fao-wapor/L1_"
_L1_PCP_DAILY_ROOT = "projects/fao-wapor/L1_"

def image_selection(**kwargs):

    """ Returns datasets to be used for WPgm
    Filter datasets selecting only images within the starting end ending date to be used for WPbm"""
    print kwargs

    for key, value in kwargs.iteritems():
        print "%s = %s" % (key, value)

    l1_calc = ee.ImageCollection(_L1_AET_DEKADAL_ROOT + kwargs['dataset'])

    print kwargs.get('year', 2009)

    if 'year' in kwargs:
        collection_l1_calc = l1_calc.filterDate(
            str(kwargs['year']) + '-1-1',
            str(kwargs['year']+1) + '-1-1')
    elif 'data_start' and 'data_end':
        collection_l1_calc = l1_calc.filterDate(
                            kwargs['data_start'],
                            kwargs['data_end'])


    calc_num = collection_l1_calc.size().getInfo()
    return calc_num

@property
def multiply_npp(filtering_values):

    """ Sets the dataset to be used in conjunction with Actual Evapotranspiration for WPgb"""

    data_start = str(filtering_values[1])
    data_end = str(filtering_values[2])

    coll_npp_filtered = _L1_NPP_DEKADAL.filterDate(
        data_start,
        data_end)
    coll_npp_multiplied = coll_npp_filtered.map(lambda npp_images: npp_images.multiply(filtering_values[0]))

    L1_AGBP_calc = coll_npp_multiplied

    return L1_AGBP_calc

# selection_params = {'year': 2015, 'dataset': 'RET', 'data_start': '2015-1-1', 'data_end': '2015-4-30'}
# selection_params = {'dataset': 'AET', 'data_start': '2015-1-1', 'data_end': '2015-4-30'}
# selection_params = {'year': 2015, 'dataset': 'RET'}
selection_params = {'year': 2011, 'dataset': 'AET'}
print image_selection(**selection_params)
