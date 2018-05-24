import numpy as np

if __name__=="__main__":
        header = "# PID MODEL JOBNAME STATUS NCORES QUEUE nfixorb eccen obliq vernlon lockedyear year naqua pCO2 pressure flux script extra notify alloutput keeprestart restart"

	tstr1 = " 0 8 greenq 1 0.0 0.0 90.0 10.0/0.0 36 1 363.96 " 
	tstr2 = "super-equil.sh super_relax.py a 0 1 locked_template"
	tstr3 = "super-equil.sh super_relax.py a 0 1 locked_frozen"

	ttxtf = open("tasks.crwl","r")
	ttxt = ttxtf.read()
	ttxtf.close()
        ttxt += header + "\n"
	n=1

        ps = 1.011
        
        for sol in np.arange(760.0,1251.0,10.0):
            ttxt+=(str(n)+" plasim jade"+str(n)+tstr1+str(ps)+" "+str(sol)
                    +" "+tstr2+'\n')
            n+=1
            ttxt+=(str(n)+" plasim cjade"+str(n)+tstr1+str(ps)+" "+str(sol)
                    +" "+tstr3+'\n')
            n+=1
            
	ttxtf = open("tasks.crwl","w")
	ttxtf.write(ttxt)
	ttxtf.close()