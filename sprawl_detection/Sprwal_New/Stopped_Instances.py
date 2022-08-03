#!/usr/bin/python
################################################################
#This script will generate an Stopped instances detailed report#
#                                                              #
#                                                              #
#                                                              # 
#                                                              #
#                                                              #    
#                                                              #   
#                                                              #
################################################################
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
from regions import regions

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