######################################################################
#This act as the config file where we can define the threshold values#
#and common values.Enable the region for which the Sprawl Detection should#
#work.                                                  				   	#
#               		                                             #
#                        		                                     # 
#                                 		                             #
#                                          			                 #    
#                                                   		         #   
#                                                          			 #
######################################################################
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

#For CPU Utilisation enter the below dates accordingly
start_year = 2017
start_month = 3
start_date = 24

end_year = 2017
end_month = 3
end_date = 25

metric_span = 86400    #In secs
cpu_threshold = 0.1   # what is 0.1 ?