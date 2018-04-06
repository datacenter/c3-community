#!/bin/bash

kubectl delete servicebrokers,serviceclasses,serviceinstancecredentials,serviceinstances,secrets,configmaps --all
helm list | grep -v catalog-0.0 | grep -v NAME | awk '{print $1}'  | xargs helm delete
