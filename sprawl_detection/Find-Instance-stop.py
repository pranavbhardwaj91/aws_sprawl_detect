#!/usr/bin/python3
import boto3
import csv

region_list = ['us-east-1', 'us-west-1', 'ap-northeast-2', 'ap-northeast-1', 'sa-east-1', 'eu-central-1', 'ap-southeast-1', 'ca-central-1', 'ap-southeast-2', 'us-west-2', 'us-east-2', 'ap-south-1', 'eu-west-1', 'eu-west-2']

for region in region_list:

        #Instances
        client = boto3.client('ec2', region_name=region)
        f = open('instance_stop_report.csv','w')
        writer = csv.writer(f)
        data=[region, 'Instance-ID', 'Stopped From Date']
        writer.writerow(data)
                
        instance = client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped'] }])['Reservations']
        for i in instance:
            data=[region, i['Instances'][0]['InstanceId'], i['Instances'][0]['StateTransitionReason'][16:26]]
            writer.writerow(data)            