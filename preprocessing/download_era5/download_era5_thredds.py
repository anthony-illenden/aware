import xarray as xr
import pandas as pd
import os
import numpy as np
import metpy.calc as mpcalc
from siphon.catalog import TDSCatalog
from metpy.units import units

lsm_file = "/cw3e/mead/projects/csg101/aillenden/preprocessing/lsm/era5_landmask.nc"
ds_lsm = xr.open_dataset(lsm_file)

def load_datasets(year, month, start_day, start_hour=0, end_day=None, end_hour=23):
    if end_day is None:
        end_day = start_day

    last_day_of_month = pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(1)
    last_day_str = f"{last_day_of_month.day:02d}"

    year_month = f'{year}{month:02d}'
    start_time = f'{year}{month:02d}{start_day:02d}{start_hour:02d}'
    end_time = f'{year}{month:02d}{end_day:02d}{end_hour:02d}'

    urls = {
        'temperature_pl': f'https://thredds.rda.ucar.edu/thredds/catalog/files/g/d633000/e5.oper.an.pl/{year_month}/catalog.html?dataset=files/g/d633000/e5.oper.an.pl/{year_month}/e5.oper.an.pl.128_130_t.ll025sc.{start_time}_{end_time}.nc',
        'humidity_pl': f'https://thredds.rda.ucar.edu/thredds/catalog/files/g/d633000/e5.oper.an.pl/{year_month}/catalog.html?dataset=files/g/d633000/e5.oper.an.pl/{year_month}/e5.oper.an.pl.128_133_q.ll025sc.{start_time}_{end_time}.nc',
        'v_wind_pl': f'https://thredds.rda.ucar.edu/thredds/catalog/files/g/d633000/e5.oper.an.pl/{year_month}/catalog.html?dataset=files/g/d633000/e5.oper.an.pl/{year_month}/e5.oper.an.pl.128_132_v.ll025uv.{start_time}_{end_time}.nc',
        'u_wind_pl': f'https://thredds.rda.ucar.edu/thredds/catalog/files/g/d633000/e5.oper.an.pl/{year_month}/catalog.html?dataset=files/g/d633000/e5.oper.an.pl/{year_month}/e5.oper.an.pl.128_131_u.ll025uv.{start_time}_{end_time}.nc',
        'mslp_sfc': f'https://thredds.rda.ucar.edu/thredds/catalog/files/g/d633000/e5.oper.an.sfc/{year_month}/catalog.html?dataset=files/g/d633000/e5.oper.an.sfc/{year_month}/e5.oper.an.sfc.128_151_msl.ll025sc.{year_month}0100_{year_month}{last_day_str}23.nc'
    }

    datasets = {}

    for var, url in urls.items():
        try:
            tds_catalog = TDSCatalog(url)
            ds_url = tds_catalog.datasets[0].access_urls['OPENDAP']
            ds = xr.open_dataset(ds_url)
            datasets[var] = ds
            print(f"Successfully loaded {var}")
        except Exception as e:
            print(f"Error loading {var}: {e}")

    ds_pl, ds_sfc = None, None

    try:
        ds_pl = xr.merge([datasets['temperature_pl'], datasets['humidity_pl'], 
                        datasets['v_wind_pl'], datasets['u_wind_pl']])
        print("Successfully merged pressure level datasets")
    except KeyError as e:
        print(f"Error merging pressure level datasets: {e}")

    try:
        ds_sfc = xr.merge([datasets['mslp_sfc']])
        print("Successfully merged surface datasets")
    except KeyError as e:
        print(f"Error merging surface datasets: {e}")

    try:
        if ds_pl is not None and ds_sfc is not None:
            first_time_pl, last_time_pl = ds_pl['time'].min().values, ds_pl['time'].max().values
            ds_sfc = ds_sfc.sel(time=slice(first_time_pl, last_time_pl))
    except KeyError as e:
        print(f"Error accessing 'time' in the datasets: {e}")
    except Exception as e:
        print(f"An error occurred during slicing: {e}")
        
    return ds_pl, ds_sfc

def merge_ds(ds_pl, ds_sfc):
    return xr.merge([ds_pl, ds_sfc])

