#!/bin/bash

# Define the log file with a timestamp
logfile="/tmp/install_terraform-$(date +%Y%m%d%H%M%S).log"

# Check if jq is installed
if ! command -v jq &> /dev/null
then
    echo "jq could not be found" | tee -a $logfile
    echo "Installing jq..." | tee -a $logfile
    sudo apt-get install jq -y | tee -a $logfile
fi

# Get the latest version of Terraform
latest_version=$(curl -s https://checkpoint-api.hashicorp.com/v1/check/terraform | jq -r -M '.current_version')

# Check if Terraform is installed
if command -v terraform &> /dev/null
then
    # Get the current Terraform version
    current_version=$(terraform --version | head -n 1 | cut -d'v' -f2)

    # Check if the current version is the latest version
    if [ "$current_version" == "$latest_version" ]
    then
        echo "The latest version of Terraform is already installed." | tee -a $logfile
        exit 0
    else
        # Rename the previous version
        mv /usr/local/bin/terraform /usr/local/bin/terraform-$current_version
        output="| Replaced Terraform version $current_version with $latest_version |"
        len=${#output}
        echo -e "\e[32m\n$(printf '%0.s=' $(seq 1 $len))" | tee -a $logfile
        echo -e "$output" | tee -a $logfile
        echo -e "$(printf '%0.s=' $(seq 1 $len))\n\e[0m" | tee -a $logfile
    fi
fi

# Download the latest Terraform binary
wget https://releases.hashicorp.com/terraform/${latest_version}/terraform_${latest_version}_linux_amd64.zip -O terraform.zip | tee -a $logfile

# Unzip the downloaded file
unzip terraform.zip | tee -a $logfile

# Move the new Terraform binary to the system location
mv terraform /usr/local/bin/ | tee -a $logfile

# Verify the installation
terraform --version | tee -a $logfile

