"""
Deployment script for AWS Lambda function
"""

import os
import subprocess
import shutil
import zipfile
import json
import boto3
from pathlib import Path

def create_deployment_package():
    """Create deployment package for Lambda"""
    print("Creating Lambda deployment package...")
    
    # Create deployment directory
    deploy_dir = Path("lambda_deploy")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # Copy source code
    src_dir = deploy_dir / "src"
    src_dir.mkdir()
    
    # Copy stealth_ocr.py
    shutil.copy("src/stealth_ocr.py", src_dir / "stealth_ocr.py")
    
    # Copy lambda function
    shutil.copy("lambda_function.py", deploy_dir / "lambda_function.py")
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.run([
        "pip", "install", "-r", "requirements_lambda.txt", 
        "-t", str(deploy_dir)
    ], check=True)
    
    # Create zip file
    zip_path = "stealth_ocr_lambda.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(deploy_dir)
                zipf.write(file_path, arcname)
    
    print(f"Deployment package created: {zip_path}")
    return zip_path

def deploy_to_lambda(zip_path, function_name="stealth-ocr-processor"):
    """Deploy the package to AWS Lambda"""
    print(f"Deploying to Lambda function: {function_name}")
    
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
            
            # Create new function
            with open(zip_path, 'rb') as f:
                response = lambda_client.create_function(
                    FunctionName=function_name,
                    Runtime='python3.9',
                    Role='arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role',  # Update this
                    Handler='lambda_function.lambda_handler',
                    Code={'ZipFile': f.read()},
                    Description='StealthOCR PDF text extraction service',
                    Timeout=300,  # 5 minutes
                    MemorySize=3008,  # Maximum memory for better performance
                    Environment={
                        'Variables': {
                            'TESSERACT_PATH': '/opt/python/bin/tesseract'
                        }
                    }
                )
            
            print(f"Function created successfully: {response['FunctionArn']}")
    
    except Exception as e:
        print(f"Error deploying to Lambda: {e}")
        return False
    
    return True

def create_lambda_layer():
    """Create Lambda layer with Tesseract and other dependencies"""
    print("Creating Lambda layer...")
    
    # This would typically involve:
    # 1. Downloading Tesseract binaries for Lambda
    # 2. Creating a layer package
    # 3. Uploading to Lambda
    
    # For now, we'll use a pre-built layer
    layer_arn = "arn:aws:lambda:us-east-1:123456789012:layer:tesseract:1"
    print(f"Using Tesseract layer: {layer_arn}")
    return layer_arn

def main():
    """Main deployment function"""
    print("StealthOCR Lambda Deployment")
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
    zip_path = create_deployment_package()
    
    # Deploy to Lambda
    if deploy_to_lambda(zip_path):
        print("Deployment successful!")
        print("\nNext steps:")
        print("1. Update the Lambda function's IAM role with necessary permissions")
        print("2. Add Tesseract layer to the function")
        print("3. Test the function")
        print("4. Update the frontend to use the Lambda API endpoint")
    else:
        print("Deployment failed!")

if __name__ == "__main__":
    main()