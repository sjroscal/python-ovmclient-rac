#!/usr/bin/python

from subprocess import call
import json
import sys
import os

with open('vm.json') as vm_file:
    ovmm_data = json.load(vm_file)

ovmmhost = ovmm_data["ovmm"]["ovmmhost"]
user = ovmm_data["ovmm"]["ovmmuser"]
pw = ovmm_data["ovmm"]["ovmmpw"]
host1 = ovmm_data["total_vms_to_clone"][0]["name"]
host2 = ovmm_data["total_vms_to_clone"][1]["name"]
host = host1 + ',' + host2
script_name = ovmm_data["deploy_rac"]["script_name"]
init_file = ovmm_data["deploy_rac"]["init_file"]
javahome = ovmm_data["java_home"]

os.environ['JAVA_HOME'] = javahome
#newjavahome = os.environ.get('JAVA_HOME')

call([script_name,'-u',user,'-p',pw,'-H',ovmmhost,'--insecure','-M',host,'-N',init_file])

#call(['/root/python/python-ovmclient-1.0.3/deploycluster3/deploycluster.py','-u','admin','-p','Welcome1','-H','ovmm-test.gdn.aus.osc','--insecure','-M','rac1,rac2','-N','/root/python/python-ovmclient-1.0.3/deploycluster3/netconfig.ini'])
