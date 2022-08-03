#!/usr/bin/env   python
import boto3
from collections import defaultdict
from datetime import datetime
import pprint
'''
CPUUtilization of Instances compared with Threshold Value
'''
client = boto3.client('ec2')
regions = client.describe_regions()['Regions']
for region in regions:
    region_name = region['RegionName']

for region in regions:
    region_name = region['RegionName']
    ec2 = boto3.resource('ec2', region_name=region['RegionName'])
    running_instances = ec2.instances.filter(Filters=[{
        'Name': 'instance-state-name',
        'Values': ['running']}])
    ec2info = defaultdict()

    cw = boto3.client('cloudwatch', region_name=region['RegionName'])

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
        print ( x +" " + region_name)
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
            EndTime=datetime(2017, 3, 25),
            Period=3600,
            Statistics=['Average'
                        ])
        #pprint.pprint(cw_cpu)
        count = 0
        for datapoint in cw_cpu['Datapoints']:
            if datapoint['Average'] > 0.1:
                print ('CPU is used more for ' + x)
                count = count + 1
            else:
                print ('CPU is used less for ' + x)
                print (count)
