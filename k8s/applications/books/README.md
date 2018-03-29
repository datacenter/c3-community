# Service Catalog and GCP Broker Demo

## Prereqs

- Installed and in your PATH:
  - [Helm](https://github.com/kubernetes/helm)
  - `gcloud`
  - `kubectl`

- You are logged in with `gcloud`. If not, run the following and follow the
  instructions:
  ```
  gcloud auth login
  ```

- Your default `gcloud` project is set to the project you intend to use for this
demo. To do so, run the following:
  ```
  gcloud config set project ${YOUR-PROJECT-HERE}
  ```

## Deploy the Service Catalog and GCP Broker

To install the Service Catalog in your cluster and connect with the GCP Broker,
you should follow the instructions in the
GoogleCloudPlatform/k8s-service-catalog project
[here](https://github.com/GoogleCloudPlatform/k8s-service-catalog).

## K8S Broker

This project uses a custom build of the
[Helm Broker](https://github.com/google/helm-broker) to install demo-specific
service instances in your cluster.

Create the actual broker resources in Kubernetes:

```
kubectl create -f k8s_broker/k8s-broker.yaml
```

Connect the K8S Broker to the Service Catalog:

```
kubectl create -f demo/k8s-broker.yaml
```

## Creating Instances and Bindings

Create the instances and bindings used in the demo:

```
kubectl create -f demo/demo-setup-instances.yaml
kubectl create -f demo/demo-setup-purchases-bindings.yaml
kubectl create -f demo/demo-setup-app-bindings.yaml
```

## Installing the app

Install the main "Books! Books! Books!" web app:

```
helm install app/app --name app
```

Access the app:

1) Find the external IP for the app
```
kubectl get services booksfe
APP_IP=XXX.XXX.XX.XX # Use the IP listed under the EXTERNAL-IP column
```

2) Visit the app in your browser at: http://${APP_IP}:8080/

You should see a list of eight books with a button that says "Purchase" beside
each. If you click "Purchase", that book will be added to your list of
Purchases, which you can view by clicking the tab at the top.

## Connecting the demo app with Google Cloud Pub/Sub
Now we're going to connect this app to Google Cloud Pub/Sub to see when
purchases are made. In this new version, when you buy a book, the app
will publish a message to the topic created by the binding.

### Installation:

#### IAM Service Account:
To connect an application with Google Cloud services, you must first create a
service account. This may be done using the IAM service class.

Create the IAM instance:
```
kubectl create -f demo/gcp-iam-instance.yaml
```

To get the name and credentials for this service account we created, you can
then create a binding to it.

Create the IAM binding:
```
kubectl create -f demo/gcp-iam-binding.yaml
```

#### Google Cloud Pub/Sub Service Instance:
Now that we have a service account that lets us use GCP services, let's hook our
application into Pub/Sub.

Create the Pub/Sub instance:
```
kubectl create -f demo/gcp-pubsub-instance.yaml
```

**NOTE**: A Pub/Sub binding requires the user to pass the name of the service
account it wishes to give the requested role to. For the time being, we must
manually reference the service account created by the IAM service instance. It
will have a name of the format
"sa-sb-XXXXXXXX-XXXX-XXXX-XXXX@${PROJECT_NAME}.iam.gserviceaccount.com". You may
find this through the Google Cloud dashboard under "IAM & admin > Service
accounts", or by base64-decoding the `serviceAccount` field of the
`gcp-iam-credentials` secret created by the IAM binding. Once you have this,
replace `## INSERT SERVICE ACCOUNT HERE ##` in `gcp-pubsub-binding.yaml` with
the service account name. This will be made much easier in a future update to
the Service Catalog which will support sourcing parameters directly from secrets
in a format compatible with the GCP Broker.

Create the Pub/Sub binding:
```
kubectl create -f demo/gcp-pubsub-binding.yaml
```

#### Upgrade the Application:
Now, redeploy the application, this time telling it to use Pub/Sub:

```
helm upgrade app app/app --set "usePubsub=true"
```

### Using the app

To view messages published by the app, first you should create a subscription on
the topic generated by the Pub/Sub instance. This may be done easily via the GCP
UI. After creating this subscription, click "Purchase" for a couple books, and
run the following command multiple times (replacing `${SUBSCRIPTION_NAME}` with
the name of the subscription you created:

```
gcloud beta pubsub subscriptions pull ${SUBSCRIPTION_NAME} --auto-ack
```

You should see messages appear that correspond to those purchases.