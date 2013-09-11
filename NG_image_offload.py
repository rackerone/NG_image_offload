#!/usr/bin/python
# -*- coding: utf-8 -*-
#Copyright 2013 Aaron Smith

#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

#http://code.activestate.com/recipes/576810-copy-files-over-ssh-using-paramiko/
#If you need to do this in a non-blocking way, you will have to use the channel object directly. You can then
#watch for both stdout and stderr with channel.recv_ready() and channel.recv_stderr_ready(), or use select.select.

###+_+_+_+_+_+_+_+_+_+_++_+_+###
#Save Next Generation server images to remote location like cloud files.  Allow download locally and restore
"""
need to:
-add a check of the SOURCE server to see which datacenter it lives in....this is necessary because out dd tranfer of over service net.
-verify download and install of packages necessary to make this work
-check os of SOURCE....need to adjust install commands for each os.  Ubuntu source require apt-get update, then apt-get -y install {packages}
-For significant speed improvement use netcat for transfer but lose security of encryption.  I want to experiment with encrypting image data on the fly
  ....possibly hmac or similar to hash each block of data before sending over wire.

"""

import os
import re
from time import sleep
import time
import subprocess  #<---use to execute local filesystem commands
import pexpect    #<---currently not used in this script
import sys
#Paramiko will not be installed by default so most people will need to install it
try:
  import paramiko  #<---this is used to create SSH connections
except ImportError as e:
  print e
  print "Please install paramiko for SSH support!\n\tpip install paramiko\n\tOR\n\teasy_install paramiko\n\n"
  print "Retry this script after installation."
  sys.exit(1)
#Pyrax may not be installed either
try:
  import pyrax
except ImportError as e:
  print e
  print "Please install pyrax for rackspace cloud support!\n\tpip install pyrax\n\tOR\n\teasy_install pyrax\n\n"
  print "Retry this script after installation."
  sys.exit(1)
#Install for debugging/troubleshooting purposes
try:
  import cgitb   #<---this provides detailed tracebacks on error
  import pdb   #<---python debugger - insert pdb.set_trace()
except Exception as e:
  print "Unable to import debugging tools.  These are not necessary but if you need them please check debug message below and install appropriate library(s)..."
  print e

### Uncomment to enable detailed tracebacks ###
#cgitb.enable(format='text')

### Clear the shell/terminal screen before executing the rest of the script###
os.system('cls' if os.name=='nt' else 'clear')

#### SETUP SOME GLOBAL VARIABLES ###
print "Setting up gloabal variables..."
CREDS_FILE = os.path.expanduser("~/.rackspace_cloud_credentials")    #<----set credentials file used to authenticate to Rackspace cloud
REGIONS = ["DFW", "ORD", "LON"]    #<----these are the currently supported regions
SOURCE_UUID = ''     #<----this is will ultimately hold the uuid of the source server we want to image
OFFLOAD_UUID = ''    #<----this is the uuid of the OFFLOAD server that be the destination for our NG image
SATA_VOLUME = ''    #<---this will hold the size of the sata volume to create
SPACER = "\n\n"   #<---this will provide a blank two-line seperator for formatting purposes
print "Done!"
print "============================"


### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
######################################################## FUNCTIONS #########################################################
### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#START FUNCTIONS  ---->

def now():
  """Use to timestamp current time."""
  return time.time()

#not implemented yet
def initiate_SSH(server):
  """This will initiate an SSH connection. """
  ssh = paramiko.SSHClient()
  try:
    ssh.load_system_host_keys()
  except:
    pass
  try:
    ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
  except:
    pass
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  MY_RSAKEY_FILE = os.path.expanduser("~/.ssh/id_rsa.pub")
  ssh.connect(server, username='root', key_filename=MY_RSAKEY_FILE, timeout=60)
  invokedShell = ssh.invoke_shell()
  transport = ssh.get_transport()  #not using this currently but get access to channels this way

