# Overview

<b>dataflow-mvp</b> provides a basic example pipeline that pulls data from an API and writes it to a BigQuery table using GCP's Dataflow (i.e., Apache Beam)

# Table of Contents

| File | Description |
|--|--|
|`main.py` | Main Python code for the Dataflow pipeline. The function `defineBQSchema` defines the BQ table schema|
|`setup.py` | When the pipeline is deployed in GCP as a template, GCP uses `setup.py` to set up the worker nodes (e.g., install required Python dependencies).|
|`build.bat`| Bash script to deploy the pipeline as a reusable template in GCP.|

# Environment

* Local machine running Microsoft Windows 10 Home
* Python 3.6.8
  * As of 12/1/21, Apache Beam only supports 3.6, 3.7, and 3.8 (not 3.9). However, <code>orjson</code> only supports 3.6.

# Getting Started

## Pre-Requisites

The following instructions assume that the project ID is `dataflow-mvp` and you have owner access to it.

1. If you don't have it already, install the Google Cloud SDK:<br>
[https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)

2. Authenticate your Google account:<br>
`gcloud auth login`

3. Create a virtual environment for Python:<br>
<code>py -3.8 venv venv</code>

4. Activate the virtual environment, upgrade pip, and install the Apache Beam library for GCP:<br>
```
"./venv/Scripts/activate.bat"
python -m pip install --upgrade pip
python -m pip install apache_beam[gcp]
```

## Run Build

5. To make our lives easier later, set environment variables for the following:<br>
* DATAFLOW_BUCKET - the name of the bucket from step 10
* DF_TEMPLATE_NAME - the name (of your choosing) for the Dataflow template (e.g., dataflow-mvp-dog)
* PROJECT_ID - the name of the GCP project from step 4 (e.g., dataflow-mvp)
* GCP_REGION - the GCP region (I like to choose the region closest to me e.g., useast-1)

For instance, to set the <code>PROJECT_ID</code> variable in the Windows CLI, use:<br>
`set PROJECT_ID=dataflow-mvp`

On Linux machines, use<br>
`export PROJECT_ID=dataflow-mvp`

The instructions below assume you're working on a Windows machine. Therefore, if you're working in a Linux environment, you'll have to use `$PROJECT_ID` instead of `%PROJECT_ID%` where appropriate in the instructions below.

6. Set the GCP project via config:<br>
`gcloud config set project %PROJECT_ID%`
* You can verify the project is correctly set using:<br>
`gcloud config list`

7. Enable the necessary APIs:
```
gcloud services enable dataflow.googleapis.com && ^
gcloud services enable cloudscheduler.googleapis.com && ^
gcloud services enable bigquery.googleapis.com && ^
gcloud services enable cloudresourcemanager.googleapis.com  && ^
gcloud services enable appengine.googleapis.com
```

8. Create a service account for the Dataflow runner:
```
gcloud iam service-accounts create dataflow-runner --display-name "Dataflow Runner service account"
```

9. Add the required IAM roles to the Dataflow runner's service account:
```
gcloud projects add-iam-policy-binding %PROJECT_ID% --member serviceAccount:dataflow-runner@%PROJECT_ID%.iam.gserviceaccount.com --role roles/owner
```

10. Create a GCS bucket to store Dataflow code, staging files and templates:<br>
```
gsutil mb -p %PROJECT_ID% -l %GCP_REGION% gs://%DATAFLOW_BUCKET%
```

## Build the Dataflow Template

11. In <code>build.bat</code>, edit the variables in lines 1 through 4:
* DATAFLOW_BUCKET - the name of the bucket from step 10
* DF_TEMPLATE_NAME - the name (of your choosing) for the Dataflow template (e.g., dataflow-mvp-dog)
* PROJECT_ID - the name of the GCP project from step 4 (e.g., dataflow-mvp)
* GCP_REGION - the GCP region (I like to choose the region closest to me e.g., useast-1)

12. Run the <code>build.bat</code> script:
```
build.bat
```

This will create the template for the Dataflow job in a the specified GCS bucket.

13. Verify that the template has been uploaded to the GCS bucket:<br>
`gsutil ls gs://%DATAFLOW_BUCKET%/templates/%DF_TEMPLATE_NAME%`

## Create the Cloud Scheduler Job

14. Finally, submit a Cloud Scheduler job to run Dataflow on a desired schedule:<br>
```
gcloud scheduler jobs create http api-to-gbq-scheduler ^
--schedule="0 */3 * * *" ^
--uri="https://dataflow.googleapis.com/v1b3/projects/%PROJECT_ID%/locations/%GCP_REGION%/templates:launch?gcsPath=gs://%DATAFLOW_BUCKET%/templates/%DF_TEMPLATE_NAME%" ^
--http-method="post" ^
--oauth-service-account-email="dataflow-runner@%PROJECT_ID%.iam.gserviceaccount.com" ^
--oauth-token-scope="https://www.googleapis.com/auth/cloud-platform" ^
--message-body="{""jobName"": ""api-to-bq-df"", ""parameters"": {""region"": ""%GCP_REGION%""}, ""environment"": {""numWorkers"": ""3""}}" ^
--time-zone=America/Chicago 
```

Notes:<br>
* Alternatively, you could use the <code>message-body-from-file</code> argument. However, you'll need to manually specify the GCP region since we can't use environment variables within the JSON.
* The cron string <code>0 */3 * * *</code> executes the job every 3 hours.
* The <code>jobName</code> parameter, <code>api-to-bq-df</code>, names the job as it will be listed in the Cloud Scheduler app.

# Resources

* Writing to BigQuery<br>
[https://beam.apache.org/documentation/io/built-in/google-bigquery/](https://beam.apache.org/documentation/io/built-in/google-bigquery/)
* BigQuery data limitations<br>
[https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json#limitations](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json#limitations)
* Loading nested and repeated JSON data<br>
[https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json#loading_nested_and_repeated_json_data](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json#loading_nested_and_repeated_json_data)
* Passing values/parameters to the API<br>
[https://stackoverflow.com/questions/65582147/apache-beam-pipeline-to-read-from-rest-api-runs-locally-but-not-on-dataflow](https://stackoverflow.com/questions/65582147/apache-beam-pipeline-to-read-from-rest-api-runs-locally-but-not-on-dataflow)

# Warranty

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
