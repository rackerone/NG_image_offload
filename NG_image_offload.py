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

#i can add support for pv (pipe viewer) later http://www.ivarch.com/programs/yum.shtml.  progress meter
#http://stackoverflow.com/questions/16199793/python-3-3-simple-threading-event-example  -->need to use threads ...
#..need to start a thread that connects to buffer server and starts nc, then new thread opens thread to rescue and starts
#..dd over netcat...we then then join threads and wait for them to finish.

#http://code.activestate.com/recipes/576810-copy-files-over-ssh-using-paramiko/
#If you need to do this in a non-blocking way, you will have to use the channel object directly. You can then
#watch for both stdout and stderr with channel.recv_ready() and channel.recv_stderr_ready(), or use select.select.

###+_+_+_+_+_+_+_+_+_+_++_+_+###
#Save Next Generation server images to remote location like cloud files.  Allow download locally and restore

import pyrax
import os
import re
from time import sleep
import time
import subprocess  #<---use to execute local filesystem commands
import pexpect
import sys
import cgitb   #<---this provides detailed tracebacks on error
import pdb   #<---python debugger - insert pdb.set_trace()
#Paramiko will not be installed by default so most people will need to install it
try:
  import paramiko  #<---this is used to create SSH connections
except ImportError as e:
  print e
  print "Please install paramiko for SSH support!\npip install paramiko\nOR\neasy_install paramiko\n\n"
  print "Retry this script after installation."
  sys.exit(1)

#enable detailed tracebacks
cgitb.enable(format='text')

#Clear screen and start output from the top
os.system('cls' if os.name=='nt' else 'clear')

### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#### SETUP SOME GLOBAL VARIABLES ###
print "Setting up gloabal variables..."
CREDS_FILE = os.path.expanduser("~/.rackspace_cloud_credentials")
REGIONS = ["DFW", "ORD", "LON"]
TARGET_UUID = ''     #<----this is will ultimately hold the target uuid of the server we want to image
SATA_VOLUME = ''    #<---this will hold the size of the sata volume to create
SPACER = "\n\n"   #<---this will provide a blank two-line seperator for formatting purposes
print "Done!"
print "=============="

### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
############################################################################################################################
### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
# ----> CLASSES  ---->
#-->can set this up later if funtional testing works out


### END CLASSES ^^
### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
############################################################################################################################
### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#----->FUNCTIONS---->

def now():
  """Use to timestamp current time."""
  return time.time()

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
  myrsakeyfile = os.path.expanduser("~/.ssh/id_rsa.pub")
  ssh.connect(server, username='root', key_filename=myrsakeyfile, timeout=60)
  invokedShell = ssh.invoke_shell()
  transport = ssh.get_transport()  #not using this currently but get access to channels this way

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
  data = channel.recv(1024)
  print "--"
  return data

def checkProgress():
    """Use to check the progress of ssh transfer of dd image to remote buffer/imageoffload server"""
    
    pass



### END FUNCTIONS ^^
### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#################################### Authenticating to Rackspace cloud######################################
### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#----->SETTING UP RACKSPACE CLOUD CONNECTION AND PREPARING/BUILDING AN OFFLOAD SERVER TO HOLD OUR IMAGE---->

#Authenticate
print "Authenticating to Rackspace Cloud..."
pyrax.set_setting('identity_type', 'rackspace')
pyrax.set_credential_file(CREDS_FILE)
print "Done!"
print "=============="

### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#Set default region and then create conections to each region
print "Setting up default region of DFW..."
pyrax.set_default_region("DFW")   #<---set default region
print "Done!"
print "=============="
print "Establishing connections to DFW and ORD and compiling list of servers.  This may take a few minutes..."
cs = pyrax.cloudservers
cs_dfw_conn = pyrax.connect_to_cloudservers(region="DFW")
cs_dfw_servers = cs_dfw_conn.servers.list()
cs_ord_conn = pyrax.connect_to_cloudservers(region="ORD")
cs_ord_servers = cs_ord_conn.servers.list()
#Set up a list of all servers from each region combined into a single list
all_servers = cs_dfw_servers + cs_ord_servers
print "Done!"
print "=============="

### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#Create a list of server UUID's that we will use to verify that user supplied target UUID is valid.  
print "Setting up list of server UUIDs used to validate user supplied target UUID is an actual valid UUID..."
server_UUIDs = [server.id for server in all_servers]
print "Done!"
print "=============="

### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#Print a list of servers/UUIDs for the user to choose from.  Must enter the UUID of the NG server you wish to image.
#I will need to set up a regex first to grab the ip4 ip from the list of public networks because I am including this IP in output.
#clear_me()    #<---this will clear the terminal screen so we can put server list up and make it easier to read
regex = re.compile(r'(?P<public_ip4>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')  #<---Set up regex for IP4 address (omit ipv6). Assign group name 'public_ip4' to the ip address
target_public_ip = ''  #<--initialize public ip variable (although not necessary)
target_private_ip = ''  #<--initialize the private ip variable (although not necessary)
print "\n\nCHOOSE FROM THE FOLLOWING LIST OF SERVERS.  Please copy the UUID and enter below as the value for 'Target Server UUID'\n"
for server in all_servers:
    for ip in server.networks['public']:
      result = regex.search(ip)
      if result:
        target_public_ip = result.group('public_ip4')
    target_private_ip = server.networks['private'][0]
    print "Server Name: %s\nServer UUID: %s\nFlavor: %s\nPublic IP: %s\nPrivate IP: %s" % (server.name, server.id, server.flavor['id'], server.accessIPv4, target_private_ip)
    print "============================"

### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#------->We need to wait for user input here (should be UUID).  We will compare this UUID to list of known UUIDs.  If not present we re-prompt for user input
while True:
  TARGET_UUID = raw_input("Enter Target UUID (this is the ID of the server you wish to image): ")   #<---wait for user input
  if TARGET_UUID not in server_UUIDs:  #<---is TARGET_UUID in our list of uuids?
    print "Error!  UUID entered did not match any of your server UUIDs.\n\n"
    continue     #<----if the TARGET_UUID is not in our list then continue back at top of loop and wait for input
  break   #<---if TARGET_UUID was in the list then break out of the loop
print "\n\n"

### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#---> Now that we have a TARGET_UUID we can create a server object using this UUID.  Then we can place it in rescue mode and continue operations on it
print "Calculating the amount of SATA block storage needed to accomodate this request based on target server chosen..."
#Setting up a dictionary to hold SATA cbs volume size in GB as keys and the flavor IDs that small enough to fit on them as the values
sata_cbs_dict = {2:100, 3:100, 4:100, 5:200, 6:400, 7:700, 8:1200}
my_target = cs.servers.get(TARGET_UUID)
target_flavor = my_target.flavor['id']  #<--determine flavor so we can attach the appropriate size block storage on temp server
target_disk = cs.flavors.get(target_flavor).disk #<---determine allocated disk size for target server.
SATA_VOLUME = [value for key,value in sata_cbs_dict.items() if key is int(target_flavor)]
print "\tTarget server's allocated disk size is %sGB." % target_disk
print "\tWe will need to create a %s SATA Block Storage device large enough to hold this." % SATA_VOLUME[0]
print ".\n..\n..."

#Set up variables to hold public and private IP address for our TARGET server
target_publicIP = my_target.accessIPv4
target_privateIP = my_target.networks['private'][0]

#Print details of our TARGET server.  This is the server we want to GET a copy of sent to our OFFLOAD server we will build
print "TARGET server details.  This is the server that we are GETTING a copy of and sending to our OFFLOAD server --->"
print "\tName:", my_target.name
print "\tAllocated Disk Size: %sGB" % target_disk
print "\tRecommended SATA Volume Size: %GB" % SATA_VOLUME[0]
print "\tPublic IP: %s" % target_publicIP
print "\tPrivate IP: %s" % target_privateIP
print "=============="

### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#WE NEED TO BUILD A TEMPORARY OFFLOAD SERVER TO ATTACH BLOCK STORAGE TO.  THIS IS THE DESTINATION SERVER FOR 'dd' DISK IMAGE OVER SSH.

print "Preparing to build OFFLOAD server that will be the destination for our dd image transfer..."
print "..."
print "Setting base image, flavor, and name of OFFLOAD server.."
#create server image object for centos 6.4
centos_image = [img for img in cs.images.list() if "CentOS 6.4" in img.name][0]
#create a flaver object used in server creation
flavor_512 = [flavor for flavor in cs.flavors.list() if flavor.ram == 512][0]
#create a unique ID used to create name for our OFFLOAD server
server_unique_id = pyrax.utils.random_name(8, ascii_only=True)    #<----create a 8 (ascii-only) character unique string ID to append to server name if necessary
#create the OFFLOAD server name by adding the unique id to base name 'OFFLOAD.NG_image.'
server_name = "OFFLOAD.NG_image." + server_unique_id
print "Done!"

