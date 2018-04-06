#!/bin/bash

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

. "${ROOT}/k8s_broker/utilities.sh" || { echo 'Cannot load bash utilities.'; exit 1; }

echo "Setting up registry..."

REGISTRY_HOST="$(KUBECONFIG="${KUBECONFIG}" kubectl get services -n k8s-broker | grep 'registry' | awk '{print $3}')"

[[ "${REGISTRY_HOST}" =~ ^[0-9.]+$ ]] \
  || error_exit 'Error when fetching registry IP address.'

echo "Using Registry IP: ${REGISTRY_HOST}"

curl -X POST -d @- "${REGISTRY_HOST}:8001/services" < "${ROOT}/k8s_broker/definitions/users.json" \
  || error_exit "Could not create users class definition."
curl -X POST -d @- "${REGISTRY_HOST}:8001/services" < "${ROOT}/k8s_broker/definitions/inventory.json" \
  || error_exit "Could not create inventory class definition."
curl -X POST -d @- "${REGISTRY_HOST}:8001/services" < "${ROOT}/k8s_broker/definitions/purchases.json" \
  || error_exit "Could not create purchases class definition."

echo "Registry definitions updated."
