import json
import os
import time
import boto3
import base64
import paramiko
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    secret_name = "INC_APP"
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        output = json.loads(get_secret_value_response['SecretString'])['Value']
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        print(e)

   
    out_lis = output.split(' ')
    out = ''
    for i in out_lis:
        out = out + i + '\n'
    
    #The extracted data from secret manager will not be in correct format and hence using the above to make it in expected format to decode it.

    f = open("/tmp/pri_encoded", "w")
    f.write(out)
    f.close()
    
    #Writing the key in /tmp folder as that is the only mount which is read/write in Lambda and rest all are Read-only.

    command = f'''base64 -d /tmp/pri_encoded > /tmp/Sas-key.pem'''
    os.popen(command)
    command = f'''chmod 400 /tmp/Sas-key.pem'''
    print(os.popen(command).read())
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    #Provide your machine ip
    
    ssh.connect('machine-ip', username='ec2-user', key_filename='/tmp/Sas-key.pem')
    
    #Running basic commands just for testing.
    stdin, stdout, stderr = ssh.exec_command('pwd; ls -lrt; date')
    
    #Giving an optional sleep 5 secs for connection to be established as it is inisde VPC.
    time.sleep(5)
    lines = stdout.readlines()
    host_output = ''
    for l in lines:
        host_output = host_output + l + '\n'

    #Once the program is ended, delete the pem file. Again this is not needed and optional. Just for safer side.
    command = f'''rm -f /tmp/Sas-key.pem /tmp/pri_encoded'''
    print(os.popen(command).read())

    final_output = f'''Connected to machine-ip via ec2-user \n{host_output}'''
    
    #Returing the output of our basic command to print it in Lambda
    return final_output
