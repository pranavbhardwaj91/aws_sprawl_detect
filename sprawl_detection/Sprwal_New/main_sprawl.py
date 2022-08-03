#!/usr/bin/python
#############################################################
#This is the Main Script which will call the other scripts  #
#                                                           #
#                                                           #
#                                                           # 
#                                                           #
#                                                           #    
#                                                           #   
#                                                           #
#############################################################
import csv
import os
import sys
import ebs_report
import Unused_Eip
import boto3
import xlwt
import glob
import smtplib
import subprocess
from email.mime.application import MIMEApplication
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
from datetime import datetime, timedelta
current_directory = os.getcwd()


#Invoking the scripts
#subprocess.call("python " + current_directory +"/ebs_report.py", shell=True)
#subprocess.call("python " + current_directory +"/Unused_Eip.py", shell=True)
#subprocess.call("python " + current_directory +"/Unused_RDS.py", shell=True)
#subprocess.call("python " + current_directory +"/Stopped_Instances.py", shell=True)
#subprocess.call("python " + current_directory +"/Old_Snapshots.py", shell=True)
#subprocess.call("python " + current_directory +"/Idle_Elb.py", shell=True)
#subprocess.call("python " + current_directory +"/Inactive_Keypairs.py", shell=True)"""
#subprocess.call("python " + current_directory +"/CPU_CW.py", shell=True)
subprocess.call("python " + current_directory +"/cpu_unused_test.py", shell=True)

#Generating the Combined Report
wb = xlwt.Workbook()
for filename in glob.glob(current_directory + "/*.csv"):
    (f_path, f_name) = os.path.split(filename)
    (f_short_name, f_extension) = os.path.splitext(f_name)
    ws = wb.add_sheet(f_short_name)
    spamReader = csv.reader(open(filename, 'rb'))
    for rowx, row in enumerate(spamReader):
        for colx, value in enumerate(row):
            ws.write(rowx, colx, value)
wb.save('Combined report.xls')


"""
#Sending Mail for Combined Report
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
"""