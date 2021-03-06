from troposphere import Template, Ref, Join, Select, Split, Tags, GetAtt, Output
from troposphere.ec2 import VPC, VPCCidrBlock, Subnet, SubnetCidrBlock, InternetGateway, RouteTable, Route, \
    VPCGatewayAttachment, SubnetRouteTableAssociation


def generate_template():
    template = Template()

    ref_stack_id = Ref('AWS::StackId')
    ref_region = Ref('AWS::Region')
    ref_stack_name = Ref('AWS::StackName')

    template.add_description(
        'Base infrastructure Stack implementing VPC Scenario 2 with 2 private subnets'
    )

    # Create VPC

    vpc = template.add_resource(
        VPC(
            'VPC',
            CidrBlock='10.0.0.0/16',
            EnableDnsHostnames=True,
            Tags=Tags(
                Application=ref_stack_id)))

    # Create Cidr Block for IPv6
    vpc_cidr_block = template.add_resource(
        VPCCidrBlock(
            'VPCCidrBlock',
            AmazonProvidedIpv6CidrBlock=True,
            VpcId=Ref(vpc),
        ))

    internet_gateway = template.add_resource(
        InternetGateway(
            'InternetGateway',
            Tags=Tags(
                Application=ref_stack_id)))

    template.add_resource(
        VPCGatewayAttachment(
            'AttachGateway',
            VpcId=Ref(vpc),
            InternetGatewayId=Ref(internet_gateway)))

    # Create Routing Tables
    public_route_table = template.add_resource(
        RouteTable(
            'PublicRouteTable',
            VpcId=Ref(vpc),
            Tags=Tags(
                Application=ref_stack_id)))

    template.add_resource(
        Route(
            'RouteIPv4',
            DependsOn='AttachGateway',
            GatewayId=Ref('InternetGateway'),
            DestinationCidrBlock='0.0.0.0/0',
            RouteTableId=Ref(public_route_table),
        ))

    template.add_resource(
        Route(
            'RouteIPv6',
            DependsOn='AttachGateway',
            GatewayId=Ref('InternetGateway'),
            DestinationIpv6CidrBlock="::/0",
            RouteTableId=Ref(public_route_table),
        ))

    # Create Public Subnet
    public_subnet1 = template.add_resource(
        Subnet(
            'PublicSubnet1',
            DependsOn=vpc_cidr_block,
            AssignIpv6AddressOnCreation=True,
            CidrBlock='10.0.0.0/24',
            Ipv6CidrBlock=Join("", [Select(0, Split("00::/56", Select(0, GetAtt(vpc, 'Ipv6CidrBlocks')))), "00::/64"]),
            AvailabilityZone=Join("", [ref_region, 'a']),
            VpcId=Ref(vpc),
            Tags=Tags(
                Name='public-10.0.0.0',
                Application=ref_stack_id)
        ))

    template.add_resource(
        SubnetRouteTableAssociation(
            'SubnetRouteTableAssociation1',
            SubnetId=Ref(public_subnet1),
            RouteTableId=Ref(public_route_table),
        ))

    # Outputs

    template.add_output(Output(
        'VPCId',
        Value=Ref(vpc),
        Description='VPC Id'
    ))

    template.add_output(Output(
        'PublicSubnet1',
        Value=Ref(public_subnet1),
        Description='Public subnet ID'
    ))

    template.add_output(Output(
        'StackID',
        Value=ref_stack_name,
        Description='Stack ID'
    ))

    return template


if __name__ == '__main__':
    print (generate_template().to_json())
