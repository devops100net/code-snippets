import boto3
from botocore.config import Config

def list_instances_in_all_regions(check_state=None):
    def available_regions(service):
        regions = []
        client = boto3.client(service)
        response = client.describe_regions()

        for item in response["Regions"]:
            regions.append(item["RegionName"])

        return regions

    regions = available_regions("ec2")

    for region in regions:
        my_config = Config(region_name=region)
        ec2_client = boto3.client("ec2", config=my_config)
        instances = ec2_client.describe_instances()

        for reservation in instances["Reservations"]:
            for instance in reservation["Instances"]:
                state = instance["State"]["Name"]
                instance_id = instance["InstanceId"]
                instance_type = instance["InstanceType"]
                availability_zone = instance["Placement"]["AvailabilityZone"]

                if check_state is None or state.lower() == check_state.lower() or check_state == "all":
                    print(f"Region: {region}, Instance ID: {instance_id}, Type: {instance_type}, AZ: {availability_zone}, State: {state}")

if __name__ == "__main__":
    valid_filters = ["running", "stopped", "terminated", "pending", "all"]
    print(f"Valid instance state filters: {', '.join(valid_filters)}")

    state_filter = input("Enter the state filter (or press Enter to check all states): ")

    if state_filter.strip().lower() not in valid_filters and state_filter.strip() != "":
        print("Invalid filter. Please choose from the following: running, stopped, terminated, pending, all.")
    else:
        list_instances_in_all_regions(state_filter.strip() if state_filter.strip() != "" else "all")

