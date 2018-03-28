import os
import numpy as np
import time

# Options:
#   noutput
#   pCO2     (ubars)
#   pressure
#   flux
#   gravity
#   radius
#   year
#   restart
#   ncarbon
#   volcanCO2
#   wmax
#   nglacier
#   glacelim
#   sidday   (hours)
#   solday   (hours)
#   sidyear  (days)
#   solyear  (days)
#   rotspd
#   obliq
#   eccen
#   vernlon
#   radius
#   snowmax
#   soilh2o
#   naqua
#   script
#   extra
#   nfixorb
#   nwpd     (writes per day)
#   months   (runtime)
#   days     (runtime)
#   steps    (runtime)
#   timestep (minutes/timestep)
#   runyears
#   fixedlon (longitude of fixed substellar point)
#   source
#   notify

jobscript1 =("#!/bin/bash -l                                                  \n"+
            "#PBS -l nodes=1:ppn=8                                            \n"+
            "#PBS -q workq                                                    \n"+
            "#PBS -r n                                                        \n"+
            #"#PBS -m ae                                                       \n"+
            "#PBS -l walltime=48:00:00                                        \n")
jobscript2 =("# EVERYTHING ABOVE THIS COMMENT IS NECESSARY, SHOULD ONLY CHANGE"+
	    " nodes,ppn,walltime and my_job_name VALUES                       \n"+
            "cd $PBS_O_WORKDIR                                                \n"+
            "module unload gcc/4.9.1                                          \n"+
            "module unload python/2.7.9                                       \n"+
            "module load intel/intel-17                                       \n"+
            "module load openmpi/2.0.1-intel-17                               \n")


def edit_namelist(jid,filename,arg,val): 
  f=open("plasim/job"+jid+"/"+filename,"r")
  fnl=f.read().split('\n')
  f.close()
  found=False
  for l in range(1,len(fnl)-2):
    fnl[l]=fnl[l].split(' ')
    if '=' in fnl[l]:
      mode='EQ'
    else:
      mode='CM'
    if arg in fnl[l]:
      fnl[l]=['',arg,'','=','',str(val),'']
      found=True
    elif (arg+'=') in fnl[l]:
      fnl[l]=['',arg+'=','',str(val),'',',']
      found=True
    fnl[l]=' '.join(fnl[l])
  if not found:
    if mode=='EQ':
      fnl.insert(-3,' '+arg+' = '+val+' ')
    else:
      fnl.insert(-3,' '+arg+'= '+val+' ,')
  f=open("plasim/job"+jid+"/"+filename,"w")
  f.write('\n'.join(fnl))
  f.close() 


