import grads
import numpy as np
import datetime
import os
grads_exe = 'grads'
ga = grads.GrADS(Bin=grads_exe,Window=False,Echo=False)

def gradstime2datetime(str):

 #Convert grads time to datetime
 date = datetime.datetime.strptime(str,'%HZ%d%b%Y')

 return date

def datetime2gradstime(date):

 #Convert datetime to grads time
 str = date.strftime('%HZ%d%b%Y')

 return str

def Create_Forcings(idate,fdate,dims):

 #Open files
 trmm_http = 'http://stream.princeton.edu:9090/dods/AFRICAN_WATER_CYCLE_MONITOR/3B42RT_BC/DAILY'
 gfsanl_http = 'http://stream.princeton.edu:9090/dods/AFRICAN_WATER_CYCLE_MONITOR/GFS_ANALYSIS_BC/DAILY'

 #Open access to grads data server
 ga("sdfopen %s" % trmm_http)
 ga("sdfopen %s" % gfsanl_http)

 #Set grads region
 ga("set lat %f %f" % (dims['minlat'],dims['maxlat']))
 ga("set lon %f %f" % (dims['minlon'],dims['maxlon']))

 #Open access to the output file
 forcing_file = 'Workspace/forcing_daily_%04d%02d%02d' % (idate.year,idate.month,idate.day)
 fp = open(forcing_file,'wb')

 #Determine time info
 nt = (fdate - idate).days + 1
 date = idate
 dt = datetime.timedelta(days=1)

 #Regrid and write variables to file
 for t in xrange(0,nt):

  timestamp = datetime2gradstime(date + t*dt)
  print timestamp
  ga("set time %s" % timestamp)
  prec = np.ma.getdata(ga.exp("prec.1")).astype(np.float32)
  tmax = np.ma.getdata(ga.exp("tmax.2-273.15")).astype(np.float32)
  tmin = np.ma.getdata(ga.exp("tmin.2-273.15")).astype(np.float32)
  wind = np.ma.getdata(ga.exp("wind.2")).astype(np.float32)

  #Append to the outgoing file
  prec.tofile(fp)
  tmax.tofile(fp)
  tmin.tofile(fp)
  wind.tofile(fp)

 #Close the outgoing file
 fp.close()
 ga("close 2")
 ga("close 1")

 #Prepare the control file
 forcing_ctl = 'Workspace/forcing_daily_%04d%02d%02d.ctl' % (idate.year,idate.month,idate.day)
 fp = open(forcing_ctl,'w')
 fp.write('dset ^forcing_daily_%04d%02d%02d\n' % (idate.year,idate.month,idate.day))
 fp.write('options template little_endian\n')
 fp.write('title forcing data\n')
 fp.write('undef -9.99e+08\n')
 fp.write('xdef %d  linear %f %f\n' % (dims['nlon'],dims['minlon'],dims['res']))
 fp.write('ydef %d  linear %f %f\n' % (dims['nlat'],dims['minlat'],dims['res']))
 fp.write('tdef %d linear 00Z%s 1dy\n' % (nt,idate.strftime('%d%b%Y')))
 fp.write('zdef 1 linear 1 1\n')
 fp.write('vars 4\n')
 fp.write('prec 0 99 mm\n')
 fp.write('tmax 0 99 c\n')
 fp.write('tmin 0 99 c\n')
 fp.write('wind 0 99 m/s\n')
 fp.write('endvars\n')
 fp.close()

 return

def Extract_Soils(dims):

 file = 'Input/soil_Africa_0.25deg_calibrated_final.txt'
 file_out = 'Workspace/soils_0.25deg.txt'
 #Read soils data line by line
 fp = open(file)
 fp_out = open(file_out,'w')
 for line in fp:
  lat = np.float(line.split()[2])
  lon = np.float(line.split()[3])
  if ((lon <= dims['maxlon']) & (lon >= dims['minlon']) & (lat <= dims['maxlat']) & (lat >= dims['minlat'])):
   fp_out.write(line)

 return

