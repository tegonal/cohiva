#!/bin/bash

## Read .env
if [ -r .env ] ; then
    export $(grep -v '^#' .env | xargs)
fi

## Start deploy trigger script
#./autodeploy.py &
#AUTODEPLOY_PID=$!

if [ -z ${COHIVA_DEV_PORT+x} ] ; then
    COHIVA_DEV_PORT=8000
    echo "Using default port $COHIVA_DEV_PORT (set COHIVA_DEV_PORT in .env to change this)."
fi
./manage.py runserver $COHIVA_DEV_PORT

## Stop autodeploy
#kill $AUTODEPLOY_PID

# IPv4
#./manage.py runserver 213.144.138.106:8080

# IPv6
#./manage.py runserver -6 "[2001:1620:206b::10:1]:8080"