#not implemented yet
def executeMe(cmd, target):
  """Send cmd string to remote server and execute.  This function will block until all remote processes have been executed
  and successfully returned.  We will need to pass the argument (target) also...this will be the target remote server IP address.
  
  --arguments--
  cmd :: This is the command we want to execute as type String
  target :: This is the IP address of the remote server we want to execute cmd against
  
  external Dep = paramiko
  internal function Dep = initiate_SSH()
  """
  print "Initiating connection to remote server %s", target
  initiate_SSH(target)
  print "Done!"
  print "Sending command '%s' to remote server %s", (cmd, target)
  stdin, stdout, stderr = ssh.exec_command(cmd)
  channel_out = stdout.channel
  print "--->Current clock time: ", now()
  print "--->Checking channel exit ready status..."
  print "--->exit status ready ===>", channel_out.exit_status_ready()
  print "--"
  print "--->Checking recv exit status..."
  status = channel_out.recv_exit_status()
  print "--->recv exit status.. ===>", status
  print "--"
  print "--->Checking channel exit ready status..."
  print "--->exit status ready ===>", channel_out.exit_status_ready()
  print "--"
  print "--->Receiving response from server..."
  print "--"
  for line in stdout.readlines():
    print line
  print ""
  for line in stderr.readlines():
    print line

#not implemented yet
def checkProgress():
    """Use to check the progress of ssh transfer of dd image to remote buffer/imageoffload server"""
    pass

#END FUNCTIONS  <-----  ^^
### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
############################################## Authenticating to Rackspace cloud ###########################################
### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###

### Authenticate to Rackspace Cloud ###
print "Authenticating to Rackspace Cloud..."
#Set identity type
pyrax.set_setting('identity_type', 'rackspace')
#Set credentials file used for auth
pyrax.set_credential_file(CREDS_FILE)
#Set default region
print "Setting up default region of DFW..."
pyrax.set_default_region("DFW") 
print "Done!"
print "============================"

### Create connections to different regions and gather list of servers ###
print "Establishing connections to DFW and ORD and compiling list of servers.  This may take a few minutes..."
#Create generic cloud server object
cs = pyrax.cloudservers
#Connect to DFW cloud servers and authenticate
cs_dfw_conn = pyrax.connect_to_cloudservers(region="DFW")
#Save a list of DFW cloud servers
cs_dfw_servers = cs_dfw_conn.servers.list()
#Connect to ORD cloud servers and authenticate
cs_ord_conn = pyrax.connect_to_cloudservers(region="ORD")
#Save a list of ORD servers
cs_ord_servers = cs_ord_conn.servers.list()
#Set up a list of all servers from each region combined into a single list
all_servers = cs_dfw_servers + cs_ord_servers
print "Done!"
print "============================"

### Server UUID list ###
print "Setting up list of server UUIDs used to validate user supplied SOURCE UUID is an actual valid UUID..."
#Create a list of server UUID's that we will use to verify that user supplied source UUID is valid.  
server_UUIDs = [server.id for server in all_servers]
print "Done!"
print "============================"



### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
######################################## Get User Input.  Choose from menu which server to image ##############################
### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###

#Clear the screen and present our servers to choose from 
os.system('cls' if os.name=='nt' else 'clear')

#Initialize public/private ip variables
SOURCE_public_ip = ''
SOURCE_private_ip = ''
print "\n\nCHOOSE FROM THE FOLLOWING LIST OF SERVERS.  Please copy the UUID and enter below as the value for 'SOURCE Server UUID'\n"
for server in all_servers:
  SOURCE_public_ip = server.accessIPv4
  SOURCE_private_ip = server.networks['private'][0]
  print "Server Name: %s \tServer UUID: %s \t" % (server.name, server.id)
print "============================"

#We need to wait for user input here (should be UUID).  We will compare this UUID to list of known UUIDs.  If not present we re-prompt for user input
while True:
  SOURCE_UUID = raw_input("Enter SOURCE UUID (this is the ID of the server you wish to image): ")   #<---wait for user input
  if SOURCE_UUID not in server_UUIDs:  #<---is SOURCE_UUID in our list of uuids?
    print "Error!  UUID entered did not match any of your server UUIDs.\n\n"
    continue     #<----if the SOURCE_UUID is not in our list then continue back at top of loop and wait for input
  break   #<---if SOURCE_UUID was in the list then break out of the loop
print "\n\n"

#Instantiate server object using the UUID of the server we chose above (SOURCE server)
my_source = cs.servers.get(SOURCE_UUID)

#Echo choice to user
print "You chose server '%s' with UUID '%s'\n\n" % (my_source.name, my_source.id)

