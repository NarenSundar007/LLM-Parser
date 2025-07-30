#!/bin/bash
# Azure deployment script for LLM Query System

set -e

# Configuration
RESOURCE_GROUP="bajaj-hackathon-rg"
LOCATION="eastus"
ACR_NAME="bajazhackathonacr"
APP_NAME="llm-query-system"
CONTAINER_APP_ENV="bajaj-llm-env"

echo "🔵 Starting Azure deployment for LLM Query System..."

# Check if Gemini API key is provided
if [ -z "$GEMINI_API_KEY" ]; then
    echo "Please set GEMINI_API_KEY environment variable or enter it below:"
    read -p "Enter your Gemini API Key: " GEMINI_API_KEY
fi

# 1. Login to Azure (if not already logged in)
echo "📝 Checking Azure login..."
if ! az account show >/dev/null 2>&1; then
    echo "Please login to Azure:"
    az login
fi

# 2. Create Resource Group
echo "📦 Creating resource group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

# 3. Create Azure Container Registry (ACR)
echo "🐳 Creating Azure Container Registry..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# 4. Get ACR credentials
echo "🔑 Getting ACR credentials..."
ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "username" --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "passwords[0].value" --output tsv)

echo "ACR Server: $ACR_SERVER"

# 5. Build and push Docker image
echo "🔨 Building Docker image..."
docker build -f Dockerfile.optimized -t $ACR_SERVER/$APP_NAME:latest .

echo "📤 Pushing to Azure Container Registry..."
docker login $ACR_SERVER --username $ACR_USERNAME --password $ACR_PASSWORD
docker push $ACR_SERVER/$APP_NAME:latest

# 6. Create Container Apps Environment
echo "🌍 Creating Container Apps environment..."
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# 7. Create Container App
echo "🚀 Deploying Container App..."
az containerapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image $ACR_SERVER/$APP_NAME:latest \
    --registry-server $ACR_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --target-port 8000 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 5 \
    --cpu 1.0 \
    --memory 2Gi \
    --secrets gemini-api-key="$GEMINI_API_KEY" \
    --env-vars GEMINI_API_KEY=secretref:gemini-api-key LLM_PROVIDER=gemini LLM_MODEL=gemini-1.5-flash ENVIRONMENT=production PORT=8000 LOG_LEVEL=INFO

# 8. Get the application URL
echo "🌐 Getting application URL..."
APP_URL=$(az containerapp show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.ingress.fqdn" \
    --output tsv)

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Application URL: https://$APP_URL"
echo "📊 Health Check: https://$APP_URL/ready"
echo "📖 API Docs: https://$APP_URL/docs"
echo ""
echo "🔧 Useful commands:"
echo "  View logs: az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo "  Scale app: az containerapp update --name $APP_NAME --resource-group $RESOURCE_GROUP --min-replicas 2"
echo "  Delete app: az group delete --name $RESOURCE_GROUP --yes"
