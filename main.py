#!/usr/bin/env python3
# coding: utf-8

#
# See setup.py for required dependencies.
#
# Run Locally:
# python3 main.py --temp-location <pre-existing GCS bucket>
#
# Run on GCP Dataflow
# python3 main.py \
# --region us-west2 \ # Use your preferred region
# --runner DataflowRunner \
# --project <project-id> \
# --temp_location <pre-existing GCS bucket> \
# --staging_location <pre-existing GCS bucket> \
# --autoscaling_algorithm NONE \
# --num_workers 1 \
# --setup_file ./setup.py \
# --job_name api-to-bq
#
#####
import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io.gcp.internal.clients import bigquery
import logging

class get_api_data(beam.DoFn):
    def __init__(self):
        logging.debug("fetching api data")

    def process(self,element):
        import requests

        api_url = "https://api.thedogapi.com/v1/breeds/"

        # if the api needs authentication
        #bearer_token = "api_secret"
        # headers = {
        #           'Content-Type': 'application/json',
        #           'Authorization': 'Bearer ' + bearer_token,
        #           'Accept': 'application/json',
        #           'Content-Type': 'application/json'
        #           }
        #response = requests.post("api_url", headers=headers)

        logging.debug("Now fetching from ", api_url)

        response = requests.get(api_url)
        for dog in response.json():
            # Building the json object here to abstract upstream api changes
            # In the event the upstream api changes, the below structure might
            # need to be retrofitted
            retval = {
                "id": dog["id"],
                "name": dog["name"],
                "weight": dog["weight"],
                "height": dog["height"],
                "life_span": dog["life_span"],
                "reference_image_id": dog["reference_image_id"],
                "image": dog["image"]
                }
            yield retval

def defineBQSchema():
    table_schema = {
    'fields':
        [
            {
                'name': 'weight', 'type': 'RECORD', 'mode': 'REPEATED',
                    'fields': [{'name':'imperial','type':'STRING','mode':'NULLABLE'},
                                {'name':'metric','type':'STRING','mode':'NULLABLE'}]
            },
            {
                'name': 'height', 'type': 'RECORD', 'mode': 'REPEATED',
                    'fields': [{'name':'imperial','type':'STRING','mode':'NULLABLE'},
                                {'name':'metric','type':'STRING','mode':'NULLABLE'}]
            },
            {
                'name': 'id', 'type': 'INTEGER', 'mode': 'REQUIRED'
            },
            {
                'name': 'name', 'type': 'STRING', 'mode': 'NULLABLE'
            },
            {
                'name': 'life_span', 'type': 'STRING', 'mode': 'NULLABLE'
            },
            {
                'name': 'reference_image_id', 'type': 'STRING', 'mode': 'NULLABLE'
            },
            {
                'name': 'image', 'type': 'RECORD', 'mode': 'REPEATED',
                    'fields': [{'name':'height','type':'INTEGER','mode':'NULLABLE'},
                                {'name':'id','type':'STRING','mode':'NULLABLE'},
                                {'name':'url','type':'STRING','mode':'NULLABLE'},
                                {'name':'width','type':'INTEGER','mode':'NULLABLE'}]
            },
        ]
    }

    return table_schema


def run(argv=None):

    parser = argparse.ArgumentParser()
    known_args, pipeline_args = parser.parse_known_args()
    pipeline_options = PipelineOptions(pipeline_args)

    # BigQuery Table details
    table_spec = bigquery.TableReference(
        projectId='dataflow-mvp',
        datasetId='api_dump',
        tableId='dogs'
    )

    with beam.Pipeline(options=pipeline_options) as pipeline:

        ingest_data = (
            pipeline
            | 'Create' >> beam.Create(['Start'])  # workaround to kickstart the pipeline
            | 'fetch API data' >> beam.ParDo(get_api_data())
            #| 'write to text' >> beam.io.WriteToText("./results.txt")
            # Uncomment the above to generate the output file locally if needed
            | 'write into gbq' >> beam.io.WriteToBigQuery(table = table_spec, schema=defineBQSchema(), write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE ,create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED)
        )

        result = pipeline.run()

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