#Calculate sata volume size
print "Calculating the amount of SATA block storage needed to accomodate this request based on SOURCE server chosen..."
#This dictionary is organized so that each flavor key has a 'sata volume size in GB' as the value....we compare our SOURCE server
#to this dictionary and get the appropriate size sata volume to accomodate the entire allocated disk on SOURCE server.
sata_cbs_dict = {2:100, 3:100, 4:100, 5:200, 6:400, 7:700, 8:1200}
source_flavor = my_source.flavor['id']  #<--determine flavor so we can attach the appropriate size block storage on temp server
source_disk = cs.flavors.get(source_flavor).disk #<---determine allocated disk size for SOURCE server.
SATA_VOLUME = [value for key,value in sata_cbs_dict.items() if key is int(source_flavor)]
print "Done!"
print "============================"
print "Getting IP addresses for SOURCE server..."
#Set up variables to hold public and private IP address for our SOURCE server
source_publicIP = my_source.accessIPv4
source_privateIP = my_source.networks['private'][0]
print "Done!"
print "============================"

#Print details of our SOURCE server.  This is the server we want to GET a copy of sent to our OFFLOAD server we will build
print "SOURCE server details.  This is the server that we are GETTING a copy of and sending to our OFFLOAD server --->"
print "\tName:", my_source.name
print "\tAllocated Disk Size: %sGB" % source_disk
print "\tRecommended SATA Volume Size: %GB" % SATA_VOLUME[0]
print "\tPublic IP: %s" % source_publicIP
print "\tPrivate IP: %s" % source_privateIP
print "============================"



### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
################################################### CREATE OFFLOAD SERVER ##################################################
### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#WE NEED TO BUILD A TEMPORARY OFFLOAD SERVER TO ATTACH BLOCK STORAGE TO.  THIS IS THE DESTINATION SERVER FOR 'dd' DISK IMAGE OVER SSH.

print "Preparing to build OFFLOAD server that will be the destination for our dd image transfer..."
print "..."

print "Setting base image, flavor, and name of OFFLOAD server to be used during server build..."
#create server image object for centos 6.4
centos_image = [img for img in cs.images.list() if "CentOS 6.4" in img.name][0]
#create a flaver object used in server creation
flavor_512 = [flavor for flavor in cs.flavors.list() if flavor.ram == 512][0]
#create a unique ID used to create name for our OFFLOAD server
server_unique_id = pyrax.utils.random_name(8, ascii_only=True)    #<----create a 8 (ascii-only) character unique string ID to append to server name if necessary
#create the OFFLOAD server name by adding the unique id to base name 'OFFLOAD.NG_image.'
server_name = "OFFLOAD.NG_image." + server_unique_id
print "Done!"
print "============================"

#We need to create a keypair so that we can utilize ssh keys later.  This keypair will allow us to load our public ssh key onto OFFLOAD server during build
MY_RSAKEY_FILE = os.path.expanduser("~/.ssh/id_rsa.pub")
existing_keypairs = cs.keypairs.list()
#
#I could use this loop to delete the existing keypairs.  I am just attempting the create and letting it pass an exception if it already exists.
#
#if existing_keypairs:
#    print "Existing keypair found!"
#    for kp in existing_keypairs:
#      if kp.name == "OFFLOAD_server_key":
#        cs.keypairs.delete(kp.name)
#      print "Deleted keypair named: ", kp.name
#else:
#    print "No existing keypairs found!"
#
print "Creating new key pair for our OFFLOAD server using public ssh key located at %s..." % MY_RSAKEY_FILE
try:
  with open(os.path.expanduser(MY_RSAKEY_FILE)) as keyfile:
    cs.keypairs.create("OFFLOAD_server_key", keyfile.read())
except Exception as e:      #<---if this key already exists it will error but we are bypassing if that is the case
  print e
  pass
print "Done!"
print "============================"

#Create our OFFLOAD server with keypair and wait until it is in ACTIVE/ERROR status
print "Creating the server with keypair and waiting until is it in 'Active' state.  This may take several seconds..."
my_offload = cs.servers.create(server_name, centos_image.id, flavor_512.id, key_name="OFFLOAD_server_key")
pyrax.utils.wait_until(my_offload, "status", ["ACTIVE", "ERROR"], attempts=0, verbose=True, verbose_atts="progress")
if my_offload.status == "ERROR":
  print "OFFLOAD server returned an ERROR status during build.  Exiting!"
  time.sleep(5)
  sys.exit(1)
