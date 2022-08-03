#! /usr/bin/python

import csv
import os
import sys
from datetime import datetime, timedelta
import boto3
import xlwt
import glob
import smtplib
from email.mime.application import MIMEApplication
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders

regions = [
    'us-east-1',
    'us-west-1',
    'ap-northeast-2',
    'ap-northeast-1',
    'sa-east-1',
    'eu-central-1',
    'ap-southeast-1',
    'ca-central-1',
    'ap-southeast-2',
    'us-west-2',
    'us-east-2',
    'ap-south-1',
    'eu-west-1',
    'eu-west-2']

report = "Imaginea_AWS_Sprawl.xls"

def ebs_report():

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

    f.close()


def Unused_Eip():

    eip = open('Unused-ElasticIPs.csv', 'w')
    csvwriter = csv.writer(eip)
    data = ['Region', 'Unassociated Ip Address']
    csvwriter.writerow(data)
    no_of_regions = len(regions)

    for region in regions:
        conn = boto3.client('ec2', region_name=region)
        address = conn.describe_addresses()['Addresses']

        if not address:
            data = [region, 'None']

        else:
            for i in range(len(address)):
                if 'NetworkInterfaceId' in address[i]:
                    data = [region, '']

                else:
                    data = [region, address[i]['PublicIp']]
                    csvwriter.writerow(data)


def Unused_RDS():

    cw = open('RDS_Report.csv', 'w')
    csvwriter = csv.writer(cw)
    data = [
        'Region Name',
        'RDS Name',
        'DBInstanceClass',
        'Connections in last 7 Days',
        'Status']
    csvwriter.writerow(data)

    for region in regions:
        conn = boto3.client('rds', region_name=region)
        d = boto3.client('cloudwatch', region_name=region)
        rds = conn.describe_db_instances()['DBInstances']
        if not rds:
            data = [region, 'None', 'None', 'N/A', 'N/A']
            csvwriter.writerow(data)
        else:
            for i in range(len(rds)):
                for j in d.get_metric_statistics(
                    Period=600,
                    StartTime=datetime.now() -
                    timedelta(
                        seconds=604800),
                    EndTime=datetime.now(),
                    MetricName="DatabaseConnections",
                    Namespace='AWS/RDS',
                    Statistics=['Sum'],
                    Dimensions=[
                        {
                            'Name': 'DBInstanceIdentifier',
                            'Value': rds[i]['DBInstanceIdentifier']}])['Datapoints']:
                    z = 0
                    z = z + j.values()[1]
                if z > 0:
                    data = [region, rds[i]['DBInstanceIdentifier'],
                            rds[i]['DBInstanceClass'], z, "Not Idle"]
                    csvwriter.writerow(data)
                else:
                    data = [region, rds[i]['DBInstanceIdentifier'],
                            rds[i]['DBInstanceClass'], "0", "Idle"]
                    csvwriter.writerow(data)


def Inactive_Keypairs():

    cw = open('Inactive-Keys.csv', 'w')
    csvwriter = csv.writer(cw)
    data = ['Region Name', 'Key-Pairs']
    csvwriter.writerow(data)

    for region in regions:
        connect = boto3.client('ec2', region_name=region)
        keys = []

        '''Get all Key pairs available'''

        for i in connect.describe_key_pairs()['KeyPairs']:
            keys.append(i['KeyName'])

        ''' Get all Key Pairs associated with the instances'''

        reservations = connect.describe_instances()['Reservations']
        for res in range(len(reservations)):
            if 'KeyName' in reservations[res]['Instances'][0] and reservations[res]['Instances'][0]['KeyName'] in keys:
                keys.remove(reservations[res]['Instances'][0]['KeyName'])

        if not keys:
            data = [region, None]
            csvwriter.writerow(data)
        else:
            data = [region, ', '.join(keys)]
            csvwriter.writerow(data)


def Stopped_Instances():

    cw = open('Stopped_Instances.csv', 'w')
    csvwriter = csv.writer(cw)
    data = [
        'Region Name',
        'Instance-id',
        'Stopped-Time',
        'Volume-Id',
        'Deleteontermination',
        'Size',
        'Iops']
    csvwriter.writerow(data)

    ec2 = []
    time = datetime.strptime(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '%Y-%m-%d %H:%M:%S')

    for region in regions:
        connect = boto3.client('ec2', region_name=region)

        for i in connect.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])['Reservations']:
            ec2_details = {}
            ec2_details['Instance-id'] = i['Instances'][0]['InstanceId']
            try:
                ec2_details['Stop-Time'] = time - datetime.strptime(
                    i['Instances'][0]['StateTransitionReason'][16:35], '%Y-%m-%d %H:%M:%S')
            except BaseException:
                ec2_details['Stop-Time'] = 'None'
                continue

            ec2.append(ec2_details)
            for vol in range(len(i['Instances'][0]['BlockDeviceMappings'])):
                ec2_details['Volume-Id'] = i['Instances'][0]['BlockDeviceMappings'][vol]['Ebs']['VolumeId']
                ec2_details['Deleteontermination'] = i['Instances'][0]['BlockDeviceMappings'][vol]['Ebs']['DeleteOnTermination']

                volume = connect.describe_volumes(
                    VolumeIds=[ec2_details['Volume-Id']])['Volumes']

                try:
                    ec2_details['Size'] = volume[0]['Size']
                except BaseException:
                    print "Timed out Couldn't retrieve Volume Size details"
                    continue

                try:
                    if volume[0]['VolumeType'] == 'gp2':
                        ec2_details['IOPS'] = volume[0]['Iops']

                    elif volume[0]['VolumeType'] == 'io1':
                        ec2_details['IOPS'] = volume[0]['Iops']

                    else:
                        ec2_details['IOPS'] = 0
                except BaseException:
                    print "Timed out Couldn't retrieve Volume Iops details"
                    continue

            data = [
                region,
                ec2_details['Instance-id'],
                ec2_details['Stop-Time'],
                ec2_details['Volume-Id'],
                ec2_details['Deleteontermination'],
                ec2_details['Size'],
                ec2_details['IOPS']]
            csvwriter.writerow(data)


