#!/bin/bash

# Cloud Build Script for Azure Container Apps
# This script builds your Docker image in the cloud using a temporary VM

echo "🚀 Starting cloud build process..."

# Create a temporary build script
cat > cloud-build.sh << 'EOF'
#!/bin/bash
set -e

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Clone the repository
git clone https://github.com/NarenSundar007/LLM-Parser.git
cd LLM-Parser

# Build the Docker image
sudo docker build -t llm-query-system:latest .

# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure (you'll need to do this interactively)
echo "Please run 'az login' and then 'az acr login --name bajazhackathonacr'"

# Tag and push to Azure Container Registry
sudo docker tag llm-query-system:latest bajazhackathonacr.azurecr.io/llm-query-system:latest
sudo docker push bajazhackathonacr.azurecr.io/llm-query-system:latest

echo "✅ Build complete! Image pushed to Azure Container Registry"
EOF

# Create a temporary Azure VM for building
echo "Creating temporary build VM..."
az vm create \
  --resource-group bajaj-hackathon-rg \
  --name temp-build-vm \
  --image Ubuntu2204 \
  --admin-username azureuser \
  --generate-ssh-keys \
  --size Standard_B2s \
  --location eastus

# Get the public IP
VM_IP=$(az vm show -d -g bajaj-hackathon-rg -n temp-build-vm --query publicIps -o tsv)

echo "VM created with IP: $VM_IP"
echo "Copy the build script to the VM and run it:"
echo "scp cloud-build.sh azureuser@$VM_IP:~/"
echo "ssh azureuser@$VM_IP"
echo "chmod +x cloud-build.sh && ./cloud-build.sh"

echo "After building, delete the VM with:"
echo "az vm delete --resource-group bajaj-hackathon-rg --name temp-build-vm --yes"
