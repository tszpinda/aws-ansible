#!/usr/bin/python

import datetime
import json
import datetime
import sys
import json
import os
import shlex
import time

from cm_api.api_client import ApiResource
from cm_api.api_client import ApiException


args_file = sys.argv[1]
args_data = file(args_file).read()

print 'args_file: %s' %args_file
print 'args_data: %s' %args_data

arguments = shlex.split(args_data)
print "%s" % arguments
cm_host = ""
cluster_name = ""
cm_cluster_version = ""
cm_parcel_version = ""


for arg in arguments:
    if "=" in arg:
        (key, value) = arg.split("=")
        if key == 'host':
            cm_host = value
        if key == 'clusterName':
            cluster_name = value
        if key == 'clusterVersion':
            cm_cluster_version = value
        if key == 'parcelVersion':
            cm_parcel_version = value

if cm_host == "" or cluster_name == "" or cm_cluster_version == "" or cm_parcel_version == "":
    print json.dumps({
        "failed" : True,
        "msg"    : "All parameters are required: host, clusterName, clusterVersion and parcelVersion"
    })
    sys.exit(1)


def waitUntilParcelFound():
  countDown = 1
  while True:
    try:
      print "parcel found..."
      cluster.get_parcel('CDH', cm_parcel_version)
      print "parcel found"
      break
    except ApiException as err:
      if err.code == 404 and countDown > 0:
        countDown = countDown -1
        time.sleep(3)
      else:
        print json.dumps({
            "failed" : True,
            "msg"    : "CDH parcel not found - version %s on cluster %s" % (cm_parcel_version, cluster_name),
            "extras" : err
        })
        sys.exit(1)


api = ApiResource(cm_host, username="admin", password="admin")
cluster = api.get_cluster(cluster_name)
waitUntilParcelFound()

while True:
  parcel = cluster.get_parcel('CDH', cm_parcel_version)
  print "parcel"
  print parcel.state
  if parcel.stage == 'DISTRIBUTED':
    parcel.activate()
    break;
  elif parcel.stage == 'DOWNLOADED':
    parcel.start_distribution()
  elif parcel.stage == 'ACTIVATED':
    break;
  elif parcel.state == 'AVAILABLE_REMOTELY':
    parcel.start_download()

  if parcel.state.errors:
    raise Exception(str(parcel.state.errors))
  time.sleep(5)

print json.dumps({
    "failed" : False,
    "msg"    : "Parcel version %s present and distributed on cluster %s" % (cm_parcel_version, cluster_name)
})

sys.exit(0)

