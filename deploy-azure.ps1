# Azure deployment script for Windows (PowerShell)
# LLM Query System deployment to Azure Container Apps

param(
    [string]$ResourceGroup = "bajaj-hackathon-rg",
    [string]$Location = "eastus",
    [string]$AcrName = "bajazhackathonacr",
    [string]$AppName = "llm-query-system",
    [string]$ContainerAppEnv = "bajaj-llm-env",
    [string]$GeminiApiKey = $env:GEMINI_API_KEY
)

Write-Host "🔵 Starting Azure deployment for LLM Query System..." -ForegroundColor Blue

# Check if Gemini API key is provided
if (-not $GeminiApiKey) {
    $GeminiApiKey = Read-Host "Enter your Gemini API Key"
}

try {
    # 1. Check Azure CLI login
    Write-Host "📝 Checking Azure login..." -ForegroundColor Yellow
    az account show | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Please login to Azure:" -ForegroundColor Red
        az login
    }

    # 2. Create Resource Group
    Write-Host "📦 Creating resource group..." -ForegroundColor Yellow
    az group create --name $ResourceGroup --location $Location

    # 3. Create Azure Container Registry
    Write-Host "🐳 Creating Azure Container Registry..." -ForegroundColor Yellow
    az acr create --resource-group $ResourceGroup --name $AcrName --sku Basic --admin-enabled true

    # 4. Get ACR credentials
    Write-Host "🔑 Getting ACR credentials..." -ForegroundColor Yellow
    $AcrServer = az acr show --name $AcrName --resource-group $ResourceGroup --query "loginServer" --output tsv
    $AcrUsername = az acr credential show --name $AcrName --resource-group $ResourceGroup --query "username" --output tsv
    $AcrPassword = az acr credential show --name $AcrName --resource-group $ResourceGroup --query "passwords[0].value" --output tsv

    Write-Host "ACR Server: $AcrServer" -ForegroundColor Green

    # 5. Build and push Docker image
    Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
    docker build -f Dockerfile.optimized -t "$AcrServer/$AppName`:latest" .

    Write-Host "📤 Pushing to Azure Container Registry..." -ForegroundColor Yellow
    docker login $AcrServer --username $AcrUsername --password $AcrPassword
    docker push "$AcrServer/$AppName`:latest"

    # 6. Create Container Apps Environment
    Write-Host "🌍 Creating Container Apps environment..." -ForegroundColor Yellow
    az containerapp env create --name $ContainerAppEnv --resource-group $ResourceGroup --location $Location

    # 7. Create Container App
    Write-Host "🚀 Deploying Container App..." -ForegroundColor Yellow
    az containerapp create `
        --name $AppName `
        --resource-group $ResourceGroup `
        --environment $ContainerAppEnv `
        --image "$AcrServer/$AppName`:latest" `
        --registry-server $AcrServer `
        --registry-username $AcrUsername `
        --registry-password $AcrPassword `
        --target-port 8000 `
        --ingress external `
        --min-replicas 1 `
        --max-replicas 5 `
        --cpu 1.0 `
        --memory 2Gi `
        --secrets gemini-api-key="$GeminiApiKey" `
        --env-vars GEMINI_API_KEY=secretref:gemini-api-key LLM_PROVIDER=gemini LLM_MODEL=gemini-1.5-flash ENVIRONMENT=production PORT=8000 LOG_LEVEL=INFO

    # 8. Get the application URL
    Write-Host "🌐 Getting application URL..." -ForegroundColor Yellow
    $AppUrl = az containerapp show --name $AppName --resource-group $ResourceGroup --query "properties.configuration.ingress.fqdn" --output tsv

    Write-Host ""
    Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host "🌐 Application URL: https://$AppUrl" -ForegroundColor Cyan
    Write-Host "📊 Health Check: https://$AppUrl/ready" -ForegroundColor Cyan
    Write-Host "📖 API Docs: https://$AppUrl/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🔧 Useful commands:" -ForegroundColor Yellow
    Write-Host "  View logs: az containerapp logs show --name $AppName --resource-group $ResourceGroup --follow"
    Write-Host "  Scale app: az containerapp update --name $AppName --resource-group $ResourceGroup --min-replicas 2"
    Write-Host "  Delete app: az group delete --name $ResourceGroup --yes"

} catch {
    Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
