#!/bin/bash

# StealthOCR Lambda Deployment Script

set -e

echo "StealthOCR Lambda Deployment"
echo "============================"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "AWS credentials not configured. Please run: aws configure"
    exit 1
fi

# Get AWS account ID and region
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)
if [ -z "$REGION" ]; then
    REGION="us-east-1"
fi

echo "AWS Account ID: $ACCOUNT_ID"
echo "AWS Region: $REGION"

# Set environment (default to dev)
ENVIRONMENT=${1:-dev}
FUNCTION_NAME="stealth-ocr-$ENVIRONMENT"
STACK_NAME="stealth-ocr-$ENVIRONMENT"

echo "Environment: $ENVIRONMENT"
echo "Function Name: $FUNCTION_NAME"
echo "Stack Name: $STACK_NAME"

# Create deployment package
echo "Creating deployment package..."
rm -rf lambda_deploy
mkdir -p lambda_deploy/src

# Copy source files
cp src/stealth_ocr.py lambda_deploy/src/
cp lambda_function.py lambda_deploy/
cp requirements_lambda.txt lambda_deploy/

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements_lambda.txt -t lambda_deploy/ --no-deps

# Install specific versions for Lambda compatibility
pip install pytesseract==0.3.13 -t lambda_deploy/
pip install Pillow==10.0.1 -t lambda_deploy/
pip install opencv-python-headless==4.8.1.78 -t lambda_deploy/
pip install easyocr==1.7.2 -t lambda_deploy/
pip install numpy==1.24.3 -t lambda_deploy/
pip install scikit-image==0.21.0 -t lambda_deploy/
pip install imutils==0.5.4 -t lambda_deploy/
pip install PyPDF2==3.0.1 -t lambda_deploy/
pip install pdf2image==1.16.3 -t lambda_deploy/
pip install torch==2.0.1 -t lambda_deploy/
pip install torchvision==0.15.2 -t lambda_deploy/
pip install python-dotenv==1.0.0 -t lambda_deploy/

# Create zip file
echo "Creating deployment package..."
cd lambda_deploy
zip -r ../stealth_ocr_lambda.zip .
cd ..

echo "Deployment package created: stealth_ocr_lambda.zip"

# Deploy using AWS CLI
echo "Deploying to AWS Lambda..."

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME &> /dev/null; then
    echo "Function exists, updating code..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://stealth_ocr_lambda.zip
else
    echo "Function doesn't exist, creating..."
    
    # Create IAM role for Lambda
    ROLE_NAME="StealthOCRLambdaRole-$ENVIRONMENT"
    
    # Check if role exists
    if ! aws iam get-role --role-name $ROLE_NAME &> /dev/null; then
        echo "Creating IAM role..."
        
        # Create trust policy
        cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
        
        # Create role
        aws iam create-role \
            --role-name $ROLE_NAME \
            --assume-role-policy-document file://trust-policy.json
        
        # Attach basic execution policy
        aws iam attach-role-policy \
            --role-name $ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        
        # Wait for role to be ready
        echo "Waiting for IAM role to be ready..."
        sleep 10
        
        rm trust-policy.json
    fi
    
    # Get role ARN
    ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
    
    # Create function
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.9 \
        --role $ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://stealth_ocr_lambda.zip \
        --description "StealthOCR PDF text extraction service" \
        --timeout 300 \
        --memory-size 3008 \
        --environment Variables='{TESSERACT_PATH=/opt/python/bin/tesseract}'
fi

# Create API Gateway
echo "Creating API Gateway..."
API_ID=$(aws apigateway get-rest-apis --query "items[?name=='$FUNCTION_NAME'].id" --output text)

if [ -z "$API_ID" ] || [ "$API_ID" = "None" ]; then
    echo "Creating new API Gateway..."
    API_ID=$(aws apigateway create-rest-api \
        --name $FUNCTION_NAME \
        --description "StealthOCR API" \
        --query 'id' --output text)
fi

echo "API Gateway ID: $API_ID"

# Get root resource ID
ROOT_RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query 'items[?path==`/`].id' --output text)

# Create /ocr resource
OCR_RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_RESOURCE_ID \
    --path-part ocr \
    --query 'id' --output text)

# Create POST method
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $OCR_RESOURCE_ID \
    --http-method POST \
    --authorization-type NONE

# Create OPTIONS method for CORS
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $OCR_RESOURCE_ID \
    --http-method OPTIONS \
    --authorization-type NONE

# Get Lambda function ARN
LAMBDA_ARN=$(aws lambda get-function --function-name $FUNCTION_NAME --query 'Configuration.FunctionArn' --output text)

# Add Lambda integration for POST
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $OCR_RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations"

# Add Lambda integration for OPTIONS
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $OCR_RESOURCE_ID \
    --http-method OPTIONS \
    --type MOCK \
    --integration-http-method OPTIONS \
    --request-templates '{"application/json": "{\"statusCode\": 200}"}'

# Add method responses
aws apigateway put-method-response \
    --rest-api-id $API_ID \
    --resource-id $OCR_RESOURCE_ID \
    --http-method POST \
    --status-code 200 \
    --response-parameters method.response.header.Access-Control-Allow-Origin=false

aws apigateway put-method-response \
    --rest-api-id $API_ID \
    --resource-id $OCR_RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters method.response.header.Access-Control-Allow-Origin=false

# Add integration responses
aws apigateway put-integration-response \
    --rest-api-id $API_ID \
    --resource-id $OCR_RESOURCE_ID \
    --http-method POST \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Origin":"'"'"'*'"'"'"}'

aws apigateway put-integration-response \
    --rest-api-id $API_ID \
    --resource-id $OCR_RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Origin":"'"'"'*'"'"'"}'

# Deploy API
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod

# Add Lambda permission for API Gateway
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*"

# Get API endpoint
API_ENDPOINT="https://$API_ID.execute-api.$REGION.amazonaws.com/prod/ocr"

echo ""
echo "Deployment completed successfully!"
echo "================================="
echo "Function Name: $FUNCTION_NAME"
echo "API Endpoint: $API_ENDPOINT"
echo ""
echo "Test the function:"
echo "curl -X POST $API_ENDPOINT \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"pdf_data\": \"base64_encoded_pdf_data\"}'"
echo ""
echo "Update your frontend to use: $API_ENDPOINT"

# Clean up
rm -rf lambda_deploy
rm stealth_ocr_lambda.zip

echo "Cleanup completed."