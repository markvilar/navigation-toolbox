import datetime
import numpy as np
import pandas as pd

#from mpl_toolkits.mplot3d import Axes3D

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
plt.style.use("./Styles/scientific.mplstyle")

from typing import Dict

import filters
import utilities
import utm

def main():
    # Script variables.
    save_figures = True
    show_figures = False
    save_csv = False
    figure_directory = "./Figures/Filtered/Dive-1/"
    output_directory = "./Output/Filtered/Dive-1/"

    # Load data.
    input_paths = {
		"ROV-HiPAP" : "./Data/Outlier-Filtered/Dive-1/ROV-HiPAP.csv"
	}
    data = utilities.load_csv_files(input_paths)
    data = data["ROV-HiPAP"]

    # Extract relevant data for filtering.
    hipap_time = data["Epoch"].to_numpy()
    hipap_data = np.stack([ data["UTM Northing"], data["UTM Easting"], \
        data["Depth"] ])
    hipap_sample_frequency = 1 / np.mean(hipap_time[1:] - hipap_time[0:-1])

    # --------------------------------------------------------------------------
    # ---- Filtering. ----------------------------------------------------------
    # --------------------------------------------------------------------------

    # Filter parameters.
    hipap_filter_order = 8
    hipap_filter_cutoff = 0.05
    hipap_filter_boundary = 10

    # Add end values.
    filtered_hipap_data = filters.add_boundary_values(hipap_data.copy(), \
        hipap_filter_boundary)

    # Filter data and account for time delay.
    filtered_hipap_data, filter_delay = filters.FIR_filter( \
        filtered_hipap_data, hipap_sample_frequency, hipap_filter_order, \
        hipap_filter_cutoff, axis=1)
    filtered_hipap_time = hipap_time - filter_delay

    print("Filter time delay: {0}".format(filter_delay))

    # Remove end values.
    filtered_hipap_data = filters.remove_boundary_values(filtered_hipap_data, \
        hipap_filter_boundary)

    filtered_data = pd.DataFrame()
    filtered_data["Epoch"] = filtered_hipap_time
    filtered_data["UTM Northing"] = filtered_hipap_data[0]
    filtered_data["UTM Easting"] = filtered_hipap_data[1]
    filtered_data["Depth"] = filtered_hipap_data[2]
    filtered_data["UTM Zone"] = data["UTM Zone"]
    filtered_data["UTM Hemisphere"] = data["UTM Hemisphere"]

    # --------------------------------------------------------------------------
    # ---- Latitude / longitude calculations -----------------------------------
    # --------------------------------------------------------------------------


    latitudes, longitudes = [], []
    for northing, easting, zone, hemisphere in \
        zip(filtered_data["UTM Northing"], filtered_data["UTM Easting"], \
            filtered_data["UTM Zone"], filtered_data["UTM Hemisphere"]):
        latitude, longitude = utm.UtmToLatLon(easting, northing, zone, \
            hemisphere)

        latitudes.append(latitude)
        longitudes.append(longitude)

    filtered_data["Latitude"] = np.array(latitudes, dtype=float)
    filtered_data["Longitude"] = np.array(longitudes, dtype=float)
    
    # --------------------------------------------------------------------------
    # ---- Datetime calculations. ----------------------------------------------
    # --------------------------------------------------------------------------

    times = []
    for epoch in filtered_data["Epoch"]:
        time = datetime.datetime.fromtimestamp(epoch).strftime("%Y:%m:%d:%H:%M:%S.%f")
        times.append(time)

    filtered_data["Datetime"] = np.array(times, dtype=str)

    # --------------------------------------------------------------------------
    # ---- Plotting. -----------------------------------------------------------
    # --------------------------------------------------------------------------
    
    # Northing plot.
    fig1, ax1 = plt.subplots(figsize=(4, 4))
    ax1.plot(data["Epoch"], data["UTM Northing"], \
        linewidth=1, label="Unfiltered")
    ax1.plot(filtered_data["Epoch"], filtered_data["UTM Northing"], \
        linewidth=1, label="Filtered")
    ax1.set_xlabel(r"Epoch, $t$ $[\text{s}]$")
    ax1.set_ylabel(r"UTM Northing, $[\text{m}]$")
    ax1.legend()

    # Easting plot.
    fig2, ax2 = plt.subplots(figsize=(4, 4))
    ax2.plot(data["Epoch"], data["UTM Easting"], \
        linewidth=1, label="Unfiltered")
    ax2.plot(filtered_data["Epoch"], filtered_data["UTM Easting"], \
        linewidth=1, label="Filtered")
    ax2.set_xlabel(r"Epoch, $t$ $[\text{s}]$")
    ax2.set_ylabel(r"UTM Easting, $[\text{m}]$")
    ax2.legend()

    # Depth plot.
    fig3, ax3 = plt.subplots(figsize=(4, 4))
    ax3.plot(data["Epoch"], data["Depth"], \
        linewidth=1, label="Unfiltered")
    ax3.plot(filtered_data["Epoch"], filtered_data["Depth"], \
        linewidth=1, label="Filtered")
    ax3.set_xlabel(r"Epoch, $t$ $[\text{s}]$")
    ax3.set_ylabel(r"Depth, $[\text{m}]$")
    ax3.legend()
    
    # Planar trajectory plot.
    fig4, ax4 = plt.subplots(figsize=(4, 4))
    ax4.plot(data["UTM Easting"], data["UTM Northing"], \
	    linewidth=1, label="Unfiltered") 
    ax4.plot(filtered_data["UTM Easting"], filtered_data["UTM Northing"], \
	    linewidth=1, label="Filtered") 
    ax4.set_xlabel(r"UTM Easting, $[\text{m}]$")
    ax4.set_ylabel(r"UTM Northing, $[\text{m}]$")
    ax4.legend()

    # 3D trajectory plot.
    fig5 = plt.figure(figsize=(6, 6))
    ax5 = fig5.add_subplot(111, projection='3d')
    ax5.plot(data["UTM Easting"], data["UTM Northing"], data["Depth"], \
        linewidth=1, label="Unfiltered")
    ax5.plot(filtered_data["UTM Easting"], filtered_data["UTM Northing"], \
        filtered_data["Depth"], linewidth=1, label="Filtered")
    ax5.invert_zaxis()
    ax5.set_xlabel(r"UTM Easting, $[\text{m}]$")
    ax5.set_ylabel(r"UTM Northing, $[\text{m}]$")
    ax5.set_zlabel(r"Depth, $[\text{m}]$")
    ax5.legend()

    if show_figures:
        plt.show()

    if save_figures:
        fig1.savefig(figure_directory + "ROV-HiPAP-Northing.png", dpi=300)
        fig2.savefig(figure_directory + "ROV-HiPAP-Easting.png", dpi=300)
        fig3.savefig(figure_directory + "ROV-HiPAP-Depth.png", dpi=300)
        fig4.savefig(figure_directory + "ROV-HiPAP-Planar-Trajectory.png", dpi=300)
        fig5.savefig(figure_directory + "ROV-HiPAP-Trajectory.png", dpi=300)

    if save_csv:
        filtered_data = pd.DataFrame(filtered_data)
        filtered_data.to_csv(output_directory + "ROV-HiPAP.csv", sep=',')

if __name__ == "__main__":
    main()