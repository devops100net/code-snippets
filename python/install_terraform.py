# Python
# AI-generated code. Review and use carefully

import os
import json
import requests
import subprocess
from datetime import datetime

# Define the log file with a timestamp
logfile = "/tmp/install_terraform_{}.log".format(datetime.now().strftime("%Y%m%d%H%M%S"))

# Check if jq is installed
if not os.system('command -v jq'):
    print("jq could not be found", file=open(logfile, 'a'))
    print("Installing jq...", file=open(logfile, 'a'))
    os.system('sudo apt-get install jq -y | tee -a {}'.format(logfile))

# Get the latest version of Terraform
response = requests.get('https://checkpoint-api.hashicorp.com/v1/check/terraform')
latest_version = json.loads(response.text)['current_version']

# Check if Terraform is installed
if not os.system('command -v terraform'):
    # Get the current Terraform version
    current_version = subprocess.check_output(['terraform', '--version']).decode('utf-8').split('\n')[0].split('v')[1]

    # Check if the current version is the latest version
    if current_version == latest_version:
        print("The latest version of Terraform is already installed.", file=open(logfile, 'a'))
        exit(0)
    else:
        # Rename the previous version
        os.system('mv /usr/local/bin/terraform /usr/local/bin/terraform-{}'.format(current_version))
        output = "| Replaced Terraform version {} with {} |".format(current_version, latest_version)
        len_output = len(output)
        print("\033[32m\n{}\n{}\n{}\n\033[0m".format('='*len_output, output, '='*len_output), file=open(logfile, 'a'))

# Download the latest Terraform binary
os.system('wget https://releases.hashicorp.com/terraform/{}/terraform_{}_linux_amd64.zip -O terraform.zip | tee -a {}'.format(latest_version, latest_version, logfile))

# Unzip the downloaded file
os.system('unzip terraform.zip | tee -a {}'.format(logfile))

# Move the new Terraform binary to the system location
os.system('mv terraform /usr/local/bin/ | tee -a {}'.format(logfile))

# Verify the installation
os.system('terraform --version | tee -a {}'.format(logfile))

