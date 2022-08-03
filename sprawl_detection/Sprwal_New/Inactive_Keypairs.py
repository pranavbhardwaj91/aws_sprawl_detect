#!/usr/bin/python
################################################################
#This script will generate an Inactive Keypairs detailed report#
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