def prep(job):

  sig=job.name
  jid=job.home
  pid=job.pid
  args=job.args
  fields=job.fields
  
  if "source" in job.parameters:
    source = job.parameters["source"]
  else:
    source = "clean"

  
  print "Setting stuff for job "+sig+" in plasim/job"+jid+" which is task number "+pid
  print "Arguments are:",fields
  
  f=open("plasim/job"+jid+"/crawljob","w")
  
  emailtag = "#PBS -m ae \n"
  scriptfile = "run.sh"
  
  f.write(jobscript1+"#PBS -N "+sig+" \n"+emailtag+jobscript2+"./"+scriptfile+"\n")
  f.close()
  
  #PlaSim
  
  p0 = 1010670.0
  
  os.system("cp plasim/"+source+"/* plasim/job"+jid+"/")
  os.system("rm plasim/job"+jid+"/plasim_restart")
  os.system("cp plasim/"+scriptfile+" plasim/job"+jid+"/")
  
  for name in job.fields:
    val = job.parameters[name]
    found=False    
        
    if name=="noutput":
      edit_namelist(jid,"plasim_namelist","NOUTPUT",val)  
      found=True
      
    if name=="flux":
      edit_namelist(jid,"planet_namelist","GSOL0",val) 
      found=True
      
    if name=="pCO2":
      found=True
      gotpress=False
      if "pressure" in fields:
	p0 = float(job.parameters["pressure"])
	gotpress=True
      if not gotpress:
	p0 += float(val)
	p0 *= 1.0e-6
	edit_namelist(jid,"plasim_namelist","PSURF",str(p0*0.1))
	
      pCO2 = float(val)/(p0*1.0e6)*1.0e6 #ppmv
      edit_namelist(jid,"radmod_namelist","CO2",str(pCO2))      
      
    if name=="pressure":
      found=True
      
      p0 = float(val)*1.0e6
      edit_namelist(jid,"plasim_namelist","PSURF",str(p0*0.1))
       
    if name=="year": #In days
      found=True
      edit_namelist(jid,"plasim_namelist","N_DAYS_PER_YEAR",val) 
             
    if name=="sidyear": #In days
      found=True
      year = float(val)*24.0*3600.0
      val = str(year)
      edit_namelist(jid,"planet_namelist","SIDEREAL_YEAR",val) 
             
    if name=="solyear": #In days
      found=True
      year = float(val)*24.0*3600.0
      val = str(year)
      edit_namelist(jid,"planet_namelist","TROPICAL_YEAR",val) 
            
    if name=="sidday": #In hours
      found=True
      day = float(val)*3600.0
      val = str(day)
      edit_namelist(jid,"planet_namelist","SIDEREAL_DAY",val) 
             
    if name=="solday": #In hours
      found=True
      day = float(val)*3600.0
      val = str(day)
      edit_namelist(jid,"planet_namelist","SOLAR_DAY",val)
     
    if name=="rotspd":
      found=True
      edit_namelist(jid,"planet_namelist","ROTSPD",val)
      
    if name=="restart":
      found=True
      if val!="none":
	os.system("cp plasim/job"+jid+"/"+val+" plasim/job"+jid+"/plasim_restart")
      else:
	os.system("rm plasim/job"+jid+"/plasim_restart")
     
    if name=="gravity":
      found=True
      edit_namelist(jid,"planet_namelist","GA",val) 
       
    if name=="radius":
      found=True
      edit_namelist(jid,"planet_namelist","PLARAD",str(float(val)*6371220.0)) 
     
    if name=="eccen":
      found=True
      edit_namelist(jid,"planet_namelist","ECCEN",val) 
     
    if name=="obliq":
      found=True
      edit_namelist(jid,"planet_namelist","OBLIQ",val) 
       
    if name=="vernlon":
      found=True
      edit_namelist(jid,"planet_namelist","MVELP",val) 
           
    if name=="nfixorb":
      found=True
      edit_namelist(jid,"planet_namelist","NFIXORB",val) 
       
    if name=="nglacier":
      found=True
      edit_namelist(jid,"glacier_namelist","NGLACIER",val) 
      
    if name=="glacelim":
      found=True
      edit_namelist(jid,"glacier_namelist","GLACELIM",val) 
    
    if name=="ncarbon":
      found=True
      edit_namelist(jid,"carbonmod_namelist","NCARBON",val) 
      
    if name=="nsupply":
      found=True
      edit_namelist(jid,"carbonmod_namelist","NSUPPLY",val) 
      
    if name=="volcanCO2":
      found=True
      edit_namelist(jid,"carbonmod_namelist","VOLCANCO2",val) 
      
    if name=="wmax":
      found=True
      edit_namelist(jid,"carbonmod_namelist","WMAX",val) 
      
    if name=="snowmax":
      found=True
      edit_namelist(jid,"landmod_namelist","DSMAX",val) 
      
    if name=="soilh2o":
      found=True
      edit_namelist(jid,"landmod_namelist","WSMAX",val) 
      
    if name=="naqua":
      found=True
      edit_namelist(jid,"plasim_namelist","NAQUA",val)
      os.system("rm plasim/job"+jid+"/*.sra")
      
    if name=="nwpd":
      found=True
      edit_namelist(jid,"plasim_namelist","NWPD",val)
      
    if name=="months":
      found=True
      edit_namelist(jid,"plasim_namelist","N_RUN_MONTHS",val)
      
    if name=="days":
      found=True
      edit_namelist(jid,"plasim_namelist","N_RUN_DAYS",val)
      
    if name=="steps":
      found=True
      edit_namelist(jid,"plasim_namelist","N_RUN_STEPS",val)
      
    if name=="timestep":
      found=True
      edit_namelist(jid,"plasim_namelist","MPSTEP",val)
      
    if name=="script":
      found=True
      f=open("plasim/job"+jid+"/crawljob","w")
      f.write(jobscript1+"#PBS -N "+sig+" \n"+emailtag+jobscript2+"./"+val+"\n")
      f.close()
      scriptfile=val
      os.system("cp "+val+" plasim/job"+jid+"/")
      
    if name=="notify":
      found=True
      f=open("plasim/job"+jid+"/crawljob","w")
      emailtag = "#PBS -m "+val+" \n"
      f.write(jobscript1+"#PBS -N "+sig+" \n"+emailtag+jobscript2+"./"+scriptfile+"\n")
      f.close()
      
    if name=="extra":
      found=True
      os.system("cp -r "+val+" plasim/job"+jid+"/")
      
    if name=="runyears":
      found=True
      f=open("plasim/job"+jid+"/most_plasim_run","r")
      fnl=f.read().split('\n')
      f.close()
      for l in range(0,len(fnl)-2):
	line=fnl[l].split("=")
	if len(line)>0:
	  if line[0]=="YEARS":
	    fnl[l] = "YEARS="+val
      fnl='\n'.join(fnl)
      f=open("plasim/job"+jid+"/most_plasim_run","w")
      f.write(fnl)
      f.close()
      
    if name=="fixedlon":
      found=True
      edit_namelist(jid,"radmod_namelist","NFIXED","1")
      edit_namelist(jid,"radmod_namelist","FIXEDLON",val)
      
    if name=="source":
      found=True #We already took care of it
      
    if not found: #Catchall for options we didn't include
      found=True
      args = name.split('@')
      if len(args)>1:
        namelist=args[1]
        name=args[0]
        edit_namelist(jid,namelist,name,val)
      else:
        print "Unknown parameter! Submit unsupported parameters as KEY@NAMELIST in the header!"
      
  print "Arguments set"  
  
def submit(job):
  os.system("cd plasim/job"+job.home+" && qsub crawljob && cd ../../")
  time.sleep(1.0)
  tag = job.getID()
  job.write()