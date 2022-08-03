import boto.ec2
import csv,sys

regions = []


for i in boto.ec2.regions():
    if i.name != ('us-gov-west-1') and i.name != ('cn-north-1'):
        regions.append(i.name)


def get_volumes():

    csvfile = open('report.csv', 'w')
    writer = csv.writer(csvfile)
    writer.writerow(['Region','Volume-id','Volume-size(in GiB)','Volume-Create-time'])

    for i in regions:
        c = boto.ec2.connect_to_region(i)
        volumes = c.get_all_volumes(filters={'status': 'available'})
        for j in volumes:
            writer.writerow([i,j.id,j.size,j.create_time])
        #print "Deleting Unsued Volumes"
        #c.delete_volume(j.id)

get_volumes()

