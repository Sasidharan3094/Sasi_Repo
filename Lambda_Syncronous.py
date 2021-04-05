import json
import boto3
#This is a simple Lambda for our Slack application to return 200 asap
client = boto3.client('lambda')
def lambda_handler(event, context):
    # Calls the Main Lambda and responds 200 async asap
    resp = client.invoke(
        FunctionName='', #Arn of our second or asynchronous lambda
        InvocationType='Event',
        Payload=json.dumps(event)
        )
    return {
        'statusCode': 200,
        'body': json.dumps('Success, Received payload')
    }
