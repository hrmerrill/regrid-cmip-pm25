"""
Author: Hunter R. Merrill

This is a short script for regridding CMIP PM 2.5 data to a higher resolution (that of a given
satellite imagery dataset). It can be run from a terminal like this:

python regrid.py --input-dir path/to/inputs/ --output-file path/to/output.nc
"""

import argparse
from pathlib import Path

import numpy as np
import xarray as xr
from tqdm import tqdm


def regrid_data(input_data: xr.DataArray, target_data: xr.DataArray) -> xr.Dataset:
    """
    Regrid the input data.

    Parameters
    ----------
    input_data: xr.DataArray
        The xarray DataArray to be regridded. It must have coordinates "time", "longitude",
        and "latitude".
    target_data: xr.DataArray
        An xarray DataArray containing the grid to which input_data should be regridded. It
        should have the same coordinates as input_data.

    Returns
    -------
    xr.Dataset
        The xarray Dataset containing the input_data regridded to the target_data grid.
    """

    # get the target grid from any single date (I'll just grab the first date)
    first_date_data = target_data.sel(time=target_data.time[0])
    target_latitude = first_date_data.latitude
    target_longitude = first_date_data.longitude

    # create an empty array to store the regridded input data
    regridded_array = np.empty(
        shape=(len(target_latitude), len(target_longitude), len(input_data.time))
    )

    # loop over dates and interpolate to the target grid
    for i, time in tqdm(enumerate(input_data.time), desc="Regridding", total=len(input_data.time)):
        original = input_data.sel(time=time)
        regridded = original.interp(latitude=target_latitude, longitude=target_longitude)

        # By default, the input data is regridded everywhere. In the case that the target
        # data is masked, we also want to mask the regridded input data to save space.
        # A quick hacky way to get the mask is to add zero times the target data (the
        # addition results in NaNs where the target is NaN, or regridded data elsewhere).
        regridded = regridded + 0 * first_date_data.data.squeeze()
        regridded_array[..., i] = regridded

    # create the dataset
    regridded_data = xr.Dataset(
        data_vars={
            input_data.name
            + "_REGRIDDED": (
                ["latitude", "longitude", "time"],
                regridded_array,
            ),
        },
        coords={
            "latitude": target_data.coords["latitude"],
            "longitude": target_data.coords["longitude"],
            "time": input_data.coords["time"],
        },
    )
    return regridded_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="directory containing required input files; e.g., 'Downloads/'. The directory "
        "should contain both 'cmip_annual_mean_output.nc' and 'vand_annual_mean_output.nc'.",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        required=True,
        help="Path to store the output file; e.g., 'Downloads/regridded_cmip.nc'.",
    )
    args = parser.parse_args()

    # open both modeled and satellite datasets
    print("Reading input data.")
    model_data = xr.open_dataset(str(Path(args.input_dir) / "cmip_annual_mean_output.nc"))
    satellite_data = xr.open_dataset(str(Path(args.input_dir) / "vand_annual_mean_output.nc"))

    regridded_model_data = regrid_data(
        input_data=model_data["PM25_CMIP"], target_data=satellite_data["PM25_VAND"]
    )

    print(f"Saving regridded data to {Path(args.output_file)}.")
    regridded_model_data.to_netcdf(args.output_file)
