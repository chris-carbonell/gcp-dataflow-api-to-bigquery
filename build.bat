set DATAFLOW_BUCKET=dataflow-mvp-dataflow-bucket
set DF_TEMPLATE_NAME=dataflow-mvp-dog
set PROJECT_ID=dataflow-mvp
set GCP_REGION=us-central1

echo:
echo "*** Building Dataflow Template **"
echo "Bucket: %DATAFLOW_BUCKET%"
echo "Project ID: %PROJECT_ID%"
echo "Dataflow Region: %GCP_REGION%"
echo "***"
echo "***"
echo "***"

echo:
echo "activating venv"
"./venv/Scripts/actiate.bat"

echo:
echo "main.py"
python main.py ^
--region %GCP_REGION% ^
--runner DataflowRunner ^
--project %PROJECT_ID% ^
--temp_location gs://%DATAFLOW_BUCKET%/temp/ ^
--staging_location gs://%DATAFLOW_BUCKET%/staging ^
--template_location gs://%DATAFLOW_BUCKET%/templates/%DF_TEMPLATE_NAME% ^
--autoscaling_algorithm NONE ^
--setup_file ./setup.py ^
--job_name api-to-gbq-df ^
--num_workers 3