#!/bin/bash

set -o nounset
set -o errexit

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

kubectl create \
  -f ${ROOT}/demo/k8s-broker.yaml \
  -f ${ROOT}/demo/demo-setup-instances.yaml \
  -f ${ROOT}/demo/demo-setup-purchases-bindings.yaml \
  -f ${ROOT}/demo/demo-setup-app-bindings.yaml
