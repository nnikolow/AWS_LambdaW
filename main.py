import json
import urllib.parse
import boto3
import requests
import os
import time

api_key = "db94967ec9dd601275593f8207eb3124"
lat = "43.206113"
lon = "27.919950"
url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}".format(lat, lon, api_key)
s3 = boto3.client('s3')

current_time = int(time.time())


def lambda_handler(event, context):
    global current_time

    def actual_call():
        global last_run

        response = requests.get(url)
        data = json.loads(response.text)

        f = open("/tmp/json_from_api.json", "w")
        f.write(str(data))
        f.close()

        try:
            # saving the value in a file
            o = open("/tmp/last_run.txt", "w")
            o.write(str(last_run))
            o.close()

            # upload the last_run value to s3
            with open("/tmp/last_run.txt", "rb") as o:
                s3.upload_fileobj(o, "deploy-bucket-nn", "last_run")

            # uploading the .json file to s3
            with open("/tmp/json_from_api.json", "rb") as f:
                s3.upload_fileobj(f, "deploy-bucket-nn", "test_file_from_api_final")
                last_run = int(time.time())
                return "File was uploaded successfully!"
        except:
            return "File uploading failed."

    # reading the contents of last_run from the bucket
    bucket_name = "deploy-bucket-nn"
    file_to_read = "last_run"
    fileobj = s3.get_object(
        Bucket=bucket_name,
        Key=file_to_read
    )
    filedata = fileobj['Body'].read()
    last_run_contents = filedata.decode('utf-8')

    # check if function is ran within the last hour
    if int(last_run_contents) - current_time >= 3600:
        return actual_call()
    else:
        return "Function was called in the last hour."

