#!/bin/bash

APPNAME=`helm list | grep app-0.0.2 | awk '{print $1}'`
helm upgrade $APPNAME app/app --set "version=${VERSION}"
