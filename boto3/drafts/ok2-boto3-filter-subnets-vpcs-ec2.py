import boto3
from termcolor import colored

def list_subnets_in_default_vpc(region_filter=None):
    # Create a Boto3 EC2 client
    ec2 = boto3.client('ec2')

    # Get a list of all available AWS regions
    regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]

    if not region_filter:
        valid_region_filters = regions + ["all"]
        print(f"Valid region filters: {', '.join(valid_region_filters)}")
        region_filter = input("Enter the region filter (press Enter for all regions): ").strip().lower()

    if not region_filter or region_filter == "all":
        region_filter = "all"

    if region_filter not in [r.lower() for r in regions] + ["all"]:
        print("Invalid region filter.")
        return

    choice = input("Display: A (all) or S (subnets do exist) or N (subnets do NOT exist): ").strip().lower()

    for region in regions:
        if region_filter != region.lower() and region_filter != "all":
            continue

        print(f"Region: {region}")

        # Describe VPCs to get the default VPC ID
        ec2 = boto3.client('ec2', region_name=region)
        vpcs = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])

        # Describe subnets in the default VPC
        subnets = ec2.describe_subnets()

        if choice == "a":
            if subnets['Subnets']:
                print(colored("Subnets Exist:", 'green', attrs=['bold']))
                for subnet in subnets['Subnets']:
                    print(f"Subnet ID: {subnet['SubnetId']}, CIDR: {subnet['CidrBlock']}, Availability Zone: {subnet['AvailabilityZone']}")
        elif choice == "s" and subnets['Subnets']:
            print(colored("Subnets Exist:", 'green', attrs=['bold']))
            for subnet in subnets['Subnets']:
                print(f"Subnet ID: {subnet['SubnetId']}, CIDR: {subnet['CidrBlock']}, Availability Zone: {subnet['AvailabilityZone']}")
        elif choice == "n" and (not vpcs['Vpcs'] or not subnets['Subnets']):
            print(colored("NO SUBNETS or NO DEFAULT VPC", 'red', attrs=['bold']))

if __name__ == '__main__':
    list_subnets_in_default_vpc()

