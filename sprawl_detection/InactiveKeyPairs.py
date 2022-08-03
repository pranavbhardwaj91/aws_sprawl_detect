# Make sure all the modules are installed in running server. use pip to install it.
import boto.ec2
from termcolor import colored

region_list = ['us-east-1', 'us-west-1', 'ap-northeast-2', 'ap-northeast-1', 'sa-east-1', 'eu-central-1', 'ap-southeast-1', 'ca-central-1', 'ap-southeast-2', 'us-west-2', 'us-east-2', 'ap-south-1', 'eu-west-1', 'eu-west-2']

def Inactive_Keypairs():

    for region in region_list:
        connect = boto.ec2.connect_to_region(region)
        keys = []

        '''Get all Key pairs available'''
        for i in connect.get_all_key_pairs():
            keys.append(i.name)

        ''' Get all Key Pairs associated with the instances'''

        for j in connect.get_all_reservations():
            if j.instances[0].key_name in keys:
                keys.remove(j.instances[0].key_name)


           
        print "\nFollowing keys are not associated with any instances in the region %s \n" %(region)  + colored(','.join(keys), 'yellow')
        #for k in keys:
         #   connect.delete_key_pair(k)


Inactive_Keypairs()