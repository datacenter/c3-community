#!/bin/bash

set -eu

gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} --display-name "Service account for Service Catalog bookstore demo"
