#If u have a requirement to monitor critical lambdas and quickly get notified via slack. 
# 1. Then, go to your lambda and click on add destination, Soure(Async), Condition(On-Failure), Destination type - lambda and provide this lambda name.
# 2. If you want to get notified for the critical exceptions for a lambda in your code then, you have to come to this lambda and click on Add trigger
# 3. Select cloudwatch log and provide the log group of the lambda that you want to monitor
# 4. Provide any name for your filter and provide filter pattern such as ?error ?failure etc,..
# 5. So whenever your source lambda has these filters in that log group then that will be caught by this lambda and will get notified to slack or any other medium you prefer.
# 6. Note: here i have used webhook url and even if you want to use slack token it is absolutely fine.

import requests, json
from datetime import datetime
import base64
import boto3
import gzip
import json
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def logpayload(event):
    logger.setLevel(logging.DEBUG)
    logger.debug(event['awslogs']['data'])
    compressed_payload = base64.b64decode(event['awslogs']['data'])
    uncompressed_payload = gzip.decompress(compressed_payload)
    log_payload = json.loads(uncompressed_payload)
    return log_payload


def error_details(payload):
    error_msg = ""
    log_events = payload['logEvents']
    logger.debug(payload)
    loggroup = payload['logGroup']
    logstream = payload['logStream']
    lambda_func_name = loggroup.split('/')
    logger.debug(f'LogGroup: {loggroup}')
    logger.debug(f'Logstream: {logstream}')
    logger.debug(f'Function name: {lambda_func_name[3]}')
    logger.debug(log_events)
    for log_event in log_events:
        error_msg += log_event['message']
    logger.debug('Message: %s' % error_msg.split("\n"))
    return loggroup, logstream, error_msg, lambda_func_name

URL= 'web-hook-url'

def lambda_function(data, context):

    output = data
    print(output)
    headers = {'Content-Type': 'application/json'}

    if 'awslogs' in output: #coming from lambda trigger
        pload = logpayload(data)
        lgroup, lstream, errmessage, lambdaname = error_details(pload)
        final_out = f'''*Lambda function* `{lambdaname}` *failed* in `aws-acct-name`
`ErrorMessage`: {errmessage}
`Log Group`: {lgroup}
`Log Stream`: {lstream}
`Logs`: 'Logfile'
'''
    else: #lambda failure
        error_Msg = output['responsePayload']['errorMessage']
        final_out = f'''*Lambda function* `lambda-name` *failed* in `aws-acct-name`
`ErrorMessage`: {error_Msg}
`Time`: {datetime.now()}
`Logs`: 'Logfile'
'''

    details = {
        'text': final_out
    }

    res = requests.post(url=URL, data=json.dumps(details), headers=headers)

    if res.status_code == 200:
        print("Successful Completion", data)


