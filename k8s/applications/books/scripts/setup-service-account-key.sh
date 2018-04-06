#!/bin/bash

set -eu

echo "Using GCP project: ${GCP_PROJECT}"
echo "Using service account: ${SERVICE_ACCOUNT_NAME}"

SECRET_NAME="${SECRET_NAME:-"gcp-service-account-key"}"
echo "Using secret name: ${SECRET_NAME}"

NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1)
DIR="/tmp/sc-bookstore-demo${NEW_UUID}"

echo "Making directory ${DIR}"
mkdir ${DIR}

echo "Creating key to service account ${SERVICE_ACCOUNT_NAME} in ${DIR}"
gcloud iam service-accounts keys create ${DIR}/key.json \
  --iam-account ${SERVICE_ACCOUNT_NAME}@${GCP_PROJECT}.iam.gserviceaccount.com

echo "Creating secret ${SECRET_NAME}"
kubectl create secret generic ${SECRET_NAME} --from-file=key.json="${DIR}/key.json"
