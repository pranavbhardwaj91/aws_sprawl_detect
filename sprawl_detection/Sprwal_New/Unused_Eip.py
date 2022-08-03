#!/usr/bin/python
##########################################################
#This script will generate an Unused EIPs detailed report#
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
import boto3
import glob
import smtplib
from email.mime.application import MIMEApplication
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
from datetime import datetime, timedelta
from regions import regions

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
Unused_Eip()