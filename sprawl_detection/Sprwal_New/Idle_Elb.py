#!/usr/bin/python
############################################################
#This script will generate an Idle ELBs detailed report#####
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
