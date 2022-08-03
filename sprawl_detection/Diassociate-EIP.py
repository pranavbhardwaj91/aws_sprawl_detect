#!/usr/bin/python2.7
import boto3

region_list = ['us-east-1', 'us-west-1', 'ap-northeast-2', 'ap-northeast-1', 'sa-east-1', 'eu-central-1', 'ap-southeast-1', 'ca-central-1', 'ap-southeast-2', 'us-west-2', 'us-east-2', 'ap-south-1', 'eu-west-1', 'eu-west-2']
#owner_id = '895183702840'
owner_id = '575110498197'

for region in region_list:


        #EIP  This script will not realese the IPAddress which are associated to NAT GateWays.
    client = boto3.client('ec2', region_name=region)
    response = client.describe_addresses()
    eips=[]
    for address in response['Addresses']:
        if 'InstanceId' not in address:
            eips.append(address['PublicIp'])
            print region, eips
            for i in range(len(eips)):
            	print region, eips
            	'''try:
            		client.release_address(AllocationId=address['AllocationId'])
            		print "Released {} in {}".format(eips[i],region)
            	except:
            		print "Could not release address {} in {}. Is this address attached \
            		to a NAT Gateway???".format(eips[i],region)
            		continue'''
    
        