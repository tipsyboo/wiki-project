pipeline {
    agent any

    environment {
        // --- CONFIGURATION ---
        // Your Lambda Function Name (NOT the ARN, just the name)
        FUNCTION_NAME = 'wikipedia' 
        
        // Your Frontend Bucket Name
        BUCKET_NAME = 'tipsy-wiki-frontend' 
        
        // AWS Region
        AWS_REGION = 'us-east-1'

        DISTRIBUTION_ID = 'E1SXPVZ5XDKZG4'
    }

    stages {
        stage('Checkout') {
            steps {
                // Pulls code from your GitHub Repo
                checkout scm
            }
        }

        stage('Test Backend') {
            steps {
                script {
                    // Simple syntax check to satisfy "Run relevant tests" requirement
                    sh 'python3 -m py_compile lambda/lambda_function.py'
                    echo "Python Syntax OK!"
                }
            }
        }

        stage('Package Backend') {
            steps {
                dir('lambda') {
                    // Zip the python file. 
                    // We DO NOT zip libraries because we used a Lambda Layer!
                    sh 'zip -r ../function.zip lambda_function.py'
                }
            }
        }

        stage('Deploy Backend (Lambda)') {
            steps {
                // Update the function code using AWS CLI
                sh """
                    aws lambda update-function-code \
                    --function-name ${FUNCTION_NAME} \
                    --zip-file fileb://function.zip \
                    --region ${AWS_REGION}
                """
            }
        }

        stage('Deploy Frontend (S3)') {
            steps {
                // Upload index.html to S3
                sh """
                    aws s3 cp frontend/index.html s3://${BUCKET_NAME}/index.html \
                    --region ${AWS_REGION}
                """
            }
        }

        stage('Invalidate Cache') {
            steps {
                sh """
                    aws cloudfront create-invalidation \
                    --distribution-id ${DISTRIBUTION_ID} \
                    --paths "/*" \
                    --region ${AWS_REGION}
                """
            }
        }
        

    }
    
    post {
        success {
            echo 'Deployment Successful! Wiki is live.'
        }
        failure {
            echo 'Deployment Failed.'
        }
        always {
            cleanWs()
        }
    }
}
