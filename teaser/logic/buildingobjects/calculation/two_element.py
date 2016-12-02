# created December 2016

from __future__ import division
import math
import random
import warnings
import re


class TwoElement(object):
    """This class contains attributes and functions for two element model

    This model distinguishes between internal thermal masses and exterior walls.
    While exterior walls contribute to heat transfer to the ambient, adiabatic
    conditions apply to interior walls. This approach allows considering the
    dynamic behaviour induced by internal heat storage. This class calculates
    and holds all attributes given in documentation.

    It treats Rooftops, GroundFloors and OuterWalls as one type of outer
    walls and computes one RC-combination for these types.

    Depending on the chosen method it will consider an extra resistance for
    windows or merge all windows into the RC-Combination for outer walls.

    Parameters
    ----------
    thermal_zone: ThermalZone()
        TEASER instance of ThermalZone
    merge_windows : boolean
        True for merging the windows into the outer wall's RC-combination,
        False for separate resistance for window, default is False
    t_bt : int
        Time constant according to VDI 6007 (default t_bt = 5)

    Attributes
    ----------
    Interior Walls

    area_iw : float [m2]
        Area of all interior walls.
    alpha_conv_inner_iw : float [W/(m2K)]
        Area-weighted convective coefficient of heat transfer of interior
        walls facing the inside of this thermal zone.
    alpha_rad_inner_iw : float [W/(m2K)]
        Area-weighted radiative coefficient of heat transfer of interior
        walls facing the inside of this thermal zone.
    alpha_comb_inner_iw : float [W/(m2K)]
        Area-weighted combined coefficient of heat transfer of interior walls
        facing the inside of this thermal zone.
    alpha_conv_outer_iw : float [W/(m2K)]
        Area-weighted convective coefficient of heat transfer of interior
        walls facing the adjacent thermal zone. (Currently not supported)
    alpha_rad_outer_iw : float [W/(m2K)]
        Area-weighted radiative coefficient of heat transfer of interior
        walls facing the adjacent thermal zone. (Currently not supported)
    alpha_comb_outer_iw : float [W/(m2K)]
        Area-weighted combined coefficient of heat transfer of interior walls
        facing the adjacent thermal zone. (Currently not supported)
    ua_value_iw : float [W/(m2K)]
        U-Value times interior wall area. (Does not take adjacent thermal
        zones into account)
    r_conv_inner_iw : float [K/W]
        Sum of convective resistances for all interior walls
        facing the inside of this thermal zone.
    r_rad_inner_iw : float [K/W]
        Sum of radiative resistances for all interior walls facing the
        inside of this thermal zone
    r_comb_inner_iw : float [K/W]
        Sum of combined resistances for all interior walls facing the
        inside of this thermal zone
    r1_iw : float [K/W]
        Lumped resistance of interior walls
    c1_iw : float [J/K]
        Lumped capacity of interior walls

    Outer Walls (OuterWall, Rooftop, GroundFloor)

    area_ow : float [m2]
        Area of all outer walls.
    alpha_conv_inner_ow : float [W/(m2K)]
        Area-weighted convective coefficient of heat transfer of outer walls
        facing the inside of this thermal zone.
    alpha_rad_inner_ow : float [W/(m2K)]
        Area-weighted radiative coefficient of heat transfer of outer walls
        facing the inside of this thermal zone.
    alpha_comb_inner_ow : float [W/(m2K)]
        Area-weighted combined coefficient of heat transfer of outer walls
        facing the inside of this thermal zone.
    alpha_conv_outer_ow : float [W/(m2K)]
        Area-weighted convective coefficient of heat transfer of outer walls
        facing the ambient.
    alpha_rad_outer_ow : float [W/(m2K)]
        Area-weighted radiative coefficient of heat transfer of outer walls
        facing the ambient.
    alpha_comb_outer_ow : float [W/(m2K)]
        Area-weighted combined coefficient of heat transfer of outer walls
        facing the ambient.
    ua_value_ow : float [W/(m2K)]
        U-Value times outer wall area.
    r_conv_inner_ow : float [K/W]
        Sum of convective resistances for all outer walls facing the
        inside of this thermal zone.
    r_rad_inner_ow : float [K/W]
        Sum of radiative resistances for all outer walls facing the
        inside of this thermal zone.
    r_comb_inner_ow : float [K/W]
        Sum of combined resistances for all outer walls facing the
        inside of this thermal zone.
    r_conv_outer_ow : float [K/W]
        Sum of convective resistances for all outer walls facing the
        ambient.
    r_rad_outer_ow : float [K/W]
        Sum of radiative resistances for all outer walls facing the
        ambient.
    r_comb_outer_ow : float [K/W]
        Sum of combined resistances for all outer walls facing the
        ambient.
    r1_ow : float [K/W]
        Lumped resistance of outer walls.
    r_rest_ow : float [K/W]
        Lumped remaining resistance of outer walls between r1_ow and c1_ow.
    c1_ow : float [J/K]
        Lumped capacity of outer walls.
    weightfactor_ow : list of floats
        Weightfactors of outer walls (UA-Value of walls with same orientation
        and tilt divided by ua_value_ow)
    weightfactor_ground : list of floats
        Weightfactors of groundfloors (UA-Value of groundfloor divided by
        ua_value_ow).
    tilt_wall : list of floats [degree]
        Tilt of outer walls against the horizontal.
    orientation_wall : list of floats [degree]
        Orientation of outer walls (Azimuth).
        0 - North
        90 - East
        180 - South
        270 - West
    outer_walls_areas : list of floats [m2]
        Area of all outer walls in one list.
    r_rad_ow_iw : float [K/W]
        Resistance for radiative heat transfer between walls.
        TODO: needs to be checked
    ir_emissivity_outer_ow : float
        Area-weighted ir emissivity of outer wall facing the ambient.
    ir_emissivity_inner_ow : float
        Area-weighted ir emissivity of outer walls facing the thermal zone.
    solar_absorp_ow : float
        Area-weighted solar absorption of outer walls facing the ambient.

    Windows

    area_win : float [m2]
        Area of all windows.
    alpha_conv_inner_win : float [W/(m2K)]
        Area-weighted convective coefficient of heat transfer of windows
        facing the inside of this thermal zone.
    alpha_rad_inner_win : float [W/(m2K)]
        Area-weighted radiative coefficient of heat transfer of windows
        facing the inside of this thermal zone.
    alpha_comb_inner_win : float [W/(m2K)]
        Area-weighted combined coefficient of heat transfer of windows facing
        the inside of this thermal zone.
    alpha_conv_outer_win : float [W/(m2K)]
        Area-weighted convective coefficient of heat transfer of windows
        facing the ambient.
    alpha_rad_outer_win : float [W/(m2K)]
        Area-weighted radiative coefficient of heat transfer of windows
        facing the ambient.
    alpha_comb_outer_win : float [W/(m2K)]
        Area-weighted combined coefficient of heat transfer of windows facing
        the ambient.
    ua_value_win : float [W/(m2K)]
        U-Value times outer wall area.
    r_conv_inner_win : float [K/W]
        Sum of convective resistances for all windows facing the
        inside of this thermal zone.
    r_rad_inner_win : float [K/W]
        Sum of radiative resistances for all windows facing the
        inside of this thermal zone.
    r_comb_inner_win : float [K/W]
        Sum of combined resistances for all windows facing the
        inside of this thermal zone.
    r_conv_outer_win : float [K/W]
        Sum of convective resistances for all windows facing the
        ambient.
    r_rad_outer_win : float [K/W]
        Sum of radiative resistances for all windows facing the
        ambient.
    r_comb_outer_win : float [K/W]
        Sum of combined resistances for all windows facing the
        ambient.
    r1_win : float [K/W]
        Lumped resistance of windows.
    r_rest_win : float [K/W]
        Lumped remaining resistance of windows between r1_win and c1_win.
    c1_win : float [J/K]
        Lumped capacity of windows.
    weightfactor_win : list of floats
        Weightfactors of windows (UA-Value of windows with same orientation
        and tilt divided by ua_value_win or ua_value_win+ua_value_ow,
        depending if windows is lumped/merged into the walls or not)
    tilt_win : list of floats [degree]
        Tilt of windows against the horizontal.
    orientation_win : list of floats [degree]
        Orientation of windows (Azimuth).
        0 - North
        90 - East
        180 - South
        270 - West
    window_areas : list of floats [m2]
        Area of all windows in one list.
    solar_absorp_win : float
        Area-weighted solar absorption for windows. (typically 0.0)
    ir_emissivity_win : float
        Area-weighted ir_emissivity for windows. Can be used for windows
        facing the thermal zone and the ambient.
    weighted_g_value : float
        Area-weighted g-Value of all windows.

    Returns
    -------

    calc_success : boolean
        True if calculation was successfull.

    """

    def __init__(self, thermal_zone, merge_windows, t_bt):
        """Constructor for TwoElement"""

        self.internal_id = random.random()

        self.thermal_zone = thermal_zone
        self.merge_windows = merge_windows
        self.t_bt = t_bt

        # Attributes of inner walls
        self.area_iw = 0.0

        # coefficient of heat transfer facing the inside of this thermal zone
        self.alpha_conv_inner_iw = 0.0
        self.alpha_rad_inner_iw = 0.0
        self.alpha_comb_inner_iw = 0.0
        # coefficient of heat transfer facing the adjacent thermal zone
        self.alpha_conv_outer_iw = 0.0
        self.alpha_rad_outer_iw = 0.0
        self.alpha_comb_outer_iw = 0.0

        # UA-Value
        self.ua_value_iw = 0.0

        # resistances for heat transfer facing the inside of this thermal zone
        self.r_conv_inner_iw = 0.0
        self.r_rad_inner_iw = 0.0
        self.r_comb_inner_iw = 0.0
        self.r_conv_outer_iw = 0.0
        self.r_rad_outer_iw = 0.0
        self.r_comb_outer_iw = 0.0

        # lumped resistance/capacity
        self.r1_iw = 0.0
        self.c1_iw = 0.0

        # Attributes for outer walls (OuterWall, Rooftop, GroundFloor)
        self.area_ow = 0.0

        # coefficient of heat transfer facing the inside of this thermal zone
        self.alpha_conv_inner_ow = 0.0
        self.alpha_rad_inner_ow = 0.0
        self.alpha_comb_inner_ow = 0.0

        # coefficient of heat transfer facing the ambient
        self.alpha_conv_outer_ow = 0.0
        self.alpha_rad_outer_ow = 0.0
        self.alpha_comb_outer_ow = 0.0

        # UA-Value
        self.ua_value_ow = 0.0

        # resistances for heat transfer facing the inside of this thermal zone
        self.r_conv_inner_ow = 0.0
        self.r_rad_inner_ow = 0.0
        self.r_comb_inner_ow = 0.0

        # resistances for heat transfer facing the ambient
        self.r_conv_outer_ow = 0.0
        self.r_rad_outer_ow = 0.0
        self.r_comb_outer_ow = 0.0

        # lumped resistances/capacity
        self.r1_ow = 0.0
        self.r_rest_ow = 0.0
        self.c1_ow = 0.0
        self.r_total_ow = 0.0

        # Optical properties
        self.ir_emissivity_outer_ow = 0.0
        self.ir_emissivity_inner_ow = 0.0
        self.solar_absorp_ow = 0.0

        # Additional attributes
        self.weightfactor_ow = []
        self.weightfactor_ground = []
        self.tilt_wall = []
        self.orientation_wall = []
        self.outer_walls_areas = []

        # TODO: check this value
        self.r_rad_ow_iw = 0.0

        # Attributes for windows
        self.area_win = 0.0

        # coefficient of heat transfer facing the inside of this thermal zone
        self.alpha_conv_inner_win = 0.0
        self.alpha_rad_inner_win = 0.0
        self.alpha_comb_inner_win = 0.0

        # coefficient of heat transfer facing the ambient
        self.alpha_conv_outer_win = 0.0
        self.alpha_rad_outer_win = 0.0
        self.alpha_comb_outer_win = 0.0

        # UA-Value
        self.ua_value_win = 0.0

        # resistances for heat transfer facing the inside of this thermal zone
        self.r_conv_inner_win = 0.0
        self.r_rad_inner_win = 0.0
        self.r_comb_inner_win = 0.0

        # resistances for heat transfer facing the ambient
        self.r_conv_outer_win = 0.0
        self.r_rad_outer_win = 0.0
        self.r_comb_outer_win = 0.0

        # lumped resistances/capacity
        self.r1_win = 0.0

        # Optical properties
        self.ir_emissivity_outer_win = 0.0
        self.ir_emissivity_inner_win = 0.0
        self.solar_absorp_win = 0.0

        # Additional attributes
        self.weightfactor_win = []
        self.tilt_win = []
        self.orientation_win = []
        self.window_areas = []
        self.g_sunblind_list = []
        self.weighted_g_value = 0.0

        self._sum_outer_wall_elements()
        self._sum_inner_wall_elements()
        self._sum_window_elements()
        self._calc_outer_elements()
        self._calc_wf()

    def _calc_chain_matrix(self, element_list, omega):
        """Matrix calculation.

        This is a helper function for def parallel_connection() to keep the
        code clean.

        TODO move this to OneElement

        Parameters
        ----------
        wall_count : list
            List of inner or outer walls

        omega : float
            VDI 6007 frequency

        Returns
        ----------
        r1 : float
            VDI 6007 resistance for inner or outer walls

        c1 : float
            VDI 6007 capacity for inner or outer walls
        """

        for wall_count in range(len(element_list) - 1):

            if wall_count == 0:

                r1 = (element_list[wall_count].r1 *
                      element_list[wall_count].c1 ** 2 +
                      element_list[wall_count + 1].r1 *
                      element_list[wall_count + 1].c1 ** 2 + omega ** 2 *
                      element_list[wall_count].r1 *
                      element_list[wall_count + 1].r1 *
                      (element_list[wall_count].r1 +
                       element_list[wall_count + 1].r1) *
                      element_list[wall_count].c1 ** 2 *
                      element_list[wall_count + 1].c1 ** 2) / \
                     ((element_list[wall_count].c1 +
                       element_list[wall_count + 1].c1) ** 2 + omega ** 2 *
                      (element_list[wall_count].r1 +
                       element_list[wall_count + 1].r1) ** 2 *
                      element_list[wall_count].c1 ** 2 *
                      element_list[wall_count + 1].c1 ** 2)

                c1 = ((element_list[wall_count].c1 +
                       element_list[wall_count + 1].c1) ** 2 + omega ** 2 *
                      (element_list[wall_count].r1 +
                       element_list[wall_count + 1].r1) ** 2 *
                      element_list[wall_count].c1 ** 2 *
                      element_list[wall_count + 1].c1 ** 2) / \
                     (element_list[wall_count].c1 +
                      element_list[wall_count + 1].c1 + omega ** 2 *
                      (element_list[wall_count].r1 ** 2 *
                       element_list[wall_count].c1 +
                       element_list[wall_count + 1].r1 ** 2 *
                       element_list[wall_count + 1].c1) *
                      element_list[wall_count].c1 *
                      element_list[wall_count + 1].c1)
            else:
                r1x = r1
                c1x = c1
                r1 = (r1x * c1x ** 2 + element_list[wall_count + 1].r1 *
                      element_list[wall_count + 1].c1 ** 2 +
                      omega ** 2 * r1x * element_list[wall_count + 1].r1 *
                      (r1x + element_list[wall_count + 1].r1) *
                      c1x ** 2 * element_list[wall_count + 1].c1 ** 2) / \
                     ((c1x + element_list[wall_count + 1].c1) ** 2 +
                      omega ** 2 * (
                          r1x + element_list[wall_count + 1].r1) ** 2 *
                      c1x ** 2 * element_list[wall_count + 1].c1 ** 2)

                c1 = ((c1x + element_list[
                    wall_count + 1].c1) ** 2 + omega ** 2 *
                      (r1x + element_list[wall_count + 1].r1) ** 2 * c1x ** 2 *
                      element_list[wall_count + 1].c1 ** 2) / \
                     (c1x + element_list[wall_count + 1].c1 + omega ** 2 *
                      (r1x ** 2 * c1x + element_list[wall_count + 1].r1 **
                       2 * element_list[wall_count + 1].c1) * c1x *
                      element_list[wall_count + 1].c1)
        return r1, c1

    def _sum_outer_wall_elements(self):
        """Sum attributes for outer wall elements

        This function sums and computes the area-weighted values,
        where necessary (the class doc string) for coefficients of heat
        transfer, resistances, areas and UA-Values.

        For TwoElement model it treats rooftops, ground floor and outer walls
        as one kind of wall type.

        """
        # treat all outer wall types identical

        self.area_ow = \
            (sum(out_wall.area for out_wall in
                 self.thermal_zone.outer_walls)
             + sum(ground.area for ground in
                   self.thermal_zone.ground_floors)
             + sum(roof.area for roof in
                   self.thermal_zone.rooftops))

        self.ua_value_ow = \
            (sum(out_wall.ua_value for out_wall in
                 self.thermal_zone.outer_walls)
             + sum(ground.ua_value for ground in
                   self.thermal_zone.ground_floors)
             + sum(roof.ua_value for roof in
                   self.thermal_zone.rooftops))

        # values facing the inside of the thermal zone

        self.r_conv_inner_ow = (1 /
                                (sum(1 / out_wall.r_inner_conv for out_wall in
                                     self.thermal_zone.outer_walls)
                                 + sum(1 / ground.r_inner_conv for ground in
                                       self.thermal_zone.ground_floors)
                                 + sum(1 / roof.r_inner_conv for roof in
                                       self.thermal_zone.rooftops)))

        self.r_rad_inner_ow = (1 /
                               (sum(1 / out_wall.r_inner_rad for out_wall in
                                    self.thermal_zone.outer_walls)
                                + sum(1 / ground.r_inner_rad for ground in
                                      self.thermal_zone.ground_floors)
                                + sum(1 / roof.r_inner_rad for roof in
                                      self.thermal_zone.rooftops)))

        self.r_comb_inner_ow = (1 /
                                (sum(1 / out_wall.r_inner_comb for out_wall in
                                     self.thermal_zone.outer_walls)
                                 + sum(1 / ground.r_inner_comb for ground in
                                       self.thermal_zone.ground_floors)
                                 + sum(1 / roof.r_inner_comb for roof in
                                       self.thermal_zone.rooftops)))

        self.ir_emissivity_inner_ow = (
            sum(out_wall.layer[0].material.ir_emissivity * out_wall.area for
                out_wall in self.thermal_zone.outer_walls)
            + sum(ground.layer[0].material.ir_emissivity * ground.area for
                  ground in self.thermal_zone.ground_floors)
            + sum(roof.layer[0].material.ir_emissivity * roof.area for
                  roof in self.thermal_zone.rooftops) / self.area_ow)

        self.alpha_conv_inner_ow = (
            1 / (self.r_conv_inner_ow * self.area_ow))
        self.alpha_rad_inner_ow = (
            1 / (self.r_rad_inner_ow * self.area_ow))
        self.alpha_comb_inner_ow = (
            1 / (self.r_comb_inner_ow * self.area_ow))

        # values facing the ambient
        # ground floor does not have any coefficients on ambient side

        self.r_conv_outer_ow = (1 /
                                (sum(1 / out_wall.r_outer_conv for out_wall in
                                     self.thermal_zone.outer_walls)
                                 + sum(1 / roof.r_outer_conv for roof in
                                       self.thermal_zone.rooftops)))
        self.r_rad_outer_ow = (1 /
                               (sum(1 / out_wall.r_outer_rad for out_wall in
                                    self.thermal_zone.outer_walls)
                                + sum(1 / roof.r_outer_rad for roof in
                                      self.thermal_zone.rooftops)))
        self.r_comb_outer_ow = (1 /
                                (sum(1 / out_wall.r_outer_comb for out_wall in
                                     self.thermal_zone.outer_walls)
                                 + sum(1 / roof.r_outer_comb for roof in
                                       self.thermal_zone.rooftops)))

        self.ir_emissivity_outer_ow = (
            sum(out_wall.layer[-1].material.ir_emissivity * out_wall.area for
                out_wall in self.thermal_zone.outer_walls)
            + sum(roof.layer[-1].material.ir_emissivity * roof.area for
                  roof in self.thermal_zone.rooftops) / self.area_ow)

        self.solar_absorp_ow = (
            sum(out_wall.layer[-1].material.solar_absorp * out_wall.area for
                out_wall in self.thermal_zone.outer_walls)
            + sum(roof.layer[-1].material.solar_absorp * roof.area for
                  roof in self.thermal_zone.rooftops) / self.area_ow)

        self.alpha_conv_outer_ow = (
            1 / (self.r_conv_outer_ow * self.area_ow))
        self.alpha_rad_outer_ow = (
            1 / (self.r_rad_outer_ow * self.area_ow))
        self.alpha_comb_outer_ow = (
            1 / (self.r_comb_outer_ow * self.area_ow))

    def _sum_inner_wall_elements(self):
        """Sum attributes for interior elements

        This function sums and computes the area-weighted values,
        where necessary (the class doc string) for coefficients of heat
        transfer, resistances, areas and UA-Values.

        It treats all inner walls identical.

        Function is identical for TwoElement, ThreeElement and FourElement.

        Calculation of adjacent thermal zones and thus these attributes are
        currently not supported.

        """
        self.area_iw = \
            (sum(in_wall.area for in_wall in
                 self.thermal_zone.inner_walls)
             + sum(floor.area for floor in
                   self.thermal_zone.floors)
             + sum(ceiling.area for ceiling in
                   self.thermal_zone.ceilings))

        self.ua_value_iw = \
            (sum(in_wall.ua_value for in_wall in
                 self.thermal_zone.inner_walls)
             + sum(floor.ua_value for floor in
                   self.thermal_zone.floors)
             + sum(ceiling.ua_value for ceiling in
                   self.thermal_zone.ceilings))

        # values facing the inside of the thermal zone

        self.r_conv_inner_iw = (1 /
                                (sum(1 / in_wall.r_inner_conv for in_wall in
                                     self.thermal_zone.inner_walls)
                                 + sum(1 / floor.r_inner_conv for floor in
                                       self.thermal_zone.floors)
                                 + sum(1 / ceiling.r_inner_conv for ceiling in
                                       self.thermal_zone.ceilings)))

        self.r_rad_inner_iw = (1 /
                               (sum(1 / in_wall.r_inner_rad for in_wall in
                                    self.thermal_zone.inner_walls)
                                + sum(1 / floor.r_inner_rad for floor in
                                      self.thermal_zone.floors)
                                + sum(1 / ceiling.r_inner_rad for ceiling in
                                      self.thermal_zone.ceilings)))

        self.r_comb_inner_iw = (1 /
                                (sum(1 / in_wall.r_inner_comb for in_wall in
                                     self.thermal_zone.inner_walls)
                                 + sum(1 / floor.r_inner_comb for floor in
                                       self.thermal_zone.floors)
                                 + sum(1 / ceiling.r_inner_comb for ceiling in
                                       self.thermal_zone.ceilings)))

        self.ir_emissivity_inner_iw = (
            sum(in_wall.layer[0].material.ir_emissivity * in_wall.area for
                in_wall in self.thermal_zone.inner_walls)
            + sum(floor.layer[0].material.ir_emissivity * floor.area for
                  floor in self.thermal_zone.floors)
            + sum(ceiling.layer[0].material.ir_emissivity * ceiling.area for
                  ceiling in self.thermal_zone.ceilings) / self.area_iw)

        self.alpha_conv_inner_iw = (
            1 / (self.r_conv_inner_iw * self.area_iw))
        self.alpha_rad_inner_iw = (
            1 / (self.r_rad_inner_iw * self.area_iw))
        self.alpha_comb_inner_iw = (
            1 / (self.r_comb_inner_iw * self.area_iw))

        # adjacent thermal zones are not supported!

    def _sum_window_elements(self):
        """Sum attributes for window elements

        This function sums and computes the area-weighted values,
        where necessary (the class doc string) for coefficients of heat
        transfer, resistances, areas and UA-Values.

        Function is identical for TwoElement, ThreeElement and FourElement.
        """

        self.area_win = sum(win.area for win in self.thermal_zone.windows)
        self.ua_value_win = sum(win.ua_value for win in self.thermal_zone.windows)

        # values facing the inside of the thermal zone

        self.r_conv_inner_win = (1 / (sum(1 / win.r_inner_conv for win in
                                          self.thermal_zone.windows)))

        self.r_rad_inner_ow = (1 / (sum(1 / win.r_inner_rad for win in
                                          self.thermal_zone.windows)))

        self.r_comb_inner_ow = (1 / (sum(1 / win.r_inner_comb for win in
                                          self.thermal_zone.windows)))

        self.ir_emissivity_inner_ow = sum(win.layer[0].material.ir_emissivity
                                          * win.area for win in
                                          self.thermal_zone.windows)

        self.alpha_conv_inner_win = (
            1 / (self.r_conv_inner_win * self.area_win))
        self.alpha_rad_inner_win = (
            1 / (self.r_rad_inner_win * self.area_win))
        self.alpha_comb_inner_win = (
            1 / (self.r_comb_inner_win * self.area_win))

        # values facing the ambient

        self.r_conv_outer_win = (1 / (sum(1 / win.r_outer_conv for win in
                                          self.thermal_zone.windows)))

        self.r_rad_outer_win = (1 / (sum(1 / win.r_outer_rad for win in
                                        self.thermal_zone.windows)))

        self.r_comb_outer_win = (1 / (sum(1 / win.r_outer_comb for win in
                                         self.thermal_zone.windows)))

        self.ir_emissivity_outer_win = sum(win.layer[-1].material.ir_emissivity
                                           * win.area for win in
                                          self.thermal_zone.windows)

        self.solar_absorp_win = sum(win.layer[-1].material.solar_absorp
                                    * win.area for win in
                                    self.thermal_zone.windows)

        self.weighted_g_value = sum(win.g_value * win.area for win in
                                    self.thermal_zone.windows)

        self.alpha_conv_outer_win = (
            1 / (self.r_conv_outer_win * self.area_win))
        self.alpha_rad_outer_win = (
            1 / (self.r_rad_outer_win * self.area_win))
        self.alpha_comb_outer_win = (
            1 / (self.r_comb_outer_win * self.area_win))

    def _calc_outer_elements(self):
        """Lumped parameter for outer elements(walls, roof, grounfloor, windows)

        Doc

        Attributes
        ----------
        omega : float
            TODO documentation for omega
        outer_walls : list
            List containing all TEASER Wall instances that are treated as same
            outer wall type. In case of TwoElement model OuterWalls,
            GroundFloors, Rooftops
        """
        # TODO: documentation for omega
        omega = 2 * math.pi / 86400 / self.t_bt

        outer_walls = (self.thermal_zone.outer_walls +
                       self.thermal_zone.ground_floors +
                       self.thermal_zone.rooftops)

        for out_wall in outer_walls:
            out_wall.calc_equivalent_res()
            out_wall.calc_ua_value()
        for win in self.thermal_zone.windows:
            win.calc_equivalent_res()
            win.calc_ua_value()

        if 0 < len(outer_walls) <= 1:
            # only one outer wall, no need to calculate chain matrix
            self.r1_ow = outer_walls[0].r1
            self.c1_ow = outer_walls[0].c1_korr
        elif len(outer_walls) > 1:
            # more than one outer wall, calculate chain matrix
            self.r1_ow, self.c1_ow = self._calc_chain_matrix(outer_walls,
                                                            omega)
        else:
            warnings.warn("No walls are defined as outer walls, please be "
                          "careful with results. In addition this might lead "
                          "to RunTimeErrors")

        if self.merge_windows is False:
            try:
                self.r1_win = (1 / sum((1 / (win.r1 + win.r_outer_comb)) for
                                       win in self.thermal_zone.windows))

                self.r_total_ow = 1 / self.ua_value_ow
                # TODO check this value (does it needs to be class variable?)
                self.r_rad_ow_iw = 1 / (1 / self.r_rad_inner_ow)

                self.r_rest_ow = (self.r_total_ow - self.r1_ow - (
                    1 / (1 / self.r_conv_inner_ow + 1 / self.r_rad_ow_iw)))

            except RuntimeError:
                print("As no outer walls or no windows are defined lumped "
                      "parameter cannot be calculated")

        if self.merge_windows is True:

            try:
                self.r1_win = (sum((1 / (win.r1 / 6)) for
                                       win in self.thermal_zone.windows))

                self.r1_ow = 1 / (1 / self.r1_ow + self.r1_win)
                self.r_total_ow = 1 / (self.ua_value_ow + self.ua_value_win)
                self.r_rad_ow_iw = 1 / ((1 / self.r_rad_inner_ow) +
                                        (1 / self.r_rad_inner_win))

                self.r_rest_ow = (self.r_total_ow - self.r1_ow - 1 / (
                    ((1 / self.r_conv_inner_ow)
                     + (1 / self.r_conv_inner_win)
                     + (1 / self.r_rad_ow_iw))))

                # TODO: should we handle this in another way?

                self.ir_emissivity_inner_ow = (
                    (self.ir_emissivity_inner_ow * self.area_ow
                     + self.ir_emissivity_inner_win * self.area_win)
                        / (self.area_ow + self.area_win))

                self.ir_emissivity_outer_ow = (
                    (self.ir_emissivity_outer_ow * self.area_ow
                     + self.ir_emissivity_outer_win * self.area_win)
                        / (self.area_ow + self.area_win))

                self.solar_absorp_ow = (
                    (self.solar_absorp_ow * self.area_ow
                     + self.solar_absorp_win * self.area_win)
                        / (self.area_ow + self.area_win))

            except RuntimeError:
                print("As no outer walls or no windows are defined lumped "
                      "parameter cannot be calculated")

    def _calc_inner_elements(self):
        """Lumped parameter for inner walls

        TODO: move this to one_element

        Attributes
        ----------
        omega : float
            TODO documentation for omega
        inner_walls : list
            List containing all TEASER Wall instances that are treated as same
            inner wall type. In case of TwoElement model InnerWall,
            Floor, Ceiling
        """

        # TODO: documentation for omega
        omega = 2 * math.pi / 86400 / self.t_bt

        inner_walls = (self.thermal_zone.inner_walls +
                       self.thermal_zone.floors +
                       self.thermal_zone.ceilings)

        for in_wall in inner_walls:
            in_wall.calc_equivalent_res()
            in_wall.calc_ua_value()

        if 0 < len(inner_walls) <= 1:
            # only one outer wall, no need to calculate chain matrix
            self.r1_1w = inner_walls[0].r1
            self.c1_1w = inner_walls[0].c1_korr
        elif len(inner_walls) > 1:
            # more than one outer wall, calculate chain matrix
            self.r1_1w, self.c1_1w = self._calc_chain_matrix(
                inner_walls,
                omega)
        else:
            warnings.warn("No walls are defined as outer walls, please be "
                          "careful with results. In addition this might lead "
                          "to RunTimeErrors")

    def _calc_wf(self):
        """Weightfactors for outer elements(walls, roof, grounfloor, windows)

        Calculates the weightfactors of the outer walls, including ground and
        windows.

        Parameters
        ----------
        outer_walls : list
            List containing all TEASER Wall instances that are treated as same
            outer wall type. In case of TwoElement model OuterWalls,
            GroundFloors, Rooftops
        """

        outer_walls = (self.thermal_zone.outer_walls +
                       self.thermal_zone.ground_floors +
                       self.thermal_zone.rooftops)

        if self.merge_windows is True:

            for wall in outer_walls:
                wall.wf_out = wall.ua_value / (
                    self.ua_value_ow + self.ua_value_win)

            for win in self.thermal_zone.windows:
                win.wf_out = win.ua_value / (
                    self.ua_value_ow + self.ua_value_win)

        elif self.merge_windows is False:

            for wall in outer_walls:
                wall.wf_out = wall.ua_value / self.ua_value_ow

            for win in self.thermal_zone.windows:
                win.wf_out = win.ua_value / self.ua_value_win

        else:
            raise ValueError("specify merge window method correctly")