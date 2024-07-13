import boto3
#import pymongo
#from pymongo import MongoClient
import os


def launch_ec2_instance():
    instanceName = input("Please enter ec2 instance name you want to create: ")
    defaultRegion = 'ap-south-1'
    ec2 = boto3.resource('ec2',defaultRegion)
    
    instance = ec2.create_instances(
        ImageId='ami-022ce6f32988af5fa', 
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro', 
        KeyName='aws',
        TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': instanceName
                }
            ]
        }
    ]
    )
    # Print the instance ID
    print(f'EC2 Instance created with ID: {instance[0].id}')
    pass

def create_rhel_gui_instance():
    # Create a new EC2 resource
    rhelInstanceName = input("Please enter RHEL GUI ec2 instance name: ")
    ec2 = boto3.resource('ec2')

    # Define the instance parameters
    instances = ec2.create_instances(
        ImageId='ami-022ce6f32988af5fa', 
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='aws',
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': rhelInstanceName  # Replace with your desired instance name
                    }
                ]
            }
        ],
        UserData='''#!/bin/bash
            yum -y groupinstall "Server with GUI"
            systemctl set-default graphical.target
            yum -y install tigervnc-server
            vncserver :1
            systemctl enable vncserver@:1.service
            systemctl start vncserver@:1.service
            '''
        )

    # Print the instance ID
    print(f'Your RHEL GUI Instance ID: {instances[0].id}')
    pass

def access_log_from_cloud():
    logs = get_log_events_from_log_group('/aws/lambda/awsemail-lw', 'ap-south-1')
    for event in logs:
        print(event['timestamp'], event['message'])
    pass

def event_driven_audio_to_text():
    audioFilePath = input("Please enter audio (MP3) file name with complete path: ")
    if(audioFilePath.strip().lower().endswith('.mp3')):
        S3BucketName = "apis3lambdatranscribeinput"
        s3ObjectName = os.path.basename(audioFilePath);
        upload_to_s3(audioFilePath, S3BucketName, s3ObjectName)
    else:
        print("The file is not an MP3 file.")
    pass

def connect_python_to_mongodb():
    # Your code to connect Python to MongoDB service on AWS using Lambda
    pass

def upload_object_to_s3():
    fileObject = input("Please enter file name with complete path: ")
    S3BucketName = "s3-amish-lw"
    s3ObjectName = os.path.basename(fileObject);
    upload_to_s3(fileObject, S3BucketName, s3ObjectName)
    pass

def integrate_lambda_with_s3():
    fileObject = input("Please enter file name which contains emails with complete path: ")
    S3BucketName = "awsemail-lw"
    s3ObjectName = os.path.basename(fileObject);
    upload_to_s3(fileObject, S3BucketName, s3ObjectName)
    pass


def upload_to_s3(file_name, bucket, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        s3_client.upload_file(file_name, bucket, object_name)
        print(f"File {file_name} uploaded to {bucket}/{object_name}")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False


def get_log_events_from_log_group(log_group_name, aws_region):

    # Create a new CloudWatch Logs client
    client = boto3.client('logs', region_name=aws_region)

    try:
        # List all log streams in the log group
        paginator = client.get_paginator('describe_log_streams')
        log_streams = []
        for page in paginator.paginate(logGroupName=log_group_name):
            log_streams.extend(page['logStreams'])

        all_events = []

        # Retrieve log events from each log stream
        for log_stream in log_streams:
            log_stream_name = log_stream['logStreamName']
            kwargs = {
                'logGroupName': log_group_name,
                'logStreamName': log_stream_name,
                'startFromHead': True
            }

            response = client.get_log_events(**kwargs)
            events = response['events']

            while 'nextForwardToken' in response:
                next_token = response['nextForwardToken']
                response = client.get_log_events(
                    logGroupName=log_group_name,
                    logStreamName=log_stream_name,
                    startFromHead=True,
                    nextToken=next_token
                )
                events.extend(response['events'])
                if next_token == response['nextForwardToken']:
                    break

            all_events.extend(events)

        return all_events
    except Exception as e:
        print(f"Error: {e}")
        return []


def menu():
    while True:
        print("AWS Cloud Menu")
        print("1. Launch EC2 Instance")
        print("2. Create RHEL GUI Instance")
        print("3. Access Log from Cloud")
        print("4. Event-Driven Audio to Text")
        print("5. Connect Python to MongoDB")
        print("6. Upload Object to S3")
        print("7. Integrate Lambda with S3 and SES")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            launch_ec2_instance()
        elif choice == '2':
            create_rhel_gui_instance()
        elif choice == '3':
            access_log_from_cloud()
        elif choice == '4':
            event_driven_audio_to_text()
        elif choice == '5':
            connect_python_to_mongodb()
        elif choice == '6':
            upload_object_to_s3()
        elif choice == '7':
            integrate_lambda_with_s3()
        elif choice == '8':
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    menu()