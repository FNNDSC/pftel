# This script describes by way of demonstration various explicit examples of
# how to interact with the pftel API using curl -s.
#
#   $ source \$PWD/workflow
#
# MAKE SURE ANY ENV VARIABLES SET BY THIS ARE WHAT YOU WANT!
#
#     * Feb-2023 -> 08-Jan-2022
#     Develop/deploy.
#

###############################################################################
#_____________________________________________________________________________#
# E N V                                                                       #
#_____________________________________________________________________________#
# Set the following variables appropriately for your local setup.             #
###############################################################################

#
# pftel service
#
# In some envs, this MUST be an IP address!
export PFTEL=http://localhost:22223


# Directory mounts etc
export DB=/home/dicom/log
export DATADIR=/home/dicom/data
export BASEMOUNT=/home/dicom

###############################################################################
#_____________________________________________________________________________#
# B U I L D                                                                   #
#_____________________________________________________________________________#
# Build the container image in a variety of difference contexts/use cases.    #
###############################################################################

build () {
# UID
# for fish:
# export UID=(id -u)
# for bash/zsh
export UID=$(id -u)
# Build (for fish shell syntax!)
docker build --build-arg UID=$UID -t local/pftel .
}

launch_quickndirty () {
# Quick 'n dirty run -- this is what you'll mostly do.
# Obviously change port mappings if needed (and in the Dockerfile)
docker run --rm -it                                                            \
        -p 4005:4005 -p 10402:11113 -p 11113:11113                             \
        local/pftel /start-reload.sh
}

launch_qndwithdb () {
# Quick 'n dirty run -- with volume mapping.
# Obviously change port mappings if needed (and in the Dockerfile)
docker run --rm -it                                                            \
        -p 4005:4005 -p 10402:11113 -p 11113:11113                             \
        -v /home/dicom:/home/dicom                                             \
        local/pftel /start-reload.sh
}

launch_debug () {
# Run with support for source debugging
docker run --rm -it                                                            \
        -p 4005:4005 -p 10402:11113 -p 11113:11113                             \
        -v /home/dicom:/home/dicom                                             \
        -v $PWD/pftel:/app:ro                                                  \
        local/pftel /start-reload.sh
}

# To access the API swagger documentation, point a brower at:
export swaggerURL=":22223/docs"

###############################################################################
#_____________________________________________________________________________#
# L O G G E R   s e t u p                                                     #
#_____________________________________________________________________________#
###############################################################################
# Setup write some telemetry to the DB from CLI.                              #
###############################################################################
#
# POPULATE DB WITH EVENTS
#
# Here we POST several events to the DB and then afterwards GET various
# API elements.
#
# POST the events with
#
# $ mha-to-dcm <obj> <collection> <time>
# $ inference <obj> <collection> <time>
# $ measure <obj> <collection> <time>
# $ push_to_PACS <obj> <collection> <time>
#
# GET information with
#
# $ logObj_list
# $ logCollections_list <obj>
# $ logEvents_list <obj> <collection>
# $ logEvent_get <obj> <collection> <event>
#

logObj_create () {
  obj=$1
  curl -s -X 'PUT' \
    "$PFTEL/api/v1/log/$obj/" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "url": "http://localhost:2223",
    "username": "any",
    "password": "any",
    "dbDir": "/home/dicom",
    "telemetryDir": "telemetry",
    "description": "A log object for testing"
  }' | jq
}

mha-to-dcm () {
  obj=$1
  collection=$2
  time=$3
  curl -s -X 'POST' \
    "$PFTEL/api/v1/log/" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
      "logObject": "'$obj'",
      "logCollection": "'$collection'",
      "logEvent": "mha-to-dicom",
      "appName": "pl-mha2dicom",
      "execTime": '$time',
      "extra": ""
    }' | jq
}

inference () {
  obj=$1
  collection=$2
  time=$3
  curl -s -X 'POST' \
    "$PFTEL/api/v1/log/" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
      "logObject": "'$obj'",
      "logCollection": "'$collection'",
      "logEvent": "heatmaps",
      "appName": "pl-LLD_infertence",
      "execTime": '$time',
      "extra": ""
    }' | jq
}

measure () {
  obj=$1
  collection=$2
  time=$3
  curl -s -X 'POST' \
    "$PFTEL/api/v1/log/" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
      "logObject": "'$obj'",
      "logCollection": "'$collection'",
      "logEvent": "measure",
      "appName": "pl-legMeas",
      "execTime": '$time',
      "extra": ""
    }' | jq
}

push_to_PACS () {
  obj=$1
  collection=$2
  time=$3
  curl -s -X 'POST' \
    "$PFTEL/api/v1/log/" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
      "logObject": "'$obj'",
      "logCollection": "'$collection'",
      "logEvent": "push-to-pacs",
      "appName": "pl-orthanc_push",
      "execTime": '$time',
      "extra": ""
    }' | jq
}

logObj_list () {
  curl -s -X 'GET' \
    "$PFTEL/api/v1/log/" \
    -H 'accept: application/json' | jq
}

logCollections_list () {
  obj=$1
  curl -s -X 'GET' \
    "$PFTEL/api/v1/log/$obj/collections/" \
    -H 'accept: application/json' | jq
}

logEvents_list () {
  obj=$1
  collection=$2
  curl -s -X 'GET' \
    "$PFTEL/api/v1/log/$obj/$collection/events/" \
    -H 'accept: application/json' | jq
}

logEvent_get () {
  obj=$1
  collection=$2
  event=$3
  curl -s -X 'GET' \
    "$PFTEL/api/v1/log/$obj/$collection/$event/" \
    -H 'accept: application/json' | jq
}

logEvent_getAll () {
  obj=$1
  collection=$2
  curl -s -X 'GET' \
    "$PFTEL/api/v1/log/$obj/$collection/" \
    -H 'accept: application/json' | jq
}

logEvent_getAllAsCSV () {
  obj=$1
  collection=$2
  RESP=$(curl -s -X 'GET' \
    "$PFTEL/api/v1/log/$obj/$collection/csv" \
    -H 'accept: application/json')
  echo -n $RESP | tr -d '"'
}

test_feedLog () {
  obj=$1
  collection=$2
  logObj_create   $obj
  mha-to-dcm      $obj $collection 0.353
  inference       $obj $collection 12.345
  measure         $obj $collection 4.234
  push_to_PACS    $obj $collection 3.2
}

#
# And we're done!
# _-30-_
#