"""Class for GNSS plots

Description:
------------
TODO

"""
# Standard liberay imports
from collections import namedtuple
from datetime import datetime
import pathlib
from typing import List, Tuple, Union

# External liberary imports
import numpy as np

# Midgard imports
from midgard.collections import enums
from midgard.gnss import gnss
from midgard.plot.matplotlib_extension import plot

# Where imports
from where.data import dataset3 as dataset
from where.lib import config
from where.lib import log


class GnssPlot:
    """Class for GNSS plots
    """

    def __init__(
        self, 
        dset: "Dataset",
        figure_dir: pathlib.PosixPath,
        figure_format: str="png",
    ) -> None:
        """Set up a new GNSS plot object

        Args:
            dset:          A dataset containing the data.
            figure_dir:    Figure directory.
            figure_format: Figure format.
        """
        self.dset = dset
        self.figure_dir = figure_dir
        self.figure_format = figure_format
        
        
    def plot_dop(self,
                  figure_name: str="plot_dop.{FIGURE_FORMAT}",
    ) -> pathlib.PosixPath:
        """Plot DOP
    
        Args:
            figure_name: File name of figure.
        """
        figure_path = self.figure_dir / figure_name.replace("{FIGURE_FORMAT}", self.figure_format)
        log.debug(f"Plot {figure_path}.")
    
        plot(
            x_arrays=[
                self.dset.time.gps.datetime,
                self.dset.time.gps.datetime,
                self.dset.time.gps.datetime,
                self.dset.time.gps.datetime,
                self.dset.time.gps.datetime,
            ],
            y_arrays=[self.dset.gdop, self.dset.pdop, self.dset.vdop, self.dset.hdop, self.dset.tdop],
            xlabel="Time [GPS]",
            ylabel="Dilution of precision",
            y_unit="",
            labels=["GDOP", "PDOP", "VDOP", "HDOP", "TDOP"],
            figure_path=figure_path,
            opt_args={
                "figsize": (7, 4), 
                "legend": True, 
                "plot_to": "file",
            },
        )
        
        return figure_path
        

    def plot_epoch_by_epoch_difference(
                            self, 
                            figure_name: str="plot_epoch_by_epoch_difference_{solution}.{FIGURE_FORMAT}",

    ) -> List[pathlib.PosixPath]:
        """Plot epoch by epoch difference of observations
        
        Args:
            figure_name: File name of figure.
        
        Returns:
            List with figure path for linear combinations depending on GNSS. File name ends with GNSS identifier
            (e.g. 'E', 'G') and observation type, for example 'plot_geometry_free_code_G_C1C_C2X.png'.
        """

        figure_paths = list()
        
        for field in self.dset.diff_epo.fields:

            for sys in sorted(self.dset.meta["obstypes"].keys()):

                x_arrays = []
                y_arrays = []
                labels = []  
                
                # Skip if nothing to plot
                idx_sys = self.dset.filter(system=sys)
                if np.all(np.isnan(self.dset.diff_epo[field][idx_sys])):
                    continue
                                  
                figure_path = self.figure_dir / figure_name.replace("{solution}", f"{sys}_{field}").replace("{FIGURE_FORMAT}", self.figure_format)
                figure_paths.append(figure_path)
                log.debug(f"Plot {figure_path}.")
    
                for sat in sorted(self.dset.unique("satellite")):
                    if not sat.startswith(sys):
                        continue
                    idx = self.dset.filter(satellite= sat)
                    x_arrays.append(self.dset.time.gps.datetime[idx])
                    y_arrays.append(self.dset.diff_epo[field][idx])
                    labels.append(sat)  
                
                # Plot scatter plot
                plot(
                    x_arrays=x_arrays,
                    y_arrays=y_arrays,
                    xlabel="Time [GPS]",
                    ylabel=f"Epoch by epoch difference ({field})",
                    y_unit="m",
                    labels=labels,
                    figure_path=figure_path,
                    opt_args={
                        "figsize": (7, 6),
                        "legend": True,
                        "legend_ncol": 6,
                        "legend_location": "bottom",
                        "plot_to": "file", 
                        "plot_type": "scatter",
                        "statistic": ["rms", "mean", "std", "min", "max", "percentile"],
                    },
                )
                
        return figure_paths
    
    
    def plot_field(
                    self, 
                    field: str,
                    collection: Union[str, None] = None, 
                    figure_name: str="plot_field_{solution}.{FIGURE_FORMAT}",

    ) -> List[pathlib.PosixPath]:
        """Plot field
        
        Args:
            collection:  Collection name.
            field:       Field name.
            figure_name: File name of figure.
        
        Returns:
            List with figure path for depending on GNSS. File name ends with GNSS identifier
            (e.g. 'E', 'G') and field name, for example 'plot_field_G_C1C.png'.
        """

        figure_paths = list()
        fieldname = f"{collection}.{field}" if collection else field
        
        field_def = {
                "gnss_ionosphere": "Ionospheric delay",
                "gnss_range": "Range",
                "gnss_satellite_clock": "Satellite clock",
                "gnss_total_group_delay": "Total group delay",
                "troposphere_radio": "Troposphere delay",
        }

        for sys in sorted(self.dset.meta["obstypes"].keys()):

            x_arrays = []
            y_arrays = []
            labels = []  
            
            # Skip if nothing to plot
            idx_sys = self.dset.filter(system=sys)
            if np.all(np.isnan(self.dset[fieldname][idx_sys])):
                continue
                              
            figure_path = self.figure_dir / figure_name.replace("{solution}", f"{sys}_{field}").replace("{FIGURE_FORMAT}", self.figure_format)
            figure_paths.append(figure_path)
            log.debug(f"Plot {figure_path}.")

            for sat in sorted(self.dset.unique("satellite")):
                if not sat.startswith(sys):
                    continue
                idx = self.dset.filter(satellite= sat)
                x_arrays.append(self.dset.time.gps.datetime[idx])
                y_arrays.append(self.dset[fieldname][idx])
                labels.append(sat)  
            
            # Plot scatter plot
            plot(
                x_arrays=x_arrays,
                y_arrays=y_arrays,
                xlabel="Time [GPS]",
                ylabel=field_def[field] if field in field_def else f"Field ({field})",
                y_unit="m",
                labels=labels,
                figure_path=figure_path,
                opt_args={
                    "figsize": (7, 6),
                    "legend": True,
                    "legend_ncol": 6,
                    "legend_location": "bottom",
                    "plot_to": "file", 
                    "plot_type": "scatter",
                    "statistic": ["rms", "mean", "std", "min", "max", "percentile"],
                },
            )
                
        return figure_paths
    
    
    
    def plot_gnss_signal_in_space_status(
                        self,
                        figure_name: str="plot_signal_in_space_status_{solution}.{FIGURE_FORMAT}",
    ) -> List[pathlib.PosixPath]:
        """Generate GNSS Signal-in-Space (SIS) status plot for each GNSS based on GNSS signal health status (SHS) 
        and for Galileo in addition based on SIS Accuracy (SISA) and data validity status (DVS) given in RINEX 
        navigation file.
    
        The SIS status can be:
    
         | CODE | SIS STATUS      | PLOTTED COLOR | DESCRIPTION                     |
         |------|-----------------|---------------|---------------------------------|
         |   0  | healthy         |         green | SIS status used by all GNSS     |
         |   1  | marginal (SISA) |        yellow | SIS status only used by Galileo |
         |   2  | marignal (DVS)  |        orange | SIS status only used by Galileo |
         |   3  | unhealthy       |           red | SIS status used by all GNSS     |
    
        Args:
            figure_name: File name of figure.
        """
        figure_paths = list()
        colors = {
                "C": ["green", "red"],
                "E": ["green", "yellow", "orange", "red"],
                "G": ["green", "red"],
                "I": ["green", "red"],
                "J": ["green", "red"],
        }
        labels = {
                "C": ["healthy", "unhealthy"],
                "E": ["healthy", "marginal (sisa)", "marginal (dvs)", "unhealthy"],
                "G": ["healthy", "unhealthy"],
                "I": ["healthy", "unhealthy"],
                "J": ["healthy", "unhealthy"],
        }
        status_def = {
                "C": [0, 3],
                "E": [0, 1, 2, 3],
                "G": [0, 3],
                "I": [0, 3],
                "J": [0, 3],
        }
        
        # Loop over GNSSs
        for sys in self.dset.unique("system"):

            signals = self._select_gnss_signal(sys)
            
            # Generate plot for each given navigation type and in case of Galileo in addition for each signal 
            # (e.g. E1, E5a, E5b)
            for signal, nav_type in sorted(signals.items()):
                x_arrays = []
                y_arrays = []
                
                solution = f"{enums.gnss_id_to_name[sys].value.lower()}_{signal}" if signal else f"{enums.gnss_id_to_name[sys].value.lower()}"
                figure_path=self.figure_dir / figure_name.replace("{solution}", solution).replace("{FIGURE_FORMAT}", self.figure_format)
                figure_paths.append(figure_path)
                
                for status in status_def[sys]:
                    if sys == "E":
                        time, satellite = self._get_gnss_signal_in_space_status_data(status, signal, system=sys)
                    else:
                        time, satellite = self._get_gnss_signal_in_space_status_data(status, system=sys)
        
                    x_arrays.append(time)
                    y_arrays.append(satellite)
        
                # Limit x-axis range to rundate
                day_start, day_end = self._get_day_limits()
                
                # Title
                if sys == "E":
                    title = f"{enums.gnss_id_to_name[sys].value.upper()} signal-in-space status for signal {signal.upper()} ({nav_type})"
                else:    
                    title = f"{enums.gnss_id_to_name[sys].value.upper()} signal-in-space status ({nav_type})"
                    
                # Generate plot
                plot(
                    x_arrays=x_arrays,
                    y_arrays=y_arrays,
                    xlabel="Time [GPS]",
                    ylabel="Satellite",
                    y_unit="",
                    labels=labels[sys],
                    colors=colors[sys],
                    figure_path=figure_path,
                    opt_args={
                        "figsize": (7, 8),
                        "marker": "s",
                        "marksersize": 10,
                        "legend_ncol": 4,
                        "legend_location": "bottom",
                        "plot_to": "file",
                        "plot_type": "scatter",
                        "title": title,
                        "xlim": [day_start, day_end],
                    },
                )
            
        return figure_paths
    
    
    def plot_gnss_signal_in_space_status_overview(
                    self,
                    figure_name: str="plot_gnss_signal_in_space_status.{FIGURE_FORMAT}",
    ) -> pathlib.PosixPath:
        """Generate GNSS Signal-in-Space (SIS) status overview plot based on SIS status given in RINEX navigation file
    
        The SIS status can be:
    
         | CODE | SIS STATUS      | PLOTTED COLOR | DESCRIPTION                     |
         |------|-----------------|---------------|---------------------------------|
         |   0  | healthy         |         green | SIS status used by all GNSS     |
         |   1  | marginal (SISA) |        yellow | SIS status only used by Galileo |
         |   2  | marignal (DVS)  |        orange | SIS status only used by Galileo |
         |   3  | unhealthy       |           red | SIS status used by all GNSS     |
    
        Args:
            figure_name: File name of figure.
        """
        figure_path = self.figure_dir / figure_name.replace("{FIGURE_FORMAT}", self.figure_format)
        colors = ["green", "yellow", "orange", "red"]
        labels = ["healthy", "marginal (sisa)", "marginal (dvs)", "unhealthy"]
        status_def = [0, 1, 2, 3]
        signal = None
    
        # Select only one Galileo signal
        # Note: Navigation message for Galileo can include I/NAV and F/NAV messages for different signals (E1, E5a, E5b).
        #       For plotting we choose only one of them.
        if "E" in self.dset.unique("system"):
            signal, _ = self.get_first_galileo_signal()
    
        # Generate time and satellite data for given SIS status
        x_arrays = []
        y_arrays = []
        for status in status_def:
            time, satellite = self._get_gnss_signal_in_space_status_data(status, signal)
            x_arrays.append(time)
            y_arrays.append(satellite)
    
        # Limit x-axis range to rundate
        day_start, day_end = self._get_day_limits()
    
        # Generate plot
        plot(
            x_arrays=x_arrays,
            y_arrays=y_arrays,
            xlabel="Time [GPS]",
            ylabel="Satellite",
            y_unit="",
            labels=labels,
            colors=colors,
            figure_path=figure_path,
            opt_args={
                "figsize": (7, 12),
                "marker": "s",
                "marksersize": 10,
                "legend_ncol": 4,
                "legend_location": "bottom",
                "plot_to": "file",
                "plot_type": "scatter",
                "tick_labelsize": ("y", 7),  # specify labelsize 7 for y-axis
                "title": f"GNSS signal-in-space status",
                "xlim": [day_start, day_end],
            },
        )
        # TODO: Legend has to be improved. Old configuration:
        # figsize = (7, 10)
        # loc="lower center",
        # bbox_to_anchor=(0.5, -0.01),
        # frameon=True,
        
        return figure_path
   
         
    def plot_linear_combinations(
                            self, 
                            figure_name: str="plot_{solution}.{FIGURE_FORMAT}",

    ) -> List[pathlib.PosixPath]:
        """Plot linear combinations of observations
        
        Args:
            figure_name: File name of figure.
        
        Returns:
            List with figure path for linear combinations depending on GNSS. File name ends with GNSS identifier
            (e.g. 'E', 'G') and observation type, for example 'plot_geometry_free_code_G_C1C_C2X.png'.
        """

        FigureInfo = namedtuple("FigureInfo", ["file_path", "name", "system", "obstype"])
        
        figure_info = list()
    
        for field in self.dset.lin.fields:

            # Melbourne-Wübbena linear combination
            if field == "melbourne_wuebbena":
                 
                for sys in sorted(self.dset.meta["obstypes"].keys()):
                    x_arrays = []
                    y_arrays = []
                    labels = []                    
                    solution = f"{field}_{sys}_{'_'.join(self.dset.meta['linear_combination'][field][sys])}"
                    figure_path = self.figure_dir / figure_name.replace("{solution}", solution).replace("{FIGURE_FORMAT}", self.figure_format)
                    log.debug(f"Plot {figure_path}.")
                    figure_info.append(FigureInfo(
                                        figure_path, 
                                        field, 
                                        sys, 
                                        self.dset.meta['linear_combination'][field][sys]),
                    )
        
                    for sat in sorted(self.dset.unique("satellite")):
                        if not sat.startswith(sys):
                            continue
                        idx = self.dset.filter(satellite= sat)
                        x_arrays.append(self.dset.time.gps.datetime[idx])
                        y_arrays.append(self.dset.lin[field][idx])
                        labels.append(sat)  
                    
                    # Plot scatter plot
                    plot(
                        x_arrays=x_arrays,
                        y_arrays=y_arrays,
                        xlabel="Time [GPS]",
                        ylabel="Melbourne-Wübbena",
                        y_unit="m",
                        labels=labels,
                        figure_path=figure_path,
                        opt_args={
                            "figsize": (7, 6),
                            "legend": True,
                            "legend_ncol": 6,
                            "legend_location": "bottom",
                            "plot_to": "file", 
                            "plot_type": "scatter",
                            "statistic": ["rms", "mean", "std", "min", "max", "percentile"],
                        },
                    )
                
            # Code-multipath linear combination
            elif field == "code_multipath_f1" or field == "code_multipath_f2":
                    
                for sys in sorted(self.dset.meta["obstypes"].keys()):
                    x_arrays = []
                    y_arrays = []
                    labels = []
                    solution = f"{field}_{sys}_{'_'.join(self.dset.meta['linear_combination'][field][sys])}"
                    figure_path = self.figure_dir / figure_name.replace("{solution}", solution).replace("{FIGURE_FORMAT}", self.figure_format)
                    figure_info.append(FigureInfo(
                                        figure_path, 
                                        field.replace("_f1", " ").replace("_f2", " "), 
                                        sys, 
                                        self.dset.meta['linear_combination'][field][sys]),
                    )
                        
                    for sat in sorted(self.dset.unique("satellite")):
                        if not sat.startswith(sys):
                            continue
                        idx = self.dset.filter(satellite= sat)
                        x_arrays.append(self.dset.time.gps.datetime[idx])
                        y_arrays.append(self.dset.lin[field][idx])
                        labels.append(sat)  

                    # Plot scatter plot
                    plot(
                        x_arrays=x_arrays,
                        y_arrays=y_arrays,
                        xlabel="Time [GPS]",
                        ylabel="Code-multipath combination",
                        y_unit="m",
                        labels=labels,
                        figure_path=figure_path,
                        opt_args={
                            "figsize": (7, 6),
                            "legend": True,
                            "legend_ncol": 6,
                            "legend_location": "bottom",
                            "plot_to": "file", 
                            "plot_type": "scatter",
                            "statistic": ["rms", "mean", "std", "min", "max", "percentile"],
                        },
                    ) 
                    
            # Code-phase difference
            elif field == "code_phase_f1" or field == "code_phase_f2":
                    
                for sys in sorted(self.dset.meta["obstypes"].keys()):
                    x_arrays = []
                    y_arrays = []
                    labels = []
                    solution = f"{field}_{sys}_{'_'.join(self.dset.meta['linear_combination'][field][sys])}"
                    figure_path = self.figure_dir / figure_name.replace("{solution}", solution).replace("{FIGURE_FORMAT}", self.figure_format)
                    log.debug(f"Plot {figure_path}.")
                    figure_info.append(FigureInfo(
                                        figure_path, 
                                        field.replace("_f1", " ").replace("_f2", " "), 
                                        sys, 
                                        self.dset.meta['linear_combination'][field][sys]),
                    )
                        
                    for sat in sorted(self.dset.unique("satellite")):
                        if not sat.startswith(sys):
                            continue
                        idx = self.dset.filter(satellite= sat)
                        x_arrays.append(self.dset.time.gps.datetime[idx])
                        y_arrays.append(self.dset.lin[field][idx])
                        labels.append(sat)  

                    # Plot scatter plot
                    plot(
                        x_arrays=x_arrays,
                        y_arrays=y_arrays,
                        xlabel="Time [GPS]",
                        ylabel="Code-phase difference",
                        y_unit="m",
                        labels=labels,
                        figure_path=figure_path,
                        opt_args={
                            "figsize": (7, 6),
                            "legend": True,
                            "legend_ncol": 6,
                            "legend_location": "bottom",
                            "plot_to": "file", 
                            "plot_type": "scatter",
                            "statistic": ["rms", "mean", "std", "min", "max", "percentile"],
                        },
                    ) 
                                        
            # Geometry_free, ionosphere_free, wide_lane and narrow_lane linear combination
            else:
                   
                for sys in sorted(self.dset.unique("system")):
                    x_arrays = []
                    y_arrays = []
                    labels = []
                    solution = f"{field}_{sys}_{'_'.join(self.dset.meta['linear_combination'][field][sys])}"
                    figure_path = self.figure_dir / figure_name.replace("{solution}", solution).replace("{FIGURE_FORMAT}", self.figure_format)
                    log.debug(f"Plot {figure_path}.")
                    figure_info.append(FigureInfo(
                                        figure_path, 
                                        "_".join(field.split('_')[0:2]), # Remove _code, _doppler, _phase or _snr  
                                        sys, 
                                        self.dset.meta['linear_combination'][field][sys]),
                    )
                        
                    for sat in sorted(self.dset.unique("satellite")):
                        if not sat.startswith(sys):
                            continue
                        idx = self.dset.filter(satellite= sat)
                        x_arrays.append(self.dset.time.gps.datetime[idx])
                        y_arrays.append(self.dset.lin[field][idx])
                        labels.append(sat)                        
                        
                    # Get ylabel
                    name1, name2, obscode = field.split("_")                                    
                    ylabel = f"{name1.capitalize()}-{name2} ({obscode})"
                    
                    # Plot scatter plot
                    plot(
                        x_arrays=x_arrays,
                        y_arrays=y_arrays,
                        xlabel="Time [GPS]",
                        ylabel=ylabel,
                        y_unit="m",
                        labels=labels,
                        figure_path=figure_path,
                        opt_args={
                            "figsize": (7, 6),
                            "legend": True,
                            "legend_ncol": 6,
                            "legend_location": "bottom",
                            "plot_to": "file", 
                            "plot_type": "scatter",
                            "statistic": ["rms", "mean", "std", "min", "max", "percentile"],
                        },
                    )

        return figure_info


    def plot_number_of_satellites(
                        self, 
                        figure_name: str="plot_gnss_number_of_satellites_epoch.{FIGURE_FORMAT}",
    ) -> pathlib.PosixPath:
        """Plot number of satellites based for each GNSS
        
        Args:
            figure_name: File name of figure.
        
        Returns:
            Figure path.
        """
    
        # Generate x- and y-axis data per system
        x_arrays = []
        y_arrays = []
        labels = []
        figure_path = self.figure_dir / figure_name.replace("{FIGURE_FORMAT}", self.figure_format)
        log.debug(f"Plot {figure_path}.")
    
        for sys in sorted(self.dset.unique("system")):
            idx = self.dset.filter(system=sys)
            x_arrays.append(self.dset.time.gps.datetime[idx])
            y_arrays.append(gnss.get_number_of_satellites(
                                            self.dset.system[idx], 
                                            self.dset.satellite[idx], 
                                            self.dset.time.gps.datetime[idx])
            )
            labels.append(enums.gnss_id_to_name[sys].value)
    
        # Plot scatter plot
        plot(
            x_arrays=x_arrays,
            y_arrays=y_arrays,
            xlabel="Time [GPS]",
            ylabel="# satellites",
            y_unit="",
            labels=labels,
            figure_path=figure_path,
            opt_args={
                "figsize": (7, 4), 
                "marker": ",",
                "legend": True,
                "legend_location": "bottom",
                "legend_ncol": len(self.dset.unique("system")),
                "plot_to": "file", 
                "plot_type": "plot"
            },
        )
        
        return figure_path
    
    
    def plot_number_of_satellites_used(
            self, 
            figure_name: str="plot_number_of_satellites_used.{FIGURE_FORMAT}",
    ) -> pathlib.PosixPath:
        """Plot available number of satellites against used number
    
        Args:
            figure_name: File name of figure.
        
        Returns:
            Figure path.
        """
        figure_path = self.figure_dir / figure_name.replace("{FIGURE_FORMAT}", self.figure_format)
        log.debug(f"Plot {figure_path}.")
    
        if "num_satellite_used" not in self.dset.fields:
            self.dset.add_float(
                "num_satellite_used",
                val=gnss.get_number_of_satellites(
                                    self.dset.system, 
                                    self.dset.satellite, 
                                    self.dset.time.gps.datetime),
            )
    
        plot(
            x_arrays=[self.dset.time.gps.datetime, self.dset.time.gps.datetime],
            y_arrays=[self.dset.num_satellite_available, self.dset.num_satellite_used],
            xlabel="Time [GPS]",
            ylabel="Number of satellites",
            y_unit="",
            labels=["Available", "Used"],
            figure_path=figure_path,
            opt_args={
                "figsize": (7, 4), 
                "legend": True, 
                "marker": ",", 
                "plot_to": "file", 
                "plot_type": "plot"
            },
        )
        
        return figure_path
    
        
    def plot_obstype_availability(
                            self, 
                            figure_name: str="plot_obstype_availability_{system}.{FIGURE_FORMAT}",
    ) -> List[pathlib.PosixPath]:
        """Generate GNSS observation type observation type availability based on RINEX observation file
 
        Args:
            figure_name: File name of figure.
            
        Returns:
            List with figure path for observation type availability depending on GNSS. File name ends with GNSS 
            identifier (e.g. 'E', 'G'), for example 'plot_obstype_availability_E.png'.
        """
    
        figure_paths = list()
    
        for sys in sorted(self.dset.unique("system")):

            x_arrays = []
            y_arrays = []
            
            idx_sys = self.dset.filter(system=sys)
            num_sat = len(set(self.dset.satellite[idx_sys]))
            
            figure_path = self.figure_dir / figure_name.replace("{system}", sys).replace("{FIGURE_FORMAT}", self.figure_format)
            figure_paths.append(figure_path)
            log.debug(f"Plot {figure_path}.")
            
            for sat in sorted(self.dset.unique("satellite"), reverse=True):
                if not sat.startswith(sys):
                    continue
                
                idx_sat = self.dset.filter(satellite=sat)
                keep_idx = np.full(self.dset.num_obs, False, dtype=bool)
                
                for obstype in self._sort_string_array(self.dset.meta["obstypes"][sys]):
                    keep_idx[idx_sat] = np.logical_not(np.isnan(self.dset.obs[obstype][idx_sat]))
                    #time_diff = np.diff(self.dset.time.gps.gps_seconds[keep_idx]) 
                    #time_diff = np.insert(time_diff, 0, float('nan')) 
                    
                    if np.any(keep_idx):
                        num_obs = len(self.dset.time[keep_idx])
                        x_arrays.append(self.dset.time.gps.datetime[keep_idx])
                        y_arrays.append(np.full(num_obs, f"{sat}_{obstype}"))

            plot(
                x_arrays=x_arrays,
                y_arrays=y_arrays,
                xlabel="Time [GPS]",
                ylabel="Satellite and observation type",
                figure_path=figure_path,
                y_unit="",
                opt_args={
                    "colormap": "tab20",
                    "figsize": (1.0 * num_sat, 3.0 * num_sat),
                    "fontsize": 5,
                    "plot_to": "file",
                    "plot_type": "scatter",
                    #"title": "Satellite and observation type",
                },
            )

        return figure_paths
    

    def plot_satellite_availability(
                            self, 
                            figure_name: str="plot_satellite_availability.{FIGURE_FORMAT}",
    ) -> pathlib.PosixPath:
        """Generate GNSS satellite observation availability overview based on RINEX observation file
 
        Args:
            figure_name: File name of figure.
            
        Returns:
            Figure path.
        """
    
        # Generate x- and y-axis data per system
        x_arrays = []
        y_arrays = []
        labels = []
        figure_path = self.figure_dir / figure_name.replace("{FIGURE_FORMAT}", self.figure_format)
        log.debug(f"Plot {figure_path}.")
    
        time, satellite, system = self._sort_by_satellite()
    
        for sys in sorted(self.dset.unique("system"), reverse=True):
            idx = system == sys
            x_arrays.append(time[idx])
            y_arrays.append(satellite[idx])
            labels.append(enums.gnss_id_to_name[sys].value)
            
        # Plot scatter plot
        num_sat = len(self.dset.unique("satellite"))
        plot(
            x_arrays=x_arrays,
            y_arrays=y_arrays,
            xlabel="Time [GPS]",
            ylabel="Satellite",
            y_unit="",
            #labels=labels,
            figure_path=figure_path,
            opt_args={
                "colormap": "tab20",
                "figsize": (0.1 * num_sat, 0.2 * num_sat),
                "fontsize": 10,
                "legend": True,
                "legend_location": "bottom",
                "legend_ncol": len(self.dset.unique("system")),
                "plot_to": "file",
                "plot_type": "scatter",
                #"title": "Satellite availability",
            },
        )
        
        return figure_path
    
        
        
    def plot_skyplot(
                    self,
                    figure_name: str="plot_skyplot_{system}.{FIGURE_FORMAT}",
    ) -> List[pathlib.PosixPath]:
        """Plot skyplot for each GNSS
        
        Args:
            figure_name: File name of figure.
    
        Returns:
            List with figure path for skyplot depending on GNSS. File name ends with GNSS identifier (e.g. 'E', 'G'), 
            for example 'plot_skyplot_E.png'.
        """
        figure_paths = list()
    
        # Convert azimuth to range 0-360 degree
        azimuth = self.dset.site_pos.azimuth
        idx = azimuth < 0
        azimuth[idx] = 2 * np.pi + azimuth[idx]
    
        # Convert zenith distance from radian to degree
        zenith_distance = np.rad2deg(self.dset.site_pos.zenith_distance)
    
        # Generate x- and y-axis data per system
        for sys in sorted(self.dset.unique("system")):
            x_arrays = []
            y_arrays = []
            labels = []
           
            figure_path = self.figure_dir / figure_name.replace("{system}", sys).replace("{FIGURE_FORMAT}", self.figure_format)
            figure_paths.append(figure_path)
            
            for sat in sorted(self.dset.unique("satellite")):
                if not sat.startswith(sys):
                    continue
                idx = self.dset.filter(satellite= sat)
                x_arrays.append(azimuth[idx])
                y_arrays.append(zenith_distance[idx])
                labels.append(sat)
        
            # Plot with polar projection
            # TODO: y-axis labels are overwritten after second array plot. Why? What to do?
            plot(
                x_arrays=x_arrays,
                y_arrays=y_arrays,
                xlabel="",
                ylabel="",
                y_unit="",
                labels=labels,
                figure_path=figure_path,
                opt_args={
                    "colormap": "tab20",
                    "figsize": (7, 7.5),
                    "legend": True,
                    "legend_ncol": 6,
                    "legend_location": "bottom",
                    "plot_to": "file",
                    "plot_type": "scatter",
                    "projection": "polar",
                    "title": f"Skyplot for {enums.gnss_id_to_name[sys]}\n Azimuth [deg] / Elevation[deg]",
                    "xlim": [0, 2 * np.pi],
                    "ylim": [0, 90],
                    "yticks": (range(0, 90, 30)),  # sets 3 concentric circles
                    "yticklabels": (map(str, range(90, 0, -30))),  # reverse labels from zenith distance to elevation
                },
            )
        
        return figure_paths
    
    
    def plot_satellite_elevation(
                    self,
                    figure_name: str="plot_satellite_elevation_{system}.{FIGURE_FORMAT}",
    ) -> List[pathlib.PosixPath]:
        """Plot satellite elevation for each GNSS
    
        Args:
            figure_name: File name of figure.
            
        Returns:
            List with figure path for skyplot depending on GNSS. File name ends with GNSS identifier (e.g. 'E', 'G'), 
            for example 'plot_skyplot_E.png'.
        """
        figure_paths = list()
    
        # Convert elevation from radian to degree
        elevation = np.rad2deg(self.dset.site_pos.elevation)
    
        # Limit x-axis range to rundate
        day_start, day_end = self._get_day_limits()
         
        # Generate x- and y-axis data per system
        for sys in sorted(self.dset.unique("system")):
            x_arrays = []
            y_arrays = []
            labels = []
            
            figure_path = self.figure_dir / figure_name.replace("{system}", sys).replace("{FIGURE_FORMAT}", self.figure_format)
            figure_paths.append(figure_path)
            log.debug(f"Plot {figure_path}.")
    
            for sat in sorted(self.dset.unique("satellite")):
                if not sat.startswith(sys):
                    continue
                idx = self.dset.filter(satellite=sat)
                x_arrays.append(self.dset.time.gps.datetime[idx])
                y_arrays.append(elevation[idx])
                labels.append(sat)
        
            # Plot with scatter plot
            plot(
                x_arrays=x_arrays,
                y_arrays=y_arrays,
                xlabel="Time [GPS]",
                ylabel="Elevation [deg]",
                y_unit="",
                labels=labels,
                figure_path=figure_path,
                opt_args={
                    "colormap": "tab20",
                    "figsize": (7, 8),
                    "legend": True,
                    "legend_ncol": 6,
                    "legend_location": "bottom",
                    "plot_to": "file",
                    "plot_type": "scatter",
                    "title": f"Satellite elevation for {enums.gnss_id_to_name[sys]}",
                    "xlim": [day_start, day_end],
                },
            )
            
        return figure_paths



    def plot_satellite_overview(
                    self,
                    figure_name: str="plot_satellite_overview.{FIGURE_FORMAT}",
    ) -> Union[pathlib.PosixPath, None]:
        """Plot satellite observation overview
    
        Args:
           dset:        A dataset containing the data.
           figure_dir:  Figure directory
           
        Returns:
           Figure path or None if necessary datasets could not be read
        """
        figure_path = self.figure_dir / figure_name.replace("{FIGURE_FORMAT}", self.figure_format)
        log.debug(f"Plot {figure_path}.")
    
        # Limit x-axis range to rundate
        day_start, day_end = self._get_day_limits()
    
        # Get time and satellite data from read and orbit stage
        file_vars = {**self.dset.vars, **self.dset.analysis}
        file_vars["stage"] = "read"
        file_path = config.files.path("dataset", file_vars=file_vars)
        if file_path.exists(): 
            time_read, satellite_read, _ = self._sort_by_satellite(
                self._get_dataset(stage="read", systems=self.dset.meta["obstypes"].keys())
            )
            time_orbit, satellite_orbit, _ = self._sort_by_satellite(
                self._get_dataset(stage="orbit", systems=self.dset.meta["obstypes"].keys())
            )
            time_edit, satellite_edit, _ = self._sort_by_satellite(
                self._get_dataset(stage="edit", systems=self.dset.meta["obstypes"].keys())
            )
            
        else:
            # NOTE: This is the case for concatencated Datasets, where "read" and "edit" stage data are not available.
            log.warn(f"Read dataset does not exists: {file_path}. Plot {figure_path} can not be plotted.")
            return None
    
        # Generate plot
        plot(
            x_arrays=[time_read.tolist(), time_orbit.tolist(), time_edit.tolist()],
            y_arrays=[satellite_read.tolist(), satellite_orbit.tolist(), satellite_edit.tolist()],
            xlabel="Time [GPS]",
            ylabel="Satellite",
            y_unit="",
            # labels = ["Rejected in orbit stage", "Rejected in edit stage", "Kept observations"],
            colors=["red", "orange", "green"],
            figure_path=figure_path,
            opt_args={
                "colormap": "tab20",
                "figsize": (7, 6),
                "marker": "|",
                "plot_to": "file",
                "plot_type": "scatter",
                "title": "Overview over satellites",
                "xlim": [day_start, day_end],
            },
        )
        
        return figure_path


    #        
    # ADDITIONAL PUBLIC FUNCTIONS
    # 
    def get_first_galileo_signal(self):
        """Get first Galileo signal given in the navigation message based on ordered list
       
        Returns:
           Tuple with chosen Galileo signal and navigation message type
        """        
        signals = self._select_gnss_signal(system="E")
        signal = next(iter(sorted(signals)))
        nav_type = signals[signal]
    
        return signal, nav_type
    
    
    #        
    # AUXILIARY FUNCTIONS
    # 
    def _get_dataset(
            self, 
            stage: str, 
            systems: Union[List[str], None] = None,
    ) -> "Dataset":
        """Get dataset for given stage
    
        Args:
           systems:     List with GNSS identifiers (e.g. E, G, ...)
    
        Returns:
           Dataset for given stage or error exit status if dataset could not be read
        """
    
        # Get Dataset
        # TODO: "label" should have a default value.
        file_vars = {**self.dset.vars, **self.dset.analysis}
        file_vars["stage"] = stage
        try:
            dset_out = dataset.Dataset.read(**file_vars)
        except OSError:
            log.warn("Could not read dataset {config.files.path('dataset', file_vars=file_vars)}.")
            return enums.ExitStatus.error
    
        # Reject not defined GNSS observations
        if systems:
            systems = [systems] if isinstance(systems, str) else systems
            keep_idx = np.zeros(dset_out.num_obs, dtype=bool)
            for sys in systems:
                idx = dset_out.filter(system=sys)
                keep_idx[idx] = True
            dset_out.subset(keep_idx)
    
        return dset_out
    
    
    def _get_day_limits(self) -> Tuple[datetime, datetime]:
        """Get start and end time for given run date
    
            Returns:
                Start and end date. 
            """
        day_start = min(self.dset.time.datetime)
        day_end = max(self.dset.time.datetime)
    
        return day_start, day_end
    
    
    def _get_gnss_signal_in_space_status_data(
                self,
                status: int, 
                signal: Union[str, None]=None,
                system: Union[str, None]=None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Get GNSS signal in space status (SIS) time and satellite data based on a given SIS status
    
        The SIS status can be:
    
         | CODE | SIS STATUS      | 
         |------|-----------------|
         |   0  | healthy         |
         |   1  | marginal (SISA) | 
         |   2  | marignal (DVS)  |
         |   3  | unhealthy       |
    
        The SIS status code is used for representing the SIS status in the dataset fields "sis_status_<signal>" (with 
        <signal>: e1, e5a or e5b).
    
        Args:
           status:        Signal in space status.   
           signal:        Galileo signal for which SIS status should be determined. The signal can be e1, e5a or e5b.
           system:        Get only signal in space status for selected system identifier.
    
        Returns:
            Tuple with time and satellite data for a given SIS status and ordered by satellite
        """
        # TODO: order of satellites is not correct. Maybe to save the data in a dataframe could help?
    
        # Generate x- and y-axis data
        time = []
        satellite = []
    
        for sat in sorted(self.dset.unique("satellite"), reverse=True):
            
            if system: # Skip GNSS, which are not selected
                if not sat.startswith(system):
                    continue
                
            idx = self.dset.filter(satellite=sat)
    
            if sat.startswith("E"):
                idx_status = getattr(self.dset, "sis_status_" + signal)[idx] == status
            else:
                if status == 0:  # healthy status
                    idx_status = self.dset.sv_health[idx] == 0
                elif status == 3:  # unhealthy status
                    idx_status = self.dset.sv_health[idx] > 0
                else:
                    continue
    
            time.extend(self.dset.time.gps.datetime[idx][idx_status])
            satellite.extend(self.dset.satellite[idx][idx_status])
    
        return time, satellite
        
        
    def _select_gnss_signal(self, system: Union[str, None]=None) -> Tuple[List[str], str]:
        """Select GNSS signal depending on given data in Dataset
    
        Args:
            system:  System identifier
            
        Returns:
            Selected GNSS signal
        """
        nav_type_def = {
                "FNAV_E5a": {"e5a": "F/NAV"},
                "INAV_E1": {"e1": "I/NAV"},
                "INAV_E5b": {"e5b": "I/NAV"},
                "INAV_E1E5b": {"e1": "I/NAV", "e5b": "I/NAV"},
                "LNAV": {None: "L/NAV"},
                "D1/D2": {None: "D1/D2"},
                "NAV": {None: "NAV"},
        }
        
        signals = dict()
        
        if system:
            idx = self.dset.filter(system=system)
            nav_types = set(self.dset.nav_type[idx])
        else:
            nav_types = self.dset.unique("nav_type")
            
        for nav_type in nav_types:
            try:
                signals.update(nav_type_def[nav_type])
            except KeyError:
                log.error(f"GNSS navigation message {nav_type} is not defined.")
                
        return signals
    
      
    def _sort_by_satellite(self, dset: Union["Dataset", None]=None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Sort time and satellite fields of dataset by satellite order
    
        Returns:
            Tuple with ordered time, satellite and system array
        """
        dset = self.dset if dset is None else dset
        time = []
        satellite = []
        system = []
        for sat in sorted(self.dset.unique("satellite"), reverse=True):
            idx = self.dset.filter(satellite=sat)
            time.extend(self.dset.time.gps.datetime[idx])
            satellite.extend(self.dset.satellite[idx])
            system.extend(self.dset.system[idx])
    
        return np.array(time), np.array(satellite), np.array(system)
    
    
    def _sort_string_array(self, array: List[str]) -> List[str]:
        """Sort string array based on last two characters
    
        Args:
            array: String array
            
        Returns:
            Sorted string array
        """
        array.sort(key=lambda x: x[-2:3])
        return array