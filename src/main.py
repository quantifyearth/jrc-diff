# Analysis code for the exported directory from the gee.js
# script, this will create some summary statistics and charts
# about the differences between the different JRC "versions".
import os
import sys
import csv
from glob import glob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def analyse(luc_dir, out_dir):
    files = glob("*.csv", root_dir=luc_dir)
    years = list(set([x.split("_")[2] for x in files]))
    countries = list(set([os.path.splitext(x.split("_")[3])[0] for x in files]))

    data = {}
    for country in countries:
        if data.get(country) is None:
            data[country] = {}
        for year in years:
            data[country][year] = {}
            path = os.path.join(luc_dir, "jrc_counts_" + year + "_" + country + ".csv")
            df = pd.read_csv(path).drop(columns=["system:index", ".geo"])

            # TODO: A bit fragile if we ever add more column names that don't
            # get dropped
            luc_years = [x for x in df.columns if x != "LUC"]
            for ly in luc_years:
                total = df[ly].sum()
                # TODO: Check this preserves LUC ordering!
                proportions = (df[ly] / total).to_list()
                data[country][year][ly] = np.array(proportions)

    # Numbers of pairs of bars you want
    years = [x for x in range(1990, 2022)]
    N = len(years)
    country = "Indonesia"
    data_year = "2022"

    undisturbed = [data[country][data_year][f"Dec{x}"][0] for x in years]
    degraded = [data[country][data_year][f"Dec{x}"][1] for x in years]
    deforested = [data[country][data_year][f"Dec{x}"][2] for x in years]
    regrowth = [data[country][data_year][f"Dec{x}"][3] for x in years]
    water = [data[country][data_year][f"Dec{x}"][4] for x in years]
    other = [data[country][data_year][f"Dec{x}"][5] for x in years]

    # Position of bars on x-axis
    ind = np.arange(N)

    # Figure size
    plt.figure(figsize=(14, 8))

    # Width of a bar
    width = 1.0 / 7

    # Plotting
    plt.bar(ind, undisturbed, width, label="Undisturbed", color=rgb_to_hex(0, 90, 0))
    plt.bar(
        ind + width, degraded, width, label="Degraded", color=rgb_to_hex(100, 155, 35)
    )
    plt.bar(
        ind + 2 * width,
        deforested,
        width,
        label="Deforested",
        color=rgb_to_hex(255, 135, 15),
    )
    plt.bar(
        ind + 3 * width,
        regrowth,
        width,
        label="Regrowth",
        color=rgb_to_hex(210, 250, 60),
    )
    plt.bar(ind + 4 * width, water, width, label="Water", color=rgb_to_hex(0, 140, 190))
    plt.bar(
        ind + 5 * width, other, width, label="Other", color=rgb_to_hex(200, 200, 200)
    )

    plt.xlabel("Year")
    plt.ylabel("Proportional Land Use Class")
    plt.title(f"Changes in Proportional LUC in {country} (JRC from {data_year})")

    plt.xticks(ind + 5 * width / 2, years, rotation=25)

    plt.legend(loc="best")

    os.makedirs(out_dir, exist_ok=True)

    plt.savefig(os.path.join(out_dir, f"./{country}-prop-luc.png"))

    # Find differences across some years
    with open(
        os.path.join(out_dir, f"./{country}-prop-diff.csv"), "w", newline=""
    ) as csvfile:
        diffwriter = csv.writer(
            csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        diffwriter.writerow(
            [
                "year",
                "undisturbed",
                "degraded",
                "deforested",
                "regrowth",
                "water",
                "other",
            ]
        )
        for year in years:
            diff = (
                data[country]["2022"][f"Dec{year}"]
                - data[country]["2021"][f"Dec{year}"]
            ) * 100
            diff = list(np.around(diff, decimals=6))
            diffwriter.writerow([year] + diff)


def main():
    try:
        luc_directory = sys.argv[1]
        out_directory = sys.argv[2]
    except IndexError:
        print(f"Usage: {sys.argv[0]} LUC_DATA_DIRECTORY OUT_DIRECTORY")
        sys.exit(1)

    analyse(luc_directory, out_directory)


if __name__ == "__main__":
    main()
