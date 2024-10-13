# Regridding CMIP PM2.5 Data

**Author:** Hunter Merrill

This repo contains a short python script for regridding modeled PM 2.5 data to the grid of a satellite imagery dataset.

## Usage

First, you'll need `python` (at least version 3.8) and to install the required packages:

```bash
pip install -U xarray dask netCDF4 scipy numpy tqdm
```

Then you need to clone this repo:

```bash
# Change to the directory where you keep cloned repositories. E.g., ~/dev/repos/
cd path/to/repos/

# Clone this repository
git clone git@github.com:hrmerrill/regrid-cmip-pm25.git

# Change directories to the root of this repo
cd regrid-cmip-pm25
```

The input NetCDF datasets `cmip_annual_mean_output.nc` and `vand_annual_mean_output.nc` should be in some directory. Mine are in my `~/Downloads/` directory. You'll also need to decide where to save the output file; when I tested this, I used `~/Downloads/output.nc`. Now you can run this script with the following:

```bash
python regrid.py --input-dir path/to/inputs/ --output-file path/to/output.nc

## Just to be explicit, this is what I ran:
# python regrid.py --input-dir ~/Downloads/ --output-file ~/Downloads/output.nc
```