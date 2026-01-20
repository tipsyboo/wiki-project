import json
import boto3
import os
import wikipedia
from botocore.exceptions import ClientError

# test1
# Initialize AWS clients
s3 = boto3.client('s3')
sns = boto3.client('sns')

# Get configuration from Environment Variables (Best Practice)
BUCKET_NAME = os.environ.get('BUCKET_NAME')  # e.g., "my-wiki-data-bucket"
FILE_KEY = "wiki_info.txt"                   # The file name in S3
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN') # The SNS Topic for notifications

def lambda_handler(event, context):
    try:
        # 1. Parse Input (Handle both direct JSON and API Gateway Query Params)
        # If running from API Gateway URL: ?topic=Python
        if 'queryStringParameters' in event and event['queryStringParameters']:
            topic = event['queryStringParameters'].get('topic')
        # If running from Test Event in Console: {"topic": "Python"}
        else:
            topic = event.get('topic')

        if not topic:
            raise ValueError("No topic provided in request.")

        # 2. Fetch 'Top' section from Wikipedia
        # The .summary() function fetches the top section by default
        print(f"Fetching summary for: {topic}")
        wiki_summary = wikipedia.summary(topic, auto_suggest=False)
        
        # Prepare the text entry with a separator
        new_entry = f"\n--- TOPIC: {topic} ---\n{wiki_summary}\n"

        # 3. Update S3 File (Read -> Append -> Write)
        current_content = ""
        try:
            # Try to get the existing file
            response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
            current_content = response['Body'].read().decode('utf-8')
        except s3.exceptions.NoSuchKey:
            # If file doesn't exist yet, that's fine, we start fresh
            print("File does not exist yet. Creating new.")

        # Append new content
        updated_content = current_content + new_entry

        # Save back to S3
        s3.put_object(Bucket=BUCKET_NAME, Key=FILE_KEY, Body=updated_content)

        # 4. Notify User via SNS (Success)
        message = f"Successfully added '{topic}' to the wiki file."
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="Wiki Script Success",
            Message=message
        )

        return {
            'statusCode': 200,
            'body': json.dumps(message)
        }

    except Exception as e:
        # 5. Notify User via SNS (Failure)
        error_msg = f"Script failed for topic '{topic if 'topic' in locals() else 'Unknown'}': {str(e)}"
        print(error_msg)
        
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="Wiki Script FAILURE",
            Message=error_msg
        )

        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