print "Done!"
print "============================"

#Set up variables to hold the public/private
offload_publicIP = my_offload.accessIPv4
offload_privateIP = my_offload.networks['private'][0]

#Print OFFLOAD server details.
print "### The following server created successfully.  It will be used as a staging area for our Next Gen image. ###"
print "\tServer name:", my_offload.name
print "\tID:", my_offload.id
print "\tStatus:", my_offload.status
print "\tAdmin Password:", my_offload.adminPass
print "\tPublic Network used for SSH access:", offload_publicIP
print "\tPrivate network (service net) used for access to this server from within the same DC/Region:", offload_privateIP
print "============================"



### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
################################################## CREATE SATA STORAGE VOLUME ##############################################
### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#Create a block storage volume, partition, create filesystem, attach and mount on OFFLOAD server

#connect to rackspace cloud block storage
print "Connecting to cloud blockstorage..."
cbs = pyrax.cloud_blockstorage
#create a unique cbs ID
cbs_unique_id = pyrax.utils.random_name(8, ascii_only=True)
#create full volume name containing SOURCE server uuid and a unique id
vol_name = "CBS_OFFLOAD_NG." + cbs_unique_id
#this is the mountpoint keyword used when creating cbs volume that denotes the device name it will have once attached to a server.
mountpoint = "/dev/xvdd"
#create the volume....in this case a SATA volume.  I will provide the SSD example just below
print "Done!"
print "============================"
print "Creating a %sGB SATA volume..." % SATA_VOLUME[0]
sata_vol = cbs.create(name=vol_name, size=SATA_VOLUME[0], volume_type="SATA")
print "Successfully created block storage volume..."
print "Volume name:", sata_vol.name
print "Volume size:", SATA_VOLUME[0]
print "OFFLOAD server where SATA volume will be attached:", my_offload.name
print "Mountpoint:", mountpoint
print "\t--> The 'mountpoint' is device name that will be assigned to the SATA volume once attached to server"
print "============================"
print "Attaching to target server.  This may take several seconds for the attachment to complete..."
sata_vol.attach_to_instance(my_offload, mountpoint=mountpoint)
pyrax.utils.wait_until(sata_vol, "status", "in-use", interval=3, attempts=0, verbose=True, verbose_atts="progress")
print "Success!"
print "Volume attachments:", sata_vol.attachments
print "Done setting up temporary OFFLOAD server to cache NG image"
print "============================"
"""
#TO DETACH volume later when tearing this stuff down
sata_vol.detach()   #<----detach volume
pyrax.utils.wait_until(sata_vol, "status", "available", interval=3, attempts=0, verbose=True)
print "Attachments:", sata_vol.attachments
print "Done!"

#TO DELETE THE VOLUME
sata_vol.delete()
print "Volume %s deleted successfully!" % sata_vol.name
"""

#Set up SSH connection to remote OFFLOAD server
print "Setting up SSH connection to OFFLOAD server and configuring parameters..."
ssh = paramiko.SSHClient()
#ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))   #<-not necessary
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#ssh.load_system_host_keys() #<-not necessary
ssh.connect(offload_publicIP, username='root', key_filename=MY_RSAKEY_FILE, timeout=60)
#ssh.connect(buffer_public_ip, username='root')
print "Done!"
print "============================"
print "Partitioning SATA Block Storage device..."
stdin, stdout, stderr = ssh.exec_command("echo -e 'n\np\n1\n\n\nw\n' | fdisk %s" % mountpoint)  #<---partition our SATA volume all in one partition
for line in stdout.readlines():
  print line
print "Done formatting volume.  Verify that new partition exists..."
partitioned_device = mountpoint + str(1)
print "partitioned_device = ", partitioned_device
stdin, stdout, stderr = ssh.exec_command("if [ -b %s ]; then echo 'True'; else echo 'False'; fi" % partitioned_device)
pre_result = stdout.read()
post_result = re.sub('\n', '', pre_result)
if post_result == "True":
  print "Successfully created partition on SATA block storage device!"
  print "post_result = ", post_result
  print "pre_result = ", pre_result
else:
  print "Failed to create partition on SATA block storage device!  Exiting!"
  #sys.exit(1)
  print "post_result = ", post_result
  print "pre_result = ", pre_result