def Prepare_VIC_Global_Parameter_File(idate,fdate,dims):

 file = 'Workspace/Global_Parameter.txt'
 fp = open(file,'w')
 fdate = fdate + datetime.timedelta(days=1)

 #Write the VIC parameters to file

 # Define Global Parameters
 fp.write('NLAYER          3       # number of layers\n')
 fp.write('TIME_STEP       24       # model time step in hours (= 24 for water balance)\n')
 fp.write('STARTYEAR       %d      # year model simulation starts\n' % idate.year)
 fp.write('STARTMONTH      %d      # month model simulation starts\n' % idate.month)
 fp.write('STARTDAY        %d      # day model simulation starts\n' % idate.day)
 fp.write('STARTHOUR       0       # hour model simulation starts\n')
 fp.write('ENDYEAR         %d      # year model simulation ends\n' % fdate.year)
 fp.write('ENDMONTH        %d      # month model simulation ends\n' % fdate.month)
 fp.write('ENDDAY          %d      # day model simulation ends\n' % fdate.day)
 fp.write('SKIPYEAR        0       # no. of startup yrs to skip before writing output\n')
 fp.write('WIND_H          10.0    # height of wind speed measurement\n')
 fp.write('MEASURE_H       2.0     # height of humidity measurement\n')
 fp.write('NODES           10       # number of soil thermal nodes\n')
 fp.write('MAX_SNOW_TEMP   0.5     # maximum temperature at which snow can fall\n')
 fp.write('MIN_RAIN_TEMP   -0.5    # minimum temperature at which rain can fall\n')

 # Define Global Parameters
 fp.write('FULL_ENERGY     FALSE    # calculate full energy balance\n')
 #fp.write('FROZEN_SOIL     TRUE    # calculate frozen soils\n')
 fp.write('DIST_PRCP       TRUE        # use distributed precipitation\n')
 fp.write('COMPRESS        FALSE       # compress input and output files when done\n')
 fp.write('CORRPREC        FALSE       # correct precipitation for gauge undercatch\n')
 fp.write('GRID_DECIMAL    3           # number of decimals to use in gridded file names\n')
 fp.write('PRT_SNOW_BAND   FALSE   # print snow variables\n')
 fp.write('SNOW_STEP       1        # time step in hours to solve snow bands\n')
 fp.write('ROOT_ZONES      2               # number of root zones in veg parameter file\n')
 fp.write('BINARY_OUTPUT   TRUE   # default is ASCII, unless LDAS format\n')
 fp.write('MIN_WIND_SPEED  0.1     # minimum allowable wind speed\n')
 fp.write('PREC_EXPT       0.6             # fraction of grid cell receiving\n')
 fp.write('GRND_FLUX       FALSE # true for full energy, false for water balance\n')
 fp.write('QUICK_FLUX      FALSE   # true uses Liang (1999), false uses finite diff.\n')
 fp.write('NOFLUX          FALSE  # false uses const. T at damping depth\n')

 # Define (Meteorological) Forcing Files
 fp.write('FORCING1        Workspace/forcing_daily_\n')
 fp.write('N_TYPES         4\n')
 fp.write('FORCE_TYPE      TMAX    SIGNED  10\n')
 fp.write('FORCE_TYPE      TMIN    SIGNED  10\n')
 fp.write('FORCE_TYPE      WIND    UNSIGNED 10\n')
 fp.write('FORCE_TYPE      PREC    UNSIGNED 10\n')
 fp.write('FORCE_FORMAT    BINARY \n')
 fp.write('FORCE_ENDIAN    LITTLE      # LITTLE for PC arch., BIG for Sun or HP-UX\n')
 fp.write('FORCE_DT        24            # time step of two input met files\n')
 fp.write('FORCEYEAR   %d   # year model meteorological forcing files start\n' % idate.year)
 fp.write('FORCEMONTH   %d   # month model meteorological forcing files start\n' % idate.month)
 fp.write('FORCEDAY        %d                   # day meteorological forcing files start\n' % idate.day)
 fp.write('FORCEHOUR       00                  # hour meteorological forcing files start\n')

 # INPUT and OUTPUT TYPE from PRINCETON  (mpan and lluo)
 fp.write('INPUT_GRID_DEF %d %d %.3f %.3f %.3f %.3f\n' % (dims['nlon'],dims['nlat'],dims['minlon'],dims['minlat'],dims['res'],dims['res']))
 fp.write('OUTPUT_GRID_DEF %d %d %.3f %.3f %.3f %.3f\n' % (dims['nlon'],dims['nlat'],dims['minlon'],dims['minlat'],dims['res'],dims['res']))
 #fp.write('INPUT_STEP_PER_FILE     1        # number of timesteps per input file\n')
 fp.write('OUTPUT_PER_STEP TRUE # number of timesteps per output file\n')
 #fp.write('INPUT_GZIP              FALSE       # true if forcing file gzipped\n')
 #fp.write('OUTPUT_GZIP             FALSE        # true for writing gzipped output\n')
 fp.write('GRID_INPUT          TRUE #true for reading the input in GrADS binary, default is false\n')
 fp.write('GRID_OUTPUT         TRUE  #true for writing the output in GrADS binary,default is false\n')
 fp.write('REGULAR_OUTPUT      FALSE  #true for writing the output in standard version, default is false\n')

 # Define Input and Output Data Files
 fp.write('SNOW_BAND       Input/global_lai_0.25deg.txt\n')
 fp.write('ARC_SOIL        FALSE   # read soil parameters from ARC/INFO ASCII grids\n')
 fp.write('SOIL            Workspace/soils_0.25deg.txt\n')
 fp.write('VEGPARAM        Input/global_lai_0.25deg.txt\n')
 fp.write('VEGLIB          Input/veglib.dat\n')
 fp.write('GLOBAL_LAI      TRUE      # true if veg param file has monthly LAI\n')
 fp.write('RESULT_DIR      Output/\n')

 # Define the state file
 fp.write('STATENAME State/state\n')
 fp.write('STATEYEAR %d\n' % fdate.year)
 fp.write('STATEMONTH %d\n' % fdate.month)
 fp.write('STATEDAY %d\n' % fdate.day)
 file_state = 'State/state_%04d%02d%02d' % (idate.year,idate.month,idate.day)
 if os.path.exists(file_state) == True:
  fp.write('INIT_STATE %s\n' % file_state)

 #Close the file
 fp.close()

def Run_Model():

 os.system('./Executables/vicNl -g Workspace/Global_Parameter.txt')

 return
