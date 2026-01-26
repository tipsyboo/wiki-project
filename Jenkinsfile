pipeline {
    agent any

    environment {
        // --- CONFIGURATION ---
        FUNCTION_NAME = 'wikipedia' 
        BUCKET_NAME = 'tipsy-wiki-frontend' 
        AWS_REGION = 'us-east-1'
        DISTRIBUTION_ID = 'E1SXPVZ5XDKZG4'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // 1. TESTS: Run only if ANY python code or test file changes
        stage('Test Backend') {
            when {
                anyOf {
                    changeset 'lambda/*.py'
                    changeset 'tests/**'
                    changeset 'requirements-test.txt'
                }
            }
            steps {
                script {
                    sh 'python3 -m venv venv'
                    sh '. venv/bin/activate && pip3 install -r requirements-test.txt'
                    sh '. venv/bin/activate && python3 -m pytest tests/ -v'
                }
            }
        }

        // 2. WIKI SERVICE: Runs only if 'lambda_function.py' changes
        stage('Deploy Wiki Service') {
            when {
                changeset 'lambda/lambda_function.py'
            }
            steps {
                dir('lambda') {
                    // Zip only this function
                    sh 'zip -r ../function.zip lambda_function.py'
                }
                // Deploy
                sh """
                    aws lambda update-function-code \
                    --function-name ${FUNCTION_NAME} \
                    --zip-file fileb://function.zip \
                    --region ${AWS_REGION}
                """
                echo "Updated Wiki Lambda"
            }
        }

        // 3. CSV SERVICE: Runs only if 'csv_service.py' changes
        stage('Deploy CSV Service') {
            when {
                changeset 'lambda/csv_service.py'
            }
            steps {
                dir('lambda') {
                    // Zip only this function
                    sh 'zip -r ../csv-service.zip csv_service.py'
                }
                // Deploy
                sh """
                    aws lambda update-function-code \
                    --function-name csv-converter \
                    --zip-file fileb://csv-service.zip \
                    --region ${AWS_REGION}
                """
                echo "Updated CSV Lambda"
            }
        }

        // 4. FRONTEND: Runs only if the 'frontend' folder changes
        stage('Deploy Frontend') {
            when {
                changeset 'frontend/**'
            }
            steps {
                // Upload
                sh """
                    aws s3 cp frontend/index.html s3://${BUCKET_NAME}/index.html \
                    --region ${AWS_REGION}
                """
                
                // Invalidate Cache (Only needed if frontend changed)
                sh """
                    aws cloudfront create-invalidation \
                    --distribution-id ${DISTRIBUTION_ID} \
                    --paths "/*" \
                    --region ${AWS_REGION}
                """
                echo "Updated S3 and Invalidated CloudFront"
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline finished successfully.'
        }
        failure {
            echo 'Pipeline Failed.'
        }
        always {
            cleanWs()
        }
    }
}
