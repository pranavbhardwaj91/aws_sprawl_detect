#!/usr/bin/python
##############################################################
#This script will generate an EBS Utilisation detailed report#
#                                                            #
#                                                            #
#                                                            # 
#                                                            #
#                                                            #    
#                                                            #   
#                                                            #
##############################################################
import csv
import os
import sys
import boto3
import glob
import smtplib
import xlwt
from email.mime.application import MIMEApplication
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
from datetime import datetime, timedelta
from regions import regions

report = "Imaginea_AWS_Sprawl.xls"
f = open('EBS-Report.csv', 'w')
volume_dict = {}
for region in regions:
    conn = boto3.client('ec2', region_name=region)
    if not conn:
        sys.stderr.write(
            'Could not connect to region: %s. Skipping\n' %
            region)
        continue

    volumes = conn.describe_volumes()['Volumes']
    snapshots = conn.describe_snapshots(OwnerIds=['self'])['Snapshots']
    volume_dict[region] = {}
    for vol in volumes:
        try:
            iops = vol['Iops']
        except BaseException:
            iops = 0

        if not vol['Attachments']:
            instance_id = 'None'
            device = 'None'

        else:
            instance_id = vol['Attachments'][0]['InstanceId']
            device = vol['Attachments'][0]['Device']

        volume_dict[region][vol['VolumeId']] = {'size': vol['Size'],
                                                'id': vol['VolumeId'],
                                                'zone': vol['AvailabilityZone'],
                                                'type': vol['VolumeType'],
                                                'iops': iops,
                                                'orig_snap': vol['SnapshotId'],
                                                'instance': instance_id,
                                                'device': device,
                                                'num_snapshots': 0,
                                                'first_snap_time': u'',
                                                'first_snap_id': u'N/A',
                                                'last_snap_time': u'',
                                                'last_snap_id': u'N/A'}

    for snap in snapshots:
        start_time = datetime.strptime(
            snap['StartTime'].strftime('%Y-%m-%dT%H:%M:%S'),
            '%Y-%m-%dT%H:%M:%S')
        if snap['VolumeId'] in volume_dict[region]:
            vol = volume_dict[region][snap['VolumeId']]
            vol['num_snapshots'] += 1
            if vol['first_snap_time'] == u'' or start_time < vol['first_snap_time']:
                vol['first_snap_time'] = start_time
                vol['first_snap_id'] = snap['SnapshotId']
            if vol['last_snap_time'] == u'' or start_time > vol['last_snap_time']:
                vol['last_snap_time'] = start_time
                vol['last_snap_id'] = snap['SnapshotId']

    writer = csv.writer(f)
    writer.writerow(['Region',
                     'volume ID',
                     'Volume Type',
                     'iops',
                     'Size (GiB)',
                     'Created from Snapshot',
                     'Attached to',
                     'Device',
                     'Number of Snapshots',
                     'Earliest Snapshot Time',
                     'Earliest Snapshot',
                     'Most Recent Snapshot Time',
                     'Most Recent Snapshot'])

    for region in volume_dict.keys():
        for volume_id in volume_dict[region].keys():
            volume = volume_dict[region][volume_id]
            writer.writerow([region,
                             volume_id,
                             volume['type'],
                             volume['iops'],
                             volume['size'],
                             volume['orig_snap'],
                             volume['instance'],
                             volume['device'],
                             volume['num_snapshots'],
                             volume['first_snap_time'],
                             volume['first_snap_id'],
                             volume['last_snap_time'],
                             volume['last_snap_id']])

    