print "============================"
print "Creating filesystem on SATA Block Storage volume..."
stdin, stdout, stderr = ssh.exec_command("mkfs -t ext3 %s1" % mountpoint)
for line in stdout.readlines():
  print line
print "Done!"
#to verify the file system type    df -T | grep partitioned_device |  awk '{print $2}'
print "============================"
print "Mounting SATA Block storage device %s on 'mount'" % my_offload.name
stdin, stdout, stderr = ssh.exec_command("mount -t ext3 %s1 /mnt" % mountpoint)
for line in stdout.readlines():
  print line
print "Done!"
print "============================"
print "CBS storage and Offload server setup complete!\n\n"


### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#################################### WE NEED TO PLACE THE SOURCE SERVER INTO RESCUE MODE ###################################
### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#NOW WE NEED TO PLACE OUR SOURCE SERVER INTO RESCUE MODE.  THIS IS THE SERVER WE WANT TO IMAGE.  THIS IMAGE
#WILL BE SENT OVER THE WIRE FROM OUR SOURCE SERVER TO THE PRIVATE IP OF OUR OFFLOAD SERVER THAT WAS JUST
#CREATED, SPECIFICALLY ONTO OUR SATA DRIVE THAT WAS PREVIOUSLY MOUNTED AND FORMATTED

#Try putting our source server into rescue mode  --> using   (my_source = cs.servers.get(SOURCE_UUID))
print "Placing SOURCE server %s into rescue mode before continuing.  This make take several minutes..." % my_source.name
mystatus,myoutput = my_source.rescue()
pyrax.utils.wait_until(my_source, "status", ["RESCUE", "ERROR"], attempts=0, verbose=True, verbose_atts="progress")
my_source_rescue_pwd = myoutput['adminPass']
print "Done!"
print "============================"
print "RESCUED SOURCE SERVER DETAILS--->"
print "\tName:", my_source.name
print "\tRescue mode return status: ", mystatus
print "\tSource rescued server password: ", my_source_rescue_pwd
print "\tPublic IP of rescued server: ", source_publicIP
print "\tPrivate IP of rescued sever: ", source_privateIP
print "Done!"
print "============================"
#Need to remove the ssh key for our source server from our local computer or ssh w/ key will fail because fingerprint has changed after rescue mode.
print "Removing SSH key from known hosts on this workstation (if ssh already exists for the SOURCE server)...."
subprocess.call('ssh-keygen -R %s' % source_publicIP, shell=True)  #<--remove ssh key for SOURCE IP from known_hosts on my workstation
print "Done!"
print "============================"
#SSH to rescued source server from my workstation.  We will initialize image transfer
print "Setting up SSH connection to rescued SOURCE server and configuring parameters..."
#Set up ssh client
ssh_rescued_server = paramiko.SSHClient()
#Turn off strict host key checking.  Equivalent to -oStrictHostKeyChecking=no when using ssh
ssh_rescued_server.set_missing_host_key_policy(paramiko.AutoAddPolicy())

### Turn on logging if necessary.  Just uncomment one of these two lines ###
#paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)   #<---turn on debug
#paramiko.common.logging.basicConfig(level=paramiko.common.INFO)   #<---turn on info level

#Connect to server by calling connect() on the ssh client object
ssh_rescued_server.connect(source_publicIP, username='root', password=my_source_rescue_pwd)
print "Done!"
print "============================"
#check for available disk devices
print "Check for available disk devices..."
stdin, stdout, stderr = ssh_rescued_server.exec_command("fdisk -l | grep '^Disk'")
channel_out = stdout.channel
#print "Current clock time: ", now()
#print "Checking channel exit ready status..."
#print "exit status ready ===>", channel_out.exit_status_ready()
#print "--"
print "Checking recv exit status..."
status = channel_out.recv_exit_status()
print "recv exit status.. ===>", status
#print "--"
#print "Checking channel exit ready status..."
#print "exit status ready ===>", channel_out.exit_status_ready()
print "--"
print "Receiving response from server..."
for line in stdout.readlines():
    print line
