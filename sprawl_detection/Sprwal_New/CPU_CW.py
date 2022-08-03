#!/usr/bin/env   python
import csv
import boto3
from collections import defaultdict
from datetime import datetime
import pprint
from regions import *

#This includes variables from regions.py file
"""
CPUUtilization of Instances compared with Threshold Value

client = boto3.client('ec2')
regions = client.describe_regions()['Regions']
for region in regions:
    region_name = region['RegionName']
    print region_name
"""
cw = open('Unused CPU.csv', 'w')
csvwriter = csv.writer(cw)
data = ['Instance ID', 'Regions', 'Description']
csvwriter.writerow(data)

def unused():
    for region in regions: 
        ec2 = boto3.resource('ec2', region_name=region)
        running_instances = ec2.instances.filter(Filters=[{
            'Name': 'instance-state-name',
            'Values': ['running']}])
        ec2info = defaultdict()
    cw = boto3.client('cloudwatch', region_name=region)

        for instance in running_instances:
            for tag in instance.tags:
                if 'Name'in tag['Key']:
                    name = tag['Value']

            ec2info[instance.id] = {
                'Name': name,
                'ID': instance.id,
            }

        for instance_id, instance in ec2info.items():
            x = instance_id 
            print (x +" " +region)

            cw_cpu = cw.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': x
                    },
                ],
                StartTime=datetime(start_year, start_month, start_date),
                EndTime=datetime(end_year, end_month, end_date),
                Period=metric_span,
                Statistics=['Average'
                            ])
 #       pprint.pprint(cw_cpu)
        
            for datapoint in cw_cpu['Datapoints']:
                if datapoint['Average'] > cpu_threshold:
                    print ('CPU is used more for ' + x + "\n")
                else:
                    print ('CPU is used less for ' + x +"\n")

unused()

       
