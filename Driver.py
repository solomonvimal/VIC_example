import os
import VIC
import datetime

#Create the workspace
if os.path.exists('Workspace') == False:
 os.mkdir('Workspace')
os.system('rm Workspace/*')
if os.path.exists('State') == False:
 os.mkdir('State')
if os.path.exists('Output') == False:
 os.mkdir('Output')
os.system('rm Output/*')

#Define the dimensions
dims = {}
dims['minlat'] = 10.875000 #minlat -34.8750
dims['minlon'] = -10.875000 #minlon -18.8750
dims['nlat'] = 5
dims['nlon'] = 5
dims['res'] = 0.250 #DO NOT CHANGE
dims['maxlat'] = dims['minlat'] + dims['res']*(dims['nlat']-1)
dims['maxlon'] = dims['minlon'] + dims['res']*(dims['nlon']-1)

#Define time domain
idate = datetime.datetime(2011,1,1) #Year,month,day
fdate = datetime.datetime(2011,12,31) #Year,month,day

#Create the new soil file
print "Preparing the soils file"
VIC.Extract_Soils(dims)

#Extract the forcing data
print "Preparing the forcing data"
VIC.Create_Forcings(idate,fdate,dims)

#Update the global parameter file
print "Preparing the global paramter file"
VIC.Prepare_VIC_Global_Parameter_File(idate,fdate,dims)

#Run VIC
print "Running the model"
VIC.Run_Model()