#We need to create a keypair so that we can utilize ssh keys later.  This keypair will allow us to load our public ssh key onto OFFLOAD server during build
#THIS IS HOW WE CREATE KEY PAIRS
#Create an object that stores your public ssh key.
#print "Checking for existing SSH keypairs.  This is relevant because by placing server in rescue mode will change fingerprint and cause error."
#print "We are just going to check for the existance of a keypair from a previous run of this script, and if it exists we will delete it..."
myrsakeyfile = os.path.expanduser("~/.ssh/id_rsa.pub")
existing_keypairs = cs.keypairs.list()
#if existing_keypairs:
#    print "Existing keypair found!"
#    for kp in existing_keypairs:
#      if kp.name == "OFFLOAD_server_key":
#        cs.keypairs.delete(kp.name)
#      print "Deleted keypair named: ", kp.name
#else:
#    print "No existing keypairs found!"
print "Creating new key pair for our OFFLOAD server using pub ssh key located at %s..." % myrsakeyfile
try:
  with open(os.path.expanduser(myrsakeyfile)) as keyfile:
    cs.keypairs.create("OFFLOAD_server_key", keyfile.read())
except Exception as e:
  pass

#print "Keypair name: %s" % keypair_name
print "Done!"
print "=============="
print "Creating the server and waiting until is it in 'Active' state.  This may take several seconds..."
myserver = cs.servers.create(server_name, centos_image.id, flavor_512.id, key_name="OFFLOAD_server_key")
pyrax.utils.wait_until(myserver, "status", ["ACTIVE", "ERROR"], attempts=0, verbose=True, verbose_atts="progress")
print "Done!"
print ""

#Print server details.  I will need to set up a regex first to grab the ip4 ip from the list of public networks.  There is probably n attribute like this but.?
regexIP4 = re.compile(r'(?P<public_ip4>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')#<---Set up regex for IP4 address. Assign group name 'public_ip4' to the ip address
public_ip = ''
buffer_public_ip = ''
for ip in myserver.networks['public']:
  result = regex.search(ip)
  if result:
    buffer_public_ip = result.group('public_ip4')
###=======>UPDATE---> there is an attribute for ip4.  server_obj.accessIP4

buffer_private_ip = myserver.networks['private'][0]
print "### The following server created successfully.  It will be used as a staging area for our Next Gen image. ###"
print "\tServer name:", myserver.name
print "\tID:", myserver.id
print "\tStatus:", myserver.status
print "\tAdmin Password:", myserver.adminPass
print "\tPublic Network used for SSH access:", buffer_public_ip
print "\tPrivate network (service net) used for access to this server from within the same DC/Region:", buffer_private_ip
print "=============="


### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#NEED TO CREATE A BLOCK STORAGE VOLUME AND ATTACH TO BUFFER SERVER THAT WE JUST CREATED

#connect to block storage
print "Connecting to cloud blockstorage..."
#cbs = pyrax.connect_to_cloud_blockstorage(region="DWF")  #<---getting SERVICE UNAVAILABLE so set default region at top and connected below
cbs = pyrax.cloud_blockstorage
#create a unique cbs ID
cbs_unique_id = pyrax.utils.random_name(8, ascii_only=True)
#create full volume name
vol_name = "CBSVolume." + cbs_unique_id
#create the volume....in this case a SATA volume.  I will provide the SSD example just below
print "=============="
print "Creating a %sGB SATA volume..." % SATA_VOLUME[0]
sata_vol = cbs.create(name=vol_name, size=SATA_VOLUME[0], volume_type="SATA")
print "Successfully created block storage volume..."
print "Volume name:", sata_vol.name
print "Volume size:", SATA_VOLUME[0]
print "Target server:", myserver.name
mountpoint = "/dev/xvdd"
print "Mountpoint:", mountpoint
print "=============="
print "Attaching to target server.  This may take several seconds for the attachment to complete..."
sata_vol.attach_to_instance(myserver, mountpoint=mountpoint)
pyrax.utils.wait_until(sata_vol, "status", "in-use", interval=3, attempts=0, verbose=True, verbose_atts="progress")
print "Success!"
print "Volume attachments:", sata_vol.attachments
#--->SSD  --->  ssd_vol = cbs.create(name=vol_name, size=100, volume_type="SSD")
print "=============="
print "Done setting up temporary server to cache NG image"
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


### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#NOW NEED TO SSH TO THIS REMOTE BUFFER SEVER AND FORMATE CBS VOLUME

#Set up SSH connection to remote buffer server
print "Setting up SSH connection to buffer server and configuring parameters..."
ssh = paramiko.SSHClient()
#ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#ssh.load_system_host_keys()
ssh.connect(buffer_public_ip, username='root', key_filename=myrsakeyfile, timeout=-1)
#ssh.connect(buffer_public_ip, username='root')
print "Done!"
print "=============="
print "Partitioning SATA Block Storage device..."
stdin, stdout, stderr = ssh.exec_command("echo -e 'n\np\n1\n\n\nw\n' | fdisk %s" % mountpoint)  #<---partition a new disk all in one partition
#pid = int(stdout.readline()) #<---this is the pid number of the command we just sent..??
for line in stdout.readlines():
  print line
print ""
for line in stderr.readlines():
  print line
print "Done formatting volume.  Verify that new partition exists..."
stdin, stdout, stderr = ssh.exec_command("fdisk -l /dev/xvdd")
for line in stdout.readlines():
  print line
print ""
for line in stderr.readlines():
  print line
print "Done!"
print "=============="
print "Creating filesystem on SATA Block Storage volume..."
stdin, stdout, stderr = ssh.exec_command("mkfs -t ext3 %s1" % mountpoint)
sleep(10)
for line in stdout.readlines():
  print line
print ""
for line in stderr.readlines():
  print line
print ""
print "Done!"
print "=============="
print "Mounting SATA Block storage device on %s" % myserver.name
stdin, stdout, stderr = ssh.exec_command("mount -t ext3 %s1 /mnt" % mountpoint)
for line in stdout.readlines():
  print line
print ""
for line in stderr.readlines():
  print line
print ""
print "Done!"
print "=============="
print "Offload/Buffer server setup complete!\n\n"

### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
############################################################################################################################
### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###==### +_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+ ###
#NOW WE NEED TO PLACE OUR TARGET SERVER INTO RESCUE MODE.  THIS IS THE SERVER WE WANT TO IMAGE.  THIS IMAGE
#WILL BE SENT OVER THE WIRE FROM OUR TARGET SERVER TO THE PRIVATE IP OF OUR BUFFER SERVER THAT WAS JUST
#CREATED, SPECIFICALLY ONTO OUR SATA DRIVE THAT WAS PREVIOUSLY MOUNTED AND FORMATTED

#Try putting our target server into rescue mode  --> using   (my_target = cs.servers.get(TARGET_UUID))
print "Placing target server %s into rescue mode before continuing.  This make take several minutes..." % my_target.name
mystatus,myoutput = my_target.rescue()
pyrax.utils.wait_until(my_target, "status", ["RESCUE", "ERROR"], attempts=0, verbose=True, verbose_atts="progress")
my_target_rescue_pwd = myoutput['adminPass']
print "Done!"
print "=============="
print "RESCUED TARGET SERVER DETAILS--->"
print "Name:", my_target.name
print "Rescue mode return status: ", mystatus
print "Target rescued server password: ", my_target_rescue_pwd
print "Public IP of rescued server: ", target_publicIP
print "Private IP of rescued sever: ", target_privateIP
print "Done!"
print "=============="

############################################################################################################################
#After placing into rescue mode my ***TARGET*** server will have a new fingerprint so i will get a failure when trying
#to connect from my workstation via SSH (keys won't match).  I can just delete the key for my target server from '/etc/known_hosts'.
#This will allow me to connect to the rescued server and initiate the image dump.
#To remove host key on my local workstation:
####example  --->  ssh-keygen -R 166.78.185.24    #<---can be server name, domain name, ip

print "Removing SSH key from known hosts on this workstation...."
subprocess.call('ssh-keygen -R %s' % target_publicIP, shell=True)  #<--remove ssh key for target IP from known_hosts on my workstation
print "Done!"
print "=============="

############################################################################################################################
#SSH to rescued target server from my workstation.  We will initialize image transfer
print "Setting up SSH connection to rescued server and configuring parameters..."

#Set up ssh client
ssh_rescued_server = paramiko.SSHClient()