print "Done!"
print "============================"
print "Verifying host name.  This should be the hostname of the Rescued server (SOURCE)..."
stdin, stdout, stderr = ssh_rescued_server.exec_command("hostname")
channel_out = stdout.channel
#print "Current clock time: ", now()
#print "Checking channel exit ready status..."
#print "exit status ready ===>", channel_out.exit_status_ready()
#print "--"
print "Checking recv exit status..."
status = channel_out.recv_exit_status()
print "recv exit status.. ===>", status
#print "--"
#print "Checking channel exit ready status..."
#print "exit status ready ===>", channel_out.exit_status_ready()
#print "--"
print "Receiving response from server..."
for line in stdout.readlines():
    print line
print ""
print "Expected hostname: %s" % my_source.name
print ""
print "Done!"
print "============================"
print "Initialize sshpass setup.  First we will install dependencies.  GCC and make must be installed because the yum installation will fail on connection attempt  ..."
print "Installing gcc.."
stdin, stdout, stderr = ssh_rescued_server.exec_command("yum -y install gcc")
print "Checking recv exit status.  Again, this may take several minutes and may appear to hang but do not cancel operation.  It will continue..."
status = channel_out.recv_exit_status()
print "recv exit status.. ===>", status
for line in stdout.readlines():
    print line
print "Done!"
print "Installing make..."
stdin, stdout, stderr = ssh_rescued_server.exec_command("yum -y install make")
print "Checking recv exit status.  Again, this may take several minutes and may appear to hang but do not cancel operation.  It will continue..."
status = channel_out.recv_exit_status()
print "recv exit status.. ===>", status
for line in stdout.readlines():
    print line
print "Done!"
channel_out = stdout.channel
print "Current clock time: ", now()
print "Checking channel exit ready status..."
print "exit status ready ===>", channel_out.exit_status_ready()
print "--"
print "Receiving response from server..."
for line in stdout.readlines():
    print line
print "Dependency resolution for sshpass complete!"
print "============================"
print "Downloading sshpass source code ..."
#NOTE - I am hosting this copy of sshpass on my cloud files account, published on the cdn.
stdin, stdout, stderr = ssh_rescued_server.exec_command("wget http://e1446f058cab9ae44fbf-5cda71ed19c8d4f705f7d0efcc8652d5.r21.cf1.rackcdn.com/sshpass-1.05.tar.gz")
channel_out = stdout.channel
#print "Current clock time: ", now()
#print "Checking channel exit ready status..."
#print "exit status ready ===>", channel_out.exit_status_ready()
#print "--"
print "Checking recv exit status..."
status = channel_out.recv_exit_status()
print "recv exit status.. ===>", status
#print "--"
#print "Checking channel exit ready status..."
#print "exit status ready ===>", channel_out.exit_status_ready()
#print "--"
print "Receiving response from server..."
for line in stdout.readlines():
    print line
print "Download Complete!"
print "============================"
print "Unpacking sshpass and cd into source directory; compile and install..."
stdin, stdout, stderr = ssh_rescued_server.exec_command("tar -xzf sshpass-1.05.tar.gz; cd sshpass-1.05;./configure;make;make install")
channel_out = stdout.channel
#print "Current clock time: ", now()
#print "Checking channel exit ready status..."
#print "exit status ready ===>", channel_out.exit_status_ready()
#print "--"
print "Checking recv exit status..."
status = channel_out.recv_exit_status()
print "recv exit status.. ===>", status
#print "--"
#print "Checking channel exit ready status..."
#print "exit status ready ===>", channel_out.exit_status_ready()
#print "--"
print "Receiving response from server..."
for line in stdout.readlines():
    print line
print "sshpass compile and install complete!"
print "============================"
print "Installing lzop for data compression on the wire..."
stdin, stdout, stderr = ssh_rescued_server.exec_command("yum -y install lzop")
channel_out = stdout.channel
#print "Current clock time: ", now()
#print "Checking channel exit ready status..."
#print "exit status ready ===>", channel_out.exit_status_ready()
#print "--"
print "Checking recv exit status..."
status = channel_out.recv_exit_status()
print "recv exit status.. ===>", status
#print "--"
#print "Checking channel exit ready status..."
#print "exit status ready ===>", channel_out.exit_status_ready()
#print "--"
print "Receiving response from server..."
for line in stdout.readlines():
    print line
