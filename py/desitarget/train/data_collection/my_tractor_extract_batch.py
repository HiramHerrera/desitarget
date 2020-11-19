#!/usr/bin/env python

import os
import subprocess
import time
import datetime
from argparse import ArgumentParser
import numpy as np
import astropy.io.fits as fits
from astropy.io import ascii

# settings
STILTSCMD = 'java -jar -Xmx4096M /global/homes/c/cclaveau/software/topcat-full.jar -stilts'
tmpdir    = './tmpdir/'
pid       = str(os.getpid())
tmplog    = tmpdir+'tmp.log_'+pid
tmpasc    = tmpdir+'tmp.asc_'+pid

# reading arguments
parser = ArgumentParser()
parser.add_argument( '-n', '--nruns', type=int, default=1, metavar='NRUNS',
                     help = 'number of jobs running simultaneously', )
parser.add_argument( '-o', '--outfits', type=str, default=None, metavar='OUTFITS',
                     help = 'output fits' )
parser.add_argument( '-r', '--release', type=str, default=None, metavar='RELEASE',
                     help = 'release ("dr7","dr8s", "dr8n")' )
parser.add_argument( '-rd', '--radec', type=str, default='0,360,-90,90', metavar='RADEC',
                     help = 'ramin,ramax,decmin,decmax' )
parser.add_argument( '-l', '--listfile', type=str, default=None, metavar='LISTFILE',
                     help = 'file listing: col1=infits, col2=outfits' )
parser.add_argument( '-s', '--selcrit', type=str, default=None, metavar='SELCRIT',
                     help = 'selection criterion' )

# attributing variables
argnamelist = ['nruns', 'outfits', 'release', 'radec', 'listfile', 'selcrit']
arg = parser.parse_args()
for argname in argnamelist:
	exec( argname.upper()+' = arg.'+argname )
	exec( "print( argname.upper()+' = '+str(arg."+argname+") )" )

# RADEC
RAMIN,RAMAX,DECMIN,DECMAX = np.array(RADEC.split(',')).astype('float')

print()
print( '[start: '+datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")+']' )
print()

# if no LISTFILE is provided, we built it from the ramin,ramax,decmin,decmax infos
if (LISTFILE==None):
	LISTFILE = tmpdir+'tmp.list_'+pid
	if (RELEASE=='dr3'):
		SWEEPDIR = '/global/project/projectdirs/cosmo/data/legacysurvey/dr3/sweep/3.1'
	if (RELEASE=='dr4'):
		SWEEPDIR = '/global/project/projectdirs/cosmo/data/legacysurvey/dr4/sweep/4.0'
	if (RELEASE=='dr5'):
		SWEEPDIR = '/global/project/projectdirs/cosmo/data/legacysurvey/dr5/sweep/5.0'
	if (RELEASE=='dr6'):
		SWEEPDIR = '/global/project/projectdirs/cosmo/data/legacysurvey/dr6/sweep/6.0'
	if (RELEASE=='dr7'):
		SWEEPDIR = '/global/project/projectdirs/cosmo/data/legacysurvey/dr7/sweep/7.1'
	if(RELEASE=='dr8n'): #BASS/MzLS
		SWEEPDIR = '/global/project/projectdirs/cosmo/data/legacysurvey/dr8/north/sweep/8.0'
	if (RELEASE=='dr8s'): #DECaLS
		SWEEPDIR = '/global/project/projectdirs/cosmo/data/legacysurvey/dr8/south/sweep/8.0'
    if (RELEASE == 'dr9n'):
        SWEEPDIR = '/global/cscratch1/sd/adamyers/dr9m/north/sweep/'
    if (RELEASE == 'dr9s'):
        SWEEPDIR = '/global/cscratch1/sd/adamyers/dr9m/south/sweep/'

	SWEEPFILE = './'+RELEASE+'_sweep_meta.fits'
	# listing the sweeps in the considered region
	hdu = fits.open(SWEEPFILE)
	data= hdu[1].data

    data=fitsio.FITS(SWEEPFILE)[1][:]

	if (RAMIN>RAMAX):
		keep = ((data['ramax']>RAMIN) | (data['ramin']<RAMAX)) & (data['decmax']>DECMIN) & (data['decmin']<DECMAX)
	else:
		keep = (data['ramax']>RAMIN) & (data['ramin']<RAMAX) & (data['decmax']>DECMIN) & (data['decmin']<DECMAX)
	f = open(LISTFILE,'w')
	for name in data['sweepname'][keep]:
		f.write(SWEEPDIR+'/'+name+'\t'+tmpdir+'tmp.'+name+'_'+pid+'\n')
	f.close()

# reading LISTFILE
data = ascii.read( LISTFILE, delimiter='\t', Reader=ascii.NoHeader )
n    = len(data)

i = 0
while (i<=n-1):
	j = 0
	if (os.path.isfile(tmplog)):
		os.remove(tmplog)
	while ((j<NRUNS) & (i<=n-1)):
		INFITS_i  = data[i][0]
		OUTFITS_i = data[i][1]
		tmpstr    = ('python data_collection/my_tractor_extract.py '+
					'-i '+INFITS_i+' '+
					'-o '+OUTFITS_i+' '+
					'-r '+RELEASE+' '+
					'-rd '+RADEC+' '+
					'-s '+SELCRIT+' '+
					'-l '+tmplog+' &')
		print( 'i='+str(i)+' , j='+str(j)+' , '+tmpstr )
		subprocess.call(tmpstr, shell=True)
		j += 1
		i += 1
	# we wait for the runs to finish
	ndone = 0
	while (ndone!=j):
		if (os.path.isfile(tmplog)):
			tmpstr = "wc -l "+tmplog+" | awk '{print $1}'"
			p1     = subprocess.Popen(tmpstr, stdout=subprocess.PIPE, shell=True)
			ndone  = int(p1.communicate()[0].decode('ascii').split('\n')[0])
		print( 'i='+str(i)+'/'+str(n)+' , j='+str(j)+' , ndone='+str(ndone)+' ['+datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")+']' )
		time.sleep(10)

print()
print( '[jobs done: '+datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")+']' )
print()

# merging catalogues
subprocess.Popen("awk '{print $2}' "+LISTFILE+"> "+tmpasc, shell=True)
tmpstr = (STILTSCMD+' tcat ifmt=fits in=@'+tmpasc+' out='+OUTFITS+' ofmt=fits')
print(tmpstr)
subprocess.call(tmpstr, shell=True)

# cleaning
subprocess.call('rm '+tmplog+' '+tmpasc, shell=True)
for i in range(n):
	OUTFITS_i = data[i][1]
	subprocess.call('rm '+OUTFITS_i, shell=True)

print()
print( '[end: '+datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")+']' )
print()
