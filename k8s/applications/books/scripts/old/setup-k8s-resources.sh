#!/bin/bash

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

. "${ROOT}/contrib/hack/utilities.sh" || { echo "Could not load utilities."; exit 1; } 

echo "Creating brokers..."

kubectl create -f "${ROOT}/demo/demo/demo-setup-brokers.yaml"

wait_for_expected_output -e "inventory" kubectl get serviceclasses \
  || error_exit "Could not find expected service classes."
wait_for_expected_output -e "purchases" kubectl get serviceclasses \
  || error_exit "Could not find expected service classes."
wait_for_expected_output -e "user-provided-service" kubectl get serviceclasses \
  || error_exit "Could not find expected service classes."
wait_for_expected_output -e "users" kubectl get serviceclasses \
  || error_exit "Could not find expected service classes."

sleep 5

echo "Creating payments service (user-provided)..."

kubectl create -f "${ROOT}/demo/demo/demo-setup-ups.yaml" \
  || error_exit "Could not set up payments service."

wait_for_expected_output -e "payments" kubectl get pods

sleep 5

echo "Creating service instances..."

kubectl create -f "${ROOT}/demo/demo/demo-setup-instances.yaml"

wait_for_expected_output -e "users" kubectl get pods \
  || error_exit "Could not find expected pod for service instance."
wait_for_expected_output -e "inventory" kubectl get pods \
  || error_exit "Could not find expected pod for service instance."
wait_for_expected_output -e "purchases" kubectl get pods \
  || error_exit "Could not find expected pod for service instance."
wait_for_expected_output -e "payments" kubectl get pods \
  || error_exit "Could not find expected pod for service instance."

sleep 5

echo "Creating bindings..."

kubectl create -f "${ROOT}/demo/demo/demo-setup-bindings.yaml"

wait_for_expected_output -e "purchases-users" kubectl get secrets \
  || error_exit "Could not find expected secret from binding."
wait_for_expected_output -e "purchases-inventory" kubectl get secrets \
  || error_exit "Could not find expected secret from binding."
wait_for_expected_output -e "purchases-payments" kubectl get secrets \
  || error_exit "Could not find expected secret from binding."

sleep 5

echo "Waiting for bindings to take effect..."

wait_for_expected_output -x -e "RunContainerError" kubectl get pods \
  || error_exit "Error when creating pods."

echo "All resources up. Confirm the following looks appropriate."

kubectl get serviceclasses,pods,secrets