print "Done!"
print "=============="
print "Initializing root disk transfer over the wire to remote OFFLOAD server..."
print "Source server: ", my_source.name
transport = ssh.get_transport()
channel = transport.open_session()
print "Sending command string to server:  time dd if=/dev/xvdb bs=2M | lzop | sshpass -p '%s' ssh -oStrictHostKeyChecking=no root@%s 'dd of=/mnt/%s_root_img.lzo bs=2M'" % (my_offload.adminPass,offload_privateIP,my_offload.name)
stdin, stdout, stderr = ssh_rescued_server.exec_command("time dd if=/dev/xvdb bs=2M | \
							lzop | \
							sshpass -p '%s' \
							ssh root@%s \
							-oStrictHostKeyChecking=no \
							'dd of=/mnt/%s_root_img.lzo bs=2M'" % (my_offload.adminPass,offload_privateIP,my_offload.name))

print "=====>>Transferring copy of root disk from %s to %s over service net..." % (my_source.name, my_offload.name)
print "=====>>>Sending block-level copy over encrypted ssh connection with LZOP compression on the wire..."
print "=====>>>>Tranfer settings optimized for maximum speed while maintaining data privacy using SSH for encryption..."
print "======>>>>This make take several minutes...I have some benchmark tests I can provide to demonstrate speed associated with dd block size and compression tools"
print "--"
#print "This is the current exit status....current exit status= ", channel.exit_status_ready()
channel_out = stdout.channel
#print "Current clock time: ", now()
#print "Checking channel exit ready status..."
#print "exit status ready ===>", channel_out.exit_status_ready()
#print "--"
print "Checking recv exit status..."
status = channel_out.recv_exit_status()
print "recv exit status.. ===>", status
#print "--"
#print "Checking channel exit ready status..."
#print "exit status ready ===>", channel_out.exit_status_ready()
print "--"
print "Receiving response from server..."
for line in stdout.readlines():
    print line
#print "Imaged copied to OFFLOAD server...current exit status=", channel.exit_status_ready()
print 'Done!'
print "============================"
print "Closing connections to OFFLOAD server and rescued server"
channel.close()
print "Connction Closed!"
print "============================"
print "SOURCE server exiting rescue mode..."
my_source.unrescue()
pyrax.utils.wait_until(my_source, "status", ["ACTIVE", "ERROR"], attempts=0, verbose=True, verbose_atts="progress")
print "Unrescue exit status:", mystatus

print "============================" * 3
print "============================" * 3

#Print details for image retrieval
print "OFFLOAD SERVER DETAILS"
print "To access my image just ssh/sftp/scp from our image offload server.  It is saved on a SATA block storage volume (mounted on /mnt) so we can also reattach to a different server if necessary"
print "\tOffload Server name:", my_offload.name
print "\tID:", my_offload.id
print "\tStatus:", my_offload.status
print "\tAdmin Password:", my_offload.adminPass
print "\tPublic Network used for SSH/SFTP/scp access:", offload_publicIP
print "\tPrivate network (service net) used for access to this server from within the same DC/Region:", offload_privateIP
print "NOTE ==. need to add prefab lines for downloading image from OFFLOAD server.."
print "=============="
#Print details of our SOURCE server.  This is the server we want to GET a copy of sent to our OFFLOAD server we will build
print "SOURCE server details.  This is the server that we are GETTING a copy of and sending to our OFFLOAD server --->"
print "\tName:", my_source.name
print "\tAllocated Disk Size: %sGB" % source_disk
print "\tRecommended SATA Volume Size: %GB" % SATA_VOLUME[0]
print "\tPublic IP: %s" % source_publicIP
print "\tPrivate IP: %s" % source_privateIP
print "=============="


print "all done for now!!!"


#
#def main():
#  parser = argparse.ArgumentParser(prog='ohthree.py', description='Use to get instance|host_server information')
#  parser.add_argument('--uuid', '-u',required=True, nargs=1, help='-u $SERVER_INSTANCE_ID|name-label UUID')
#  args = parser.parse_args()
#  #print ("Input file: %s" % args.uuid )
#  if args.uuid:
#    y = "".join(args.uuid)
#    #x = str(args.uuid[0])
#    instance = OhThree(y)
#    return instance.getVMinfo()
#
#if __name__ == "__main__" :
#  try:
#    main()
#  except Exception, e:
#    print "Error: %s" % e
#    print ""
#    print 'Enter correct instance UUID or verify that instance exists and then retry'
#    print ""
#    sys.exit()