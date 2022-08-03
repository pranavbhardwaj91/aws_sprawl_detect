#!/usr/bin/python
############################################################
#This script will generate an Old Snapshots detailed report#
#                                                          #
#                                                          #
#                                                          # 
#                                                          #
#                                                          #    
#                                                          #   
#                                                          #
############################################################
import csv
from datetime import datetime, timedelta
import boto3
from regions import regions

cw = open('Old_Snapshots.csv', 'w')
csvwriter = csv.writer(cw)
data = ['Region Name', 'Snapshot-id', 'Volume-Size']
csvwriter.writerow(data)
retention_period = datetime.now() - timedelta(days=90)

for region in regions:
    connect = boto3.client('ec2', region_name=region)
    snapshots = connect.describe_snapshots(OwnerIds=['self'])
    count = 0
    for i in snapshots['Snapshots']:
        start_time = datetime.strptime(
        i['StartTime'].strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        '%Y-%m-%dT%H:%M:%S.000Z')
        if (i['State'] == 'completed' and start_time < retention_period):
            count += 1
    print "{} Snapshots are older than 90days in {}".format(count, region)
    data = [region, i['SnapshotId'], i['VolumeSize']]
    csvwriter.writerow(data)
