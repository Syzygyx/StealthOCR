#!/usr/bin/env python3
"""
Simple Lambda deployment script for StealthOCR
"""

import os
import subprocess
import shutil
import zipfile
import json
import boto3
from pathlib import Path

def create_simple_deployment_package():
    """Create a simple deployment package for Lambda"""
    print("Creating simple Lambda deployment package...")
    
    # Create deployment directory
    deploy_dir = Path("lambda_simple_deploy")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # Copy the simple lambda function
    shutil.copy("lambda_simple.py", deploy_dir / "lambda_function.py")
    
    # Create zip file
    zip_path = "stealth_ocr_simple_lambda.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(deploy_dir)
                zipf.write(file_path, arcname)
    
    print(f"Simple deployment package created: {zip_path}")
    return zip_path

def deploy_simple_lambda(zip_path, function_name="stealth-ocr-simple"):
    """Deploy the simple package to AWS Lambda"""
    print(f"Deploying simple Lambda function: {function_name}")
    
    # Initialize boto3 client
    lambda_client = boto3.client('lambda')
    
    try:
        # Check if function exists
        try:
            lambda_client.get_function(FunctionName=function_name)
            print("Function exists, updating...")
            
            # Update function code
            with open(zip_path, 'rb') as f:
                response = lambda_client.update_function_code(
                    FunctionName=function_name,
                    ZipFile=f.read()
                )
            
            print(f"Function updated successfully: {response['FunctionArn']}")
            
        except lambda_client.exceptions.ResourceNotFoundException:
            print("Function doesn't exist, creating...")
            
            # Create IAM role for Lambda
            iam_client = boto3.client('iam')
            role_name = f"{function_name}-role"
            
            # Check if role exists
            try:
                role = iam_client.get_role(RoleName=role_name)
                role_arn = role['Role']['Arn']
            except iam_client.exceptions.NoSuchEntityException:
                print("Creating IAM role...")
                
                # Create trust policy
                trust_policy = {
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
                
                # Create role
                role_response = iam_client.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(trust_policy)
                )
                role_arn = role_response['Role']['Arn']
                
                # Attach basic execution policy
                iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
                )
                
                print("IAM role created successfully")
            
            # Create new function
            with open(zip_path, 'rb') as f:
                response = lambda_client.create_function(
                    FunctionName=function_name,
                    Runtime='python3.9',
                    Role=role_arn,
                    Handler='lambda_function.lambda_handler',
                    Code={'ZipFile': f.read()},
                    Description='StealthOCR simple PDF processing service',
                    Timeout=30,  # 30 seconds
                    MemorySize=128,  # 128 MB
                    Environment={
                        'Variables': {}
                    }
                )
            
            print(f"Function created successfully: {response['FunctionArn']}")
    
    except Exception as e:
        print(f"Error deploying to Lambda: {e}")
        return False
    
    return True

def create_api_gateway(function_name="stealth-ocr-simple"):
    """Create API Gateway for the Lambda function"""
    print("Creating API Gateway...")
    
    try:
        # Get Lambda function ARN
        lambda_client = boto3.client('lambda')
        function_info = lambda_client.get_function(FunctionName=function_name)
        lambda_arn = function_info['Configuration']['FunctionArn']
        
        # Create API Gateway
        apigateway_client = boto3.client('apigateway')
        
        # Create REST API
        api_response = apigateway_client.create_rest_api(
            name=f'{function_name}-api',
            description='StealthOCR API Gateway'
        )
        api_id = api_response['id']
        
        # Get root resource
        resources = apigateway_client.get_resources(restApiId=api_id)
        root_resource_id = None
        for resource in resources['items']:
            if resource['path'] == '/':
                root_resource_id = resource['id']
                break
        
        # Create /ocr resource
        resource_response = apigateway_client.create_resource(
            restApiId=api_id,
            parentId=root_resource_id,
            pathPart='ocr'
        )
        resource_id = resource_response['id']
        
        # Create POST method
        apigateway_client.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            authorizationType='NONE'
        )
        
        # Create OPTIONS method for CORS
        apigateway_client.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            authorizationType='NONE'
        )
        
        # Add Lambda integration for POST
        apigateway_client.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
        )
        
        # Add mock integration for OPTIONS
        apigateway_client.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            type='MOCK',
            integrationHttpMethod='OPTIONS',
            requestTemplates={'application/json': '{"statusCode": 200}'}
        )
        
        # Add method responses
        apigateway_client.put_method_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Origin': True
            }
        )
        
        apigateway_client.put_method_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Origin': True
            }
        )
        
        # Add integration responses
        apigateway_client.put_integration_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Origin': "'*'"
            }
        )
        
        apigateway_client.put_integration_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Origin': "'*'"
            }
        )
        
        # Deploy API
        apigateway_client.create_deployment(
            restApiId=api_id,
            stageName='prod'
        )
        
        # Add Lambda permission for API Gateway
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId='apigateway-invoke',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f'arn:aws:execute-api:us-east-1:*:{api_id}/*/*'
        )
        
        # Get API endpoint
        api_endpoint = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod/ocr"
        
        print(f"API Gateway created successfully!")
        print(f"API Endpoint: {api_endpoint}")
        
        return api_endpoint
        
    except Exception as e:
        print(f"Error creating API Gateway: {e}")
        return None

def main():
    """Main deployment function"""
    print("StealthOCR Simple Lambda Deployment")
    print("=" * 40)
    
    # Check if AWS credentials are configured
    try:
        boto3.client('sts').get_caller_identity()
        print("AWS credentials found")
    except Exception as e:
        print(f"AWS credentials not configured: {e}")
        print("Please run: aws configure")
        return
    
    # Create deployment package
    zip_path = create_simple_deployment_package()
    
    # Deploy to Lambda
    if deploy_simple_lambda(zip_path):
        print("Lambda deployment successful!")
        
        # Create API Gateway
        api_endpoint = create_api_gateway()
        
        if api_endpoint:
            print(f"\n🎉 Deployment completed successfully!")
            print(f"API Endpoint: {api_endpoint}")
            print(f"\nNext steps:")
            print(f"1. Update config.js with: {api_endpoint}")
            print(f"2. Push changes to GitHub")
            print(f"3. Test the full functionality")
        else:
            print("Lambda deployed but API Gateway creation failed")
    else:
        print("Lambda deployment failed!")

if __name__ == "__main__":
    main()