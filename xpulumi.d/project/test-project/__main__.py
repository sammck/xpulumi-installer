#!/usr/bin/env python3

import pulumi
from pulumi import Output
import pulumi_aws as aws

config = pulumi.Config()

instance_type: str = config.require('instance_type')

secret_input = config.require_secret('secret_input')

ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["137112412989"],
    filters=[
        aws.GetAmiFilterArgs(name="name", values=["amzn-ami-hvm-*"])
      ],
  )

sg = aws.ec2.SecurityGroup(
    'frontend-sg',
    description='HTTP only',
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=80,
            to_port=80,
            cidr_blocks=['0.0.0.0/0'],
          ),
      ],
  )

user_data: str = """
#!/bin/bash
echo "It works!!" > index.html
nohup python -m SimpleHTTPServer 80 &
"""

server = aws.ec2.Instance(
    'frontend-ec2-instance',
    instance_type=instance_type,
    vpc_security_group_ids=[sg.id],
    user_data=user_data,
    ami=ami.id,
  )

pulumi.export('public_ip', server.public_ip)
pulumi.export('url', Output.concat("http://", server.public_ip))
pulumi.export("secret_output", Output.secret("John is the Walrus"))
pulumi.export("secret_input", secret_input)
pulumi.export("exposed_input", Output.unsecret(secret_input))