### Turn on logging if necessary.  Just uncomment one of these two lines ###
#paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)   #<---turn on debug
#paramiko.common.logging.basicConfig(level=paramiko.common.INFO)   #<---turn on info level

#Turn off strict host key checking.  Equivalent to -oStrictHostKeyChecking=no when using ssh
ssh_rescued_server.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#Connect to server by calling connect() on the ssh client object
ssh_rescued_server.connect(target_publicIP, username='root', password=my_target_rescue_pwd)
print "Done!"
print "=============="

#check for available disk devices
print "Check for available disk devices..."
stdin, stdout, stderr = ssh_rescued_server.exec_command("fdisk -l | grep '^Disk'")
channel_out = stdout.channel
print "Current clock time: ", now()
print "Checking channel exit ready status..."
print "exit status ready ===>", channel_out.exit_status_ready()
print "--"
print "Checking recv exit status..."
status = channel_out.recv_exit_status()
print "recv exit status.. ===>", status
print "--"
print "Checking channel exit ready status..."
print "exit status ready ===>", channel_out.exit_status_ready()
print "--"
print "Receiving response from server..."
#data = channel.recv(1024)
#for line in stdout.readlines():
#    print line
#print data
print ""
print "Done!"
print "=============="
print "Verifying host name.  This should be the hostname of the Rescued server (Target)..."
stdin, stdout, stderr = ssh_rescued_server.exec_command("hostname")
channel_out = stdout.channel
print "Current clock time: ", now()
print "Checking channel exit ready status..."
print "exit status ready ===>", channel_out.exit_status_ready()
print "--"
print "Checking recv exit status..."
status = channel_out.recv_exit_status()
print "recv exit status.. ===>", status
print "--"
print "Checking channel exit ready status..."
print "exit status ready ===>", channel_out.exit_status_ready()
print "--"
print "Receiving response from server..."
#data = channel.recv(1024)
#for line in stdout.readlines():
#    print line
#print data
print ""
print "Expected hostname: %s" % my_target.name
print ""
print "Done!"
print "=============="
print "Initialize sshpass setup.  First we will install dependencies.  GCC and make must be installed \nbecause the yum installation will fail on connection attempt  ..."
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
##data = channel.recv(1024)
for line in stdout.readlines():
    print line
#print data
print ""
print "Dependency resolution for sshpass complete!"
print "=============="
print "Downloading sshpass source code ..."
#NOTE - I am hosting this copy of sshpass on my cloud files account, published on the cdn.
stdin, stdout, stderr = ssh_rescued_server.exec_command("wget http://e1446f058cab9ae44fbf-5cda71ed19c8d4f705f7d0efcc8652d5.r21.cf1.rackcdn.com/sshpass-1.05.tar.gz")
channel_out = stdout.channel
print "Current clock time: ", now()
print "Checking channel exit ready status..."
print "exit status ready ===>", channel_out.exit_status_ready()
print "--"
print "Checking recv exit status..."
status = channel_out.recv_exit_status()
print "recv exit status.. ===>", status
print "--"
print "Checking channel exit ready status..."
print "exit status ready ===>", channel_out.exit_status_ready()
print "--"
print "Receiving response from server..."
#data = channel.recv(1024)
for line in stdout.readlines():
    print line
#print data
print ""
print "Download Complete!"
print "=============="
print "Unpacking sshpass and cd into source directory; compile and install..."
stdin, stdout, stderr = ssh_rescued_server.exec_command("tar -xzf sshpass-1.05.tar.gz; cd sshpass-1.05;./configure;make;make install")
channel_out = stdout.channel
print "Current clock time: ", now()
print "Checking channel exit ready status..."
print "exit status ready ===>", channel_out.exit_status_ready()
print "--"
print "Checking recv exit status..."
status = channel_out.recv_exit_status()
print "recv exit status.. ===>", status
print "--"
print "Checking channel exit ready status..."
print "exit status ready ===>", channel_out.exit_status_ready()
print "--"
print "Receiving response from server..."
#data = channel.recv(1024)
for line in stdout.readlines():
    print line
#print data
print ""
print "sshpass compile and install complete!"
print "=============="
print "Installing lzop for data compression on the wire..."
stdin, stdout, stderr = ssh_rescued_server.exec_command("yum -y install lzop")
channel_out = stdout.channel
print "Current clock time: ", now()
print "Checking channel exit ready status..."
print "exit status ready ===>", channel_out.exit_status_ready()
print "--"
print "Checking recv exit status..."
status = channel_out.recv_exit_status()
print "recv exit status.. ===>", status
print "--"
print "Checking channel exit ready status..."
print "exit status ready ===>", channel_out.exit_status_ready()
print "--"
print "Receiving response from server..."
#data = channel.recv(1024)
for line in stdout.readlines():
    print line
