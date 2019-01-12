# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 16:05:05 2018

@author: ud
"""
import subprocess
process = subprocess.Popen("ifconfig | grep enp2s0 | awk '{print $1}'", shell =True, stdout =subprocess.PIPE)
try:
    outs, errs = process.communicate()
    print (outs.strip())
except:
    process.kill()
    outs, errs = process.communicate()
    print(errs)
ifconfig = subprocess.Popen("ifconfig| grep -c 'inet addr'", shell =True, stdout =subprocess.PIPE)
try:
    out ,err =ifconfig.communicate()
    print(out.strip())
except:
    process.kill()
    out, err =process.communicate()
    print(err.strip())