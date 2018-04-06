#!/bin/bash

set -e

docker build ../app -t "gcr.io/sc-bookstore-demo/app:test"
gcloud docker -- push "gcr.io/sc-bookstore-demo/app:test"
