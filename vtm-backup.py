#!/usr/bin/python
#
# Name: 
#   VTM Backup Manager 
# Description: 
#   This is a script to manage the backups from virtual traffic manager
# Usage:
#   Usage: vtm-backup.py [options]
#
#   Options:
#     -h, --help            show this help message and exit
#     -t HOSTNAME, --hostname=HOSTNAME
#                        hostname of VTM server
#     -o OPERATION, --operation=list/download/create/delete
#                        the operation to perform 
#     -n NAME, --name=Backup Name
#                         the name of the backup file for download/create/delete
# Author:
#   Stephen Bancroft
# Email:
#   stevereaver@gmail.com
#

import requests, json, pprint, sys, urllib3
from requests.auth import HTTPBasicAuth
from pprint import pprint
from optparse import OptionParser

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

PASSWORD = "<base64 encrypted username/password>"

parser = OptionParser()
parser.add_option("-t", "--hostname", 
                  action="store", dest="hostName",type="string",
                  help="hostname of VTM server")
parser.add_option("-o", "--operation",
                  action="store",dest="operation",type="string",
                  help="set type of operation, list/donwload/create/delete")
parser.add_option("-n", "--name",
                  action="store",dest="backupName",
                  help="name of the backup to download/create/delete")

(options, args) = parser.parse_args()

# Do some basic checking of the options
if not ((options.operation == 'list') or (options.operation == 'create') or (options.operation == 'download') or (options.operation == 'delete')):
    sys.exit("Operation must be one of: list, create, download.")

# Download backup
if options.operation == "download":
  http = urllib3.PoolManager()
  URL = 'https://'+options.hostName+':9070/api/tm/5.1/status/'+options.hostName+'/backups/full/'+options.backupName
  PATH = options.backupName+'.tar'
  headers = {'accept': 'application/x-tar', 'authorization': 'Basic '+PASSWORD}
  response = http.request('GET', URL, headers=headers, preload_content=False)
  with open(PATH, 'wb') as out:
    for chunk in response.stream(32):
        out.write(chunk)
  response.release_conn()

# Create a backup
if options.operation == "create":
  URL = 'https://'+options.hostName+':9070/api/tm/5.1/status/'+options.hostName+'/backups/full/'+options.backupName
  headers = {'Content-Type': 'application/json', 'authorization': 'Basic '+PASSWORD}
  data = {
           'properties': {
              'backup': {
                'description': '',
              }
            }
         }
  response = requests.put(URL, data=json.dumps(data), headers=headers, verify=False)
  if response.status_code != 201:
    print (response.status_code, response.reason)

# List avaliable backups
if options.operation == "list":
  URL = 'https://'+options.hostName+':9070/api/tm/5.1/status/'+options.hostName+'/backups/full'
  headers = {'Content-Type': 'application/json', 'authorization': 'Basic '+PASSWORD}
  response = requests.get(URL, headers=headers, verify=False)
  if response.status_code != 200:
    print (response.status_code, response.reason)
  print json.dumps (response.json(), sort_keys=True, indent=4, separators=(',', ': '))

# Delete avaliable backups
if options.operation == "delete":
  URL = 'https://'+options.hostName+':9070/api/tm/5.1/status/'+options.hostName+'/backups/full/'+options.backupName
  headers = {'Content-Type': 'application/json', 'authorization': 'Basic '+PASSWORD}
  response = requests.delete(URL, headers=headers, verify=False)
  if response.status_code != 204:
    print (response.status_code, response.reason)
