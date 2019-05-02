"""This module contains an example how to export buildings from a TEASER
project to ready-to-run simulation models for Modelica library AixLib. These
models will only simulate using Dymola, the reason for this are state
machines that are used in one AixLib specific AHU model.
"""

import teaser.examples.e1_generate_archetype as e1
import teaser.logic.utilities as utilities
import os


def example_change_boundary_conditions():
    """"This function demonstrates the export to Modelica library AixLib using
    the API function of TEASER with an additional change of the ahu boundary
    conditions for the offive building"""

    # In e1_generate_archetype we created a Project with three archetype
    # buildings to get this Project we rerun this example

    prj = e1.example_generate_archetype()

    # To make sure the export is using the desired parameters you should
    # always set model settings in the Project.
    # Project().used_library_calc specifies the used Modelica library
    # Project().number_of_elements_calc sets the models order
    # For more information on models we'd like to refer you to the docs. By
    # default TEASER uses a weather file provided in
    # teaser.data.input.inputdata.weatherdata. You can use your own weather
    # file by setting Project().weather_file_path. However we will use default
    # weather file.
    # Be careful: Dymola does not like whitespaces in names and filenames,
    # thus we will delete them anyway in TEASER.

    prj.used_library_calc = 'AixLib'
    prj.number_of_elements_calc = 2
    prj.weather_file_path = utilities.get_full_path(
        os.path.join(
            "data",
            "input",
            "inputdata",
            "weatherdata",
            "DEU_BW_Mannheim_107290_TRY2010_12_Jahr_BBSR.mos"))

    # now we want to set the ahu profile of the office building with another
    # profil that reduces the ahu during the weekends

    office = [
        bldg for bldg in prj.buildings if bldg.name == "OfficeBuilding"][0]

    v_flow_workday = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]

    v_flow_week = []
    for day in range(7):
        for val in v_flow_workday:
            if day < 5:
                ratio = val
            else:
                if val == 1:
                    ratio = 0.2
                else:
                    ratio = 0.0
            v_flow_week.append(ratio)

    office.central_ahu.v_flow_profile = v_flow_week

    heating_profile_workday = [
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
        293,
    ]

    # We can apply this also to profiles in UseConditions (e.g. set temperature
    # profile for heating (heating_profile)). We assume on weeksends a lower
    # heating setpoint

    heating_profile_week = []
    for day in range(7):
        for val in heating_profile_workday:
            if day < 5:
                set_point = val
            else:
                set_point = 290.0
            heating_profile_week.append(set_point)
    for zone in office.thermal_zones:
        zone.use_conditions.heating_profile_profile = heating_profile_week

    # To make sure the parameters are calculated correctly we recommend to
    # run calc_all_buildings() function

    prj.calc_all_buildings()

    # To export the ready-to-run models simply call Project.export_aixlib().
    # You can specify the path, where the model files should be saved.
    # None means, that the default path in your home directory
    # will be used. If you only want to export one specific building, you can
    # pass over the internal_id of that building and only this model will be
    # exported. In this case we want to export all buildings to our home
    # directory, thus we are passing over None for both parameters.

    prj.export_aixlib(
        internal_id=office.internal_id,
        path=None)


if __name__ == '__main__':

    example_change_boundary_conditions()

    print("Example 9: That's it! :)")