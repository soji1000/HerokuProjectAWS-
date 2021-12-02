from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core

from aws_cdk import aws_s3 as s3
from aws_cdk import aws_apprunner as apprunner
from aws_cdk import aws_rds as rds
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticbeanstalk as eb
import aws_cdk.aws_cloudfront as cloudfront
import aws_cdk.aws_elasticache as elasticache
import aws_cdk.aws_cloudfront_origins as origins

import json


class HelloCdkStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # get app data from json
        f = open('app.json',)
        data = json.load(f)
        f.close()
        
        for addon in data['addons']:
            if addon['plan']['addon_service']['name'] == "Bucketeer" :
               # S3 (Bucketeer)
               # The code that defines your stack goes here
                bucket = s3.Bucket(self, "s3-bucket",
                bucket_name= ('HelloCdkBucket'),
                website_index_document= 'index.html',
                website_error_document= 'error.html',
                public_read_access= True,
                removal_policy= core.RemovalPolicy.DESTROY)
                
            elif addon['plan']['addon_service']['name'] == "Redis To Go" :
                #put code here. 
                # Elasticachecluster (Redis)
                cfn_cache_cluster = elasticache.CfnCacheCluster(self, "MyCfnCacheCluster",
                    cache_node_type="cacheNodeType",
                    engine="engine",
                    num_cache_nodes=123,
                    auto_minor_version_upgrade=False,
                    az_mode="azMode",
                    cache_parameter_group_name="cacheParameterGroupName",
                    cache_security_group_names=["cacheSecurityGroupNames"],
                    cache_subnet_group_name="cacheSubnetGroupName",
                    cluster_name="clusterName",
                    engine_version="engineVersion",
                    log_delivery_configurations=[elasticache.CfnCacheCluster.LogDeliveryConfigurationRequestProperty(
                        destination_details=elasticache.CfnCacheCluster.DestinationDetailsProperty(
                            cloud_watch_logs_details=elasticache.CfnCacheCluster.CloudWatchLogsDestinationDetailsProperty(
                                log_group="logGroup"
                                ),
                                    kinesis_firehose_details=elasticache.CfnCacheCluster.KinesisFirehoseDestinationDetailsProperty(
                                        delivery_stream="deliveryStream"
                                    )
                                ),
                                destination_type="destinationType",
                                log_format="logFormat",
                                log_type="logType"
                            )],
                            notification_topic_arn="notificationTopicArn",
                            port=123,
                            preferred_availability_zone="preferredAvailabilityZone",
                            preferred_availability_zones=["preferredAvailabilityZones"],
                            preferred_maintenance_window="preferredMaintenanceWindow",
                            snapshot_arns=["snapshotArns"],
                            snapshot_name="snapshotName",
                            snapshot_retention_limit=123,
                            snapshot_window="snapshotWindow"
                        )
                    
                 
            elif addon['plan']['addon_service']['name'] == "Edge" :
                #put code here.
                # Cloudfront Distribution (Edge) 
                cloudfront.Distribution(self, "myDist",
                    default_behavior=cloudfront.BehaviorOptions(origin=origins.S3Origin(bucket)))
            else:
                pass 
                  
         
        apprunner_service_name = cdk.CfnParameter(self, "ServiceName", type = "String", description = "name of apprunner service", default = data['appName'])

        # VPC
        vpc = ec2.Vpc.from_lookup(self, data["vpcName"], is_default=True)

        # # security group to allow public access
        dbSecurityGroup = ec2.SecurityGroup(self, "PublicAccessDB", vpc=vpc)
        dbSecurityGroup.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(5432))

        # Database
        instance = rds.DatabaseInstance(self, 'Instance', \
            engine = rds.DatabaseInstanceEngine.POSTGRES, \
            vpc = vpc, \
            vpc_subnets = ec2.SubnetSelection(subnet_type = ec2.SubnetType.PUBLIC), \
            multi_az = True, \
            security_groups = [dbSecurityGroup]
        )
        
        # Apprunner
        if data['hasGithub'] == 'y':
            app = apprunner.CfnService(self, "Service", \
                service_name = apprunner_service_name.value_as_string, \
                source_configuration = apprunner.CfnService.SourceConfigurationProperty( \
                    code_repository = apprunner.CfnService.CodeRepositoryProperty( \
                        repository_url = data['link'], \
                        source_code_version = apprunner.CfnService.SourceCodeVersionProperty( \
                            type = "BRANCH", \
                            value = "master" \
                        ) \
                    ), \
                    authentication_configuration = apprunner.CfnService.AuthenticationConfigurationProperty( \
                        connection_arn = data['connectionArn'] \
                    ) \
                ) \
            )
        else: 
            app = apprunner.CfnService(self, "Service", \
                service_name = apprunner_service_name.value_as_string, \
                source_configuration = apprunner.CfnService.SourceConfigurationProperty( \
                    image_repository = apprunner.CfnService.ImageRepositoryProperty( \
                        image_identifier = data["link"], \
                        image_configuration = apprunner.CfnService.ImageConfigurationProperty(port = '8000'), \
                        image_repository_type = data['private_or_public'] \
                    ) \
                ) \
            )

        outputs = cdk.CfnOutput(self, "Endpoint", \
            description = "The endpoint of the App Runner service.", \
            value = app.get_att('ServiceUrl').to_string() \
        )
            

   
       
    
 

        