def calc_vars(ds, level, output_dir):
    g = 9.81  # units: m/s2
    level_hpa = level * units.hPa
    selected_hours = [0, 3, 6, 9, 12, 15, 18, 21]
    time_list = ds['time'].sel(time=ds['time'].dt.hour.isin(selected_hours))

    for time in time_list:
        try:
            u_sliced = ds['U'].sel(time=time, level=slice(300, 1000))
            v_sliced = ds['V'].sel(time=time, level=slice(300, 1000))
            q_sliced = ds['Q'].sel(time=time, level=slice(300, 1000))
            t_sliced = ds['T'].sel(time=time, level=slice(300, 1000))
            mslp = ds['MSL'].sel(time=time) / 100

            u_lev = u_sliced.sel(level=level_hpa)
            v_lev = v_sliced.sel(level=level_hpa)
            q_lev = q_sliced.sel(level=level_hpa)
            t_lev = t_sliced.sel(level=level_hpa)
            p_lev = level * units.hPa

            pressure_levels = u_sliced['level'][::-1] * 100

            u_ivt = -1 / g * np.trapz(u_sliced * q_sliced, pressure_levels, axis=0)
            v_ivt = -1 / g * np.trapz(v_sliced * q_sliced, pressure_levels, axis=0)

            ivt = np.sqrt(u_ivt**2 + v_ivt**2)
            ivt_da = xr.DataArray(ivt, dims=['latitude', 'longitude'],
                                  coords={'latitude': u_sliced['latitude'], 'longitude': u_sliced['longitude']})
            ivt_da.name = 'IVT'

            td_lev = mpcalc.dewpoint_from_specific_humidity(p_lev, t_lev, q_lev)
            theta_e = mpcalc.equivalent_potential_temperature(p_lev, t_lev, td_lev)

            dtheta_e_dx, dtheta_e_dy = mpcalc.geospatial_gradient(theta_e)
            theta_e_gradient = np.sqrt(dtheta_e_dx**2 + dtheta_e_dy**2) * 1e5
            theta_e_gradient_da = xr.DataArray(theta_e_gradient, dims=['latitude', 'longitude'],
                                              coords={'latitude': u_sliced['latitude'], 'longitude': u_sliced['longitude']})
            theta_e_gradient_da.name = 'thetae_grad'

            vort_lev = mpcalc.vorticity(u_lev, v_lev) * 1e5

            ds = ds.assign({
                'MSLP': mslp,
                'IVT': ivt_da,
                'thetae_grad': theta_e_gradient_da,
                'vort_925': vort_lev})

            final_variables = ['MSLP', 'IVT', 'thetae_grad', 'vort_925']
            ds_final = ds[final_variables]

            formatted_time = pd.to_datetime(time.values)
            ds_final = ds_final.expand_dims(time=[formatted_time])
            time_str = formatted_time.strftime('%Y%m%d_%H')

            ds_final_filtered = ds_final.where(ds_lsm['LSM'] <= 0)

            save_ds(ds_final_filtered, output_dir, time_str)
            print(f"Processed time step {time_str}!")

        except Exception as e:
            print(f"Error processing time step: {e}")
            continue

def save_ds(ds, output_dir, time_str):
    if ds is None:
        print(f"Dataset is None for time {time_str}. Skipping save.")
        return
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = os.path.join(output_dir, f"sliced_{time_str}.nc")
    ds = ds.sortby('latitude')
    ds.to_netcdf(output_file)

def main(start_date, end_date, output_dir='', level=925):
    print("="*50)
    print("Script is running...")
    print("="*50)

    dates = pd.date_range(start=start_date, end=end_date, freq="D")

    for date in dates:
        year, month, day = date.year, date.month, date.day
        print(f"Processing data for {year}-{month:02d}-{day:02d}...")

        try:
            ds_pl, ds_sfc = load_datasets(year, month, start_day=day, end_day=day)
            if ds_pl is None:
                print(f"Skipping {date.strftime('%Y-%m-%d')} due to missing datasets.")
                continue

            ds_merged = merge_ds(ds_pl, ds_sfc) if ds_sfc is not None else ds_pl
            calc_vars(ds_merged, level, output_dir)

        except Exception as e:
            print(f"Error processing {date.strftime('%Y-%m-%d')}: {e}")
            continue

    print("="*50)
    print("Script is complete!")
    print("="*50)

if __name__ == '__main__':
    start_date = "2014-10-01"
    end_date = "2015-09-30" #"2015-09-30"
    level = 925
    output_dir = "/cw3e/mead/projects/csg101/aillenden/era5_data/wy2015"

    main(start_date, end_date, output_dir, level)