print "Done!"
print "=============="
print "Initializing root disk transfer over the wire to remote buffer server..."
print "Source server, also referred to as the 'target' of this script: ", my_target.name
transport = ssh.get_transport()
channel = transport.open_session()
#Possibly need to use screen to make the nc stay alive during this process...it keeps getting killed and we don't see transfer
#I need to see if there is a way to monitor progress of this call....
#stdin, stdout, stderr = ssh_rescued_server.exec_command("dd if=/dev/xvdb bs=16M | bzip2 -c | nc -v %s 9000 &" % buffer_private_ip)
print "Sending command string to server:  time dd if=/dev/xvdb bs=2M | lzop | sshpass -p '%s' ssh -oStrictHostKeyChecking=no root@%s 'dd of=/mnt/%s_root_img.lzo bs=2M'" % (myserver.adminPass,buffer_private_ip,myserver.name)
stdin, stdout, stderr = ssh_rescued_server.exec_command("time dd if=/dev/xvdb bs=2M | \
							lzop | \
							sshpass -p '%s' \
							ssh root@%s \
							-oStrictHostKeyChecking=no \
							'dd of=/mnt/%s_root_img.lzo bs=2M'" % (myserver.adminPass,buffer_private_ip,myserver.name))

print "=>\n==>\n===>\n====>\n"
print "=====>>Transferring copy of root disk from %s to %s over service net..." % (my_target.name, myserver.name)
print "=====>>>Sending block-level copy over encrypted ssh connection and LZOP compression..."
print "=====>>>>Tranfer settings optimized for maximum speed while maintaining data privacy on the wire..."
print "======>>>>This make take several minutes...I have some benchmark tests I can provide to demonstrate speed associated with dd block size and compression tools"
print "--"
print "This is the current exit status....current exit status= ", channel.exit_status_ready()
channel_out = stdout.channel
print "Current clock time: ", now()
print "Checking channel exit ready status..."
print "exit status ready ===>", channel_out.exit_status_ready()
print "--"
print "Checking recv exit status..."
status = channel_out.recv_exit_status()
print "recv exit status.. ===>", status
print "--"
print "Checking channel exit ready status..."
print "exit status ready ===>", channel_out.exit_status_ready()
print "--"
print "Receiving response from server..."
#data = channel.recv(1024)
for line in stdout.readlines():
    print line
#print data
print ""
print 'Done! Imaged copied to OFFLOAD server...current exit status=', channel.exit_status_ready()
print "=============="
print "Closing connections to OFFLOAD server and rescued server"
channel.close()
print "Done!"

print "==============" * 3
print "==============" * 3
print "OFFLOAD SERVER DETAILS"
print "To access my image just ssh/sftp/scp from our image offload server.  It is saved on a SATA block storage volume so we can also reattach to a different server if necessary"
print "\tOffload Server name:", myserver.name
print "\tID:", myserver.id
print "\tStatus:", myserver.status
print "\tAdmin Password:", myserver.adminPass
print "\tPublic Network used for SSH/SFTP/scp access:", buffer_public_ip
print "\tPrivate network (service net) used for access to this server from within the same DC/Region:", buffer_private_ip
print "NOTE ==. need to add prefab lines for downloading image from OFFLOAD server.."
print "=============="
#Print details of our TARGET server.  This is the server we want to GET a copy of sent to our OFFLOAD server we will build
print "TARGET server details.  This is the server that we are GETTING a copy of and sending to our OFFLOAD server --->"
print "\tName:", my_target.name
print "\tAllocated Disk Size: %sGB" % target_disk
print "\tRecommended SATA Volume Size: %GB" % SATA_VOLUME[0]
print "\tPublic IP: %s" % target_publicIP
print "\tPrivate IP: %s" % target_privateIP
print "=============="
print "Exiting TARGET server rescue mode..."
my_target.unrescue()
pyrax.utils.wait_until(my_target, "status", ["ACTIVE", "ERROR"], attempts=0, verbose=True, verbose_atts="progress")
print "Unrescue exit status:", mystatus


print "....to be continued..."

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