#!/usr/bin/python

import datetime
import json
import datetime
import sys
import json
import os
import shlex
import time
#import q

from cm_api.api_client import ApiResource
from cm_api.api_client import ApiException


args_file = sys.argv[1]
args_data = file(args_file).read()

arguments = shlex.split(args_data)
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
      cluster.get_parcel('CDH', cm_parcel_version)
      return
    except ApiException as err:
      #q.q('Error ')
      sys.exit(1)
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
#q.q('wait finished')

while True:
  #q.q('starting while')
  parcel = cluster.get_parcel('CDH', cm_parcel_version)

  state = parcel.stage;

  #q.q('>>>>>> Parcel status: ', state)

  if state == 'DISTRIBUTED':
    #q.q('DISTRIBUTED')
    parcel.activate()
  elif state == 'DOWNLOADED':
    #q.q('DOWNLOADED')
    parcel.start_distribution()
  elif state == 'ACTIVATED':
    #q.q('ACTIVATED')
    break;
  elif state == 'AVAILABLE_REMOTELY':
    #q.q('AVAILABLE_REMOTELY')
    parcel.start_download()

  if parcel.state.errors:
    raise Exception(str(parcel.state.errors))
  time.sleep(5)

print json.dumps({
    "failed" : False,
    "msg"    : "Parcel version %s present and distributed on cluster %s" % (cm_parcel_version, cluster_name)
})

sys.exit(0)

