#- For the record (and future updates):
#- This code was used to generate tractor and sweep file subsets for testing.
#- The hardcoded paths are for NERSC, but you can swap out any
#- legacy survey data release path as needed.
#ADM as of DR4, we read in DR3 files and use desitarget.io 
#ADM to transform the format to the post-DR3 data model.
#ADM Should eventually update to read in DR5 files directly

from os.path import basename
import numpy as np
#from astropy.io import fits
from desitarget.cuts import apply_cuts
from desitarget.io import read_tractor
from desitarget.gaiamatch import find_gaia_files, read_gaia_file
import fitsio
from time import time


start = time()
tractordir = '/project/projectdirs/cosmo/data/legacysurvey/dr3.1/tractor/330'
#tractordir = '/data/legacysurvey/dr3.1/tractor/330/'
for brick in ['3301m002', '3301m007', '3303p000']:
    filepath = '{}/tractor-{}.fits'.format(tractordir, brick)
    desi_target = apply_cuts(filepath)[0]
    yes = np.where(desi_target != 0)[0]
    no = np.where(desi_target == 0)[0]
    keep = np.concatenate([yes[0:3], no[0:3]])
#    data, hdr = fits.getdata(filepath, header=True)
#    fits.writeto('t/'+basename(filepath), data[keep], header=hdr)
    data, hdr = read_tractor(filepath, header=True)
    #ADM the FRACDEV columns can contain some NaNs, which break testing
    wnan = np.where(data["FRACDEV"] != data["FRACDEV"])
    if len(wnan[0]) > 0:
        data["FRACDEV"][wnan] = 0.
    fitsio.write('t/'+basename(filepath), data[keep], header=hdr, clobber=True)
    print('made Tractor file for brick {}...t={:.2f}s'.format(brick,time()-start))

sweepdir = '/project/projectdirs/cosmo/data/legacysurvey/dr3.1/sweep/3.1'
gaiadir = '/project/projectdirs/cosmo/work/gaia/chunks-gaia-dr2-astrom'
#sweepdir = '/data/legacysurvey/dr2p/sweep/'
for radec in ['310m005-320p000', '320m005-330p000', '330m005-340p000']:
    filepath = '{}/sweep-{}.fits'.format(sweepdir, radec)
    desi_target = apply_cuts(filepath)[0]
    yes = np.where(desi_target != 0)[0]
    no = np.where(desi_target == 0)[0]
    keep = np.concatenate([yes[0:3], no[0:3]])
#    data, hdr = fits.getdata(filepath, header=True)
#    fits.writeto('t/'+basename(filepath), data[keep], header=hdr)
    data, hdr = read_tractor(filepath, header=True)
    fitsio.write('t/'+basename(filepath), data[keep], header=hdr, clobber=True)
    print('made sweeps file for range {}...t={:.2f}s'.format(radec,time()-start))
    
    #ADM also need to add files that are structured like the Gaia
    #ADM "chunks" files and that match to the sweeps files
    gaiafile = find_gaia_files(data,neighbors=False,gaiadir=gaiadir)
    gaiadata = read_gaia_file()
    



#ADM adding a file to make a mask for bright stars
#ADM this should go in its own directory /t2 (others are in t1)
filepath = '{}/sweep-{}.fits'.format(sweepdir, '190m005-200p000')
data, hdr = read_tractor(filepath, header=True)
keep = np.where(data["FLUX_Z"] > 100000)
fitsio.write('t2/'+basename(filepath), data[keep], header=hdr, clobber=True)
print('Done...t={:.2f}s'.format(time()-start))
