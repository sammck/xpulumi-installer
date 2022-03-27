#!/usr/bin/env python3

import pulumi
from pulumi import Output
import pulumi_aws as aws
import xpulumi
import xpulumi.runtime
from xpulumi.runtime import (
    VpcEnv,
    DnsZone,
    FrontEndSecurityGroup,
  )

vpc = VpcEnv.load()
vpc.stack_export()

parent_dns_zone = DnsZone(resource_prefix='parent-', subzone_name='mckelvie.org', create=False)
parent_dns_zone.stack_export(export_prefix='parent_')

dns_zone = DnsZone(resource_prefix='main-', subzone_name='xhub', parent_zone=parent_dns_zone)
dns_zone.stack_export(export_prefix='main_')

frontend_sg = FrontEndSecurityGroup(
    vpc,
    open_ports=[ 22, 80, 443 ]
  )
frontend_sg.stack_export()