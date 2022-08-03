#!/usr/bin/env   python
import boto3
from collections import defaultdict
from datetime import datetime
import pprint
import csv
from regions import *
'''
CPUUtilization of Instances compared with Threshold Value
'''
#import pdb; pdb.set_trace()
client = boto3.client('ec2')
regions = client.describe_regions()['Regions']
cpu_threshold = 0.1
csvfile = open('LOW-CPU.csv', 'w')
writer = csv.writer(csvfile)
writer.writerow(['Report for Instances with Low CPU Utilization i.e, <', cpu_threshold])
writer.writerow(['Region','Instance-IDs'])

for region in regions:
    region_name = region['RegionName']
    ec2 = boto3.resource('ec2', region_name=region['RegionName'])
    running_instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name','Values': ['running']}])

    cw = boto3.client('cloudwatch', region_name=region['RegionName'])

    for instance in running_instances:
        x = instance.id
        print ( x +" is running in "+ region_name)


        cw_cpu = cw.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': x
                },
            ],
            StartTime=datetime(2017, 3, 24),
            EndTime=datetime(2017, 4, 25),
            Period=2592000,
            Statistics=['Average'
                        ])
        print cw_cpu

#        for datapoint in cw_cpu['Datapoints']:
#            if datapoint['Average'] > 0.1:
#                data=[region_name,x]
#                writer.writerow(data)

