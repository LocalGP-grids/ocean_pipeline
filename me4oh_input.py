import glob, os, sys, pandas, xarray, argparse, numpy, datetime
from helpers import helpers

parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", type=str, help="directory with Argovis JSON")
parser.add_argument("--year", type=int, help="year to consider")
parser.add_argument("--month", type=int, help="month to consider")
parser.add_argument("--output_file", type=str, help="name of output file, with path.")
args = parser.parse_args()

fn = f'{args.data_dir}/ofam3-jra55.all.EN.4.1.1.f.profiles.g10.{args.year}{args.month:02d}.update.nc'
xar = xarray.open_dataset(fn)

lons = xar['ts_lon'].to_dict()['data']
lats = xar['ts_lat'].to_dict()['data']
ymd = xar['en4_ymd'].to_dict()['data']
dn = [helpers.datetime_to_datenum(datetime.datetime(*[int(x) for x in ymd_i])) for ymd_i in ymd]
temp = xar['temp'].to_dict()['data']
salt = xar['salt'].to_dict()['data']
level = xar['ts_z'].to_dict()['data']
eta_t = xar['eta_t'].to_dict()['data']
sst = xar['sst'].to_dict()['data']
dohc = xar['dohc'].to_dict()['data']

# following schema of argonc output for pipeline harmony
df = pandas.DataFrame({
    'float': [-1] * len(lons),
    'cycle': ['xxxx'] * len(lons),
    'juld': dn,
    'longitude': lons,
    'latitude': lats,
    'temperature': temp,
    'temperature_qc': [[-1] * len(row) for row in temp],
    'salinity': salt,
    'salinity_qc': [[-1] * len(row) for row in salt],
    'pressure': [level]*len(temp), # yes its redundant, but pack it like a normal profile so downstream stages get what they expect
    'pressure_qc': [[-1] * len(row) for row in temp],
    'eta_t': eta_t,
    'sst': sst,
    'dohc': dohc,
    'filetype': '',
    'flag': [0] * len(lons),
})

df.to_parquet(args.output_file, engine='pyarrow')