def Old_Snapshots():

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


def Idle_Elb():

    cw = open('idle_elb.csv', 'w')
    csvwriter = csv.writer(cw)
    data = ['Region Name', 'ELB Name', 'Instance ID', 'Status', 'Reason']
    csvwriter.writerow(data)

    for region in regions:
        conn = boto3.client('elb', region_name=region)
        elb = conn.describe_load_balancers()['LoadBalancerDescriptions']
        if not elb:
            print "No ELBs in {}".format(region)
        else:
            for i in elb:
                if not elb[0]['Instances']:
                    data = [
                        region,
                        elb[0]['LoadBalancerName'],
                        '',
                        "IDLE",
                        "No active Instances"]
                    csvwriter.writerow(data)
                else:
                    print region, elb[0]['Instances']
                    for j in range(len(elb[0]['Instances'])):
                        s = conn.describe_instance_health(LoadBalancerName=elb[0]['LoadBalancerName'], Instances=[
                                                          {'InstanceId': elb[0]['Instances'][j]['InstanceId']}])
                        if s['InstanceStates'][0]['State'] == 'InService':
                            d = boto3.client('cloudwatch', region_name=region)

                            for k in d.get_metric_statistics(
                                Period=600,
                                StartTime=datetime.now() -
                                timedelta(
                                    seconds=604800),
                                EndTime=datetime.now(),
                                MetricName="RequestCount",
                                Namespace='AWS/ELB',
                                Statistics=['Sum'],
                                Dimensions=[
                                    {
                                        'Name': 'LoadBalancerName',
                                        'Value': elb[0]['LoadBalancerName']}])['Datapoints']:

                                z = 0
                                z = z + k['Sum']
                            if z > 100:
                                print "The", elb[0]['LoadBalancerName'], "is not idle for instance", elb[0]['Instances'][j]['InstanceId']
                            else:
                                print "The", elb[0]['LoadBalancerName'], "is idle for instance", elb[0]['Instances'][j]['InstanceId']
                                data = [
                                    region,
                                    elb[0]['LoadBalancerName'],
                                    elb[0]['Instances'][j]['InstanceId'],
                                    "IDLE",
                                    "Number of Requests are less than 100 for past 7 days"]
                                csvwriter.writerow(data)

                        else:
                            print "The instance are Out of Service", elb[0]['Instances'][j]['InstanceId']
                            data = [
                                region,
                                elb[0]['LoadBalancerName'],
                                elb[0]['Instances'][j]['InstanceId'],
                                "IDLE",
                                "Instance are Out of Service"]
                            csvwriter.writerow(data)


if __name__ == '__main__':
    ebs_report()
    Unused_Eip()
    Unused_RDS()
    Inactive_Keypairs()
    Stopped_Instances()
    Old_Snapshots()
    Idle_Elb()

wb = xlwt.Workbook()
for filename in glob.glob("*.csv"):
    (f_path, f_name) = os.path.split(filename)
    (f_short_name, f_extension) = os.path.splitext(f_name)
    ws = wb.add_sheet(f_short_name)
    spamReader = csv.reader(open(filename, 'rb'))
    for rowx, row in enumerate(spamReader):
        for colx, value in enumerate(row):
            ws.write(rowx, colx, value)

wb.save("report")


#Sending mail to the generated report.
def send_report():
    server = smtplib.SMTP("localhost", 25)
    SUBJECT = "AWS Report"
    EMAIL_FROM = "localhost"
    EMAIL_TO  = ['sr.sysdoc@gmail.com']
    msg = MIMEMultipart()
    msg['Subject'] = SUBJECT 
    msg['From'] = EMAIL_FROM
    msg['To'] = ', '.join(EMAIL_TO)
   
    part = MIMEApplication(
                open(report).read(),
                Name=report
            )
    part['Content-Disposition'] = 'attachment; filename="%s"' % report
    msg.attach(part)
    server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

send_report()
