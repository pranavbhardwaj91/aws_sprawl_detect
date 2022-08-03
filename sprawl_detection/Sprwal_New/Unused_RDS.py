#!/usr/bin/python
##########################################################
#This script will generate an Unused RDSs detailed report#
#                                                        #
#                                                        #
#                                                        # 
#                                                        #
#                                                        #    
#                                                        #   
#                                                        #
##########################################################
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