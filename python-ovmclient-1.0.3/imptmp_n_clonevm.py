#!/usr/bin/python

import json
import sys
import ovmclient
from ovmclient import constants
import pprint
from copy import copy

with open('vm.json') as vm_file:
    ovmm_data = json.load(vm_file)

client = ovmclient.Client(ovmm_data["ovmm"]["ovmmurl"], ovmm_data["ovmm"]["ovmmuser"], ovmm_data["ovmm"]["ovmmpw"])
repo_id = client.repositories.get_id_by_name(ovmm_data["repo"]["reponame"])
pool_id = client.server_pools.get_id_by_name(ovmm_data["pool"]["poolname"])

# Make sure the manager is running
client.managers.wait_for_manager_state()

#---------------------------------------------
#
# 1. import template
# 2. delete unused network from the template
# 3. assign two networks to the template (public, private)
#
#---------------------------------------------

# import new template
job = client.jobs.wait_for_job(client.repositories.importVm(repo_id, ovmm_data["template"]))

template_id = job['resultId']['value']
template_info = client.vms.get_by_id(template_id)


# Delete a vnic
for i in range(len(template_info["virtualNicIds"])):
    del_vnic_data = template_info["virtualNicIds"][i]["value"]
    client.jobs.wait_for_job(client.vm_virtual_nics(template_id).delete(del_vnic_data))


# Add a vnic
for i in range(len(ovmm_data["network"])):
    network_id = client.networks.get_id_by_name(ovmm_data["network"][i]["name"])
    add_vnic_data = {
        'networkId': network_id,
    }
    client.jobs.wait_for_job(client.vm_virtual_nics(template_id).create(add_vnic_data))


#---------------------------------------------
#
# 1. clone 2 vms from template
# 2. edit vm name for 2 vms
#
#---------------------------------------------

# Clone the template
#template_id = "0004fb0000140000a0974158d2c96d22"
#template_id = ovmm_data["vm_template"]["templateid"]
vm_id = []

for i in range(len(ovmm_data["total_vms_to_clone"])):
    job = client.jobs.wait_for_job(client.vms.clone(template_id,pool_id))

    # Update the VM, e.g. setting a new name
    vm_id.append(job['resultId']['value'])
    vm = client.vms.get_by_id(vm_id[i])

    vm['name'] = ovmm_data["total_vms_to_clone"][i]["name"]
    client.jobs.wait_for_job(client.vms.update(vm_id[i], vm))

#---------------------------------------------
#
# 1. create 5 vdisks
# 2. assign them to two vms
#
#---------------------------------------------

# Create vdisk
#vm_id = ['0004fb0000060000e7d83173a5973a91', '0004fb00000600005fdd361579dfbe2c']
vdisk_id = []
vdisk_info = copy(ovmm_data["vdisks"])

for i in range(ovmm_data["total_vdisks"]["no"]):
    vdisk_info["name"] = ovmm_data["vdisks"]["name"] + str(i)

    job = client.jobs.wait_for_job(client.repository_virtual_disks(repo_id).create(vdisk_info, sparse='true'))
    vdisk_id.append(job['resultId'])

  
# Map the virtual disk
for i in range(len(vm_id)):
    for cnt_disk in range(len(vdisk_id)):

        vm_disk_mapping_data = {
            'virtualDiskId': vdisk_id[cnt_disk],
            'diskWriteMode': constants.DISK_WRITE_MODE_READ_WRITE,
            'emulatedBlockDevice': False,
            'storageElementId': None,
            'diskTarget': cnt_disk+2
        }

        job = client.jobs.wait_for_job(client.vm_disk_mappings(vm_id[i]).create(vm_disk_mapping_data))


#---------------------------------------------
#
# 1. start vms
#
#---------------------------------------------

#for i in range(len(vm_id)):
#    client.jobs.wait_for_job(client.vms.start(vm_id[i]))
