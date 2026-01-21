import sys
import os
import json
from unittest.mock import MagicMock, patch

# 1. Mock libraries BEFORE importing the lambda function
# This prevents the script from trying to connect to AWS or Wikipedia immediately
sys.modules["boto3"] = MagicMock()
sys.modules["wikipedia"] = MagicMock()

# 2. Add the lambda folder to the path so we can import it
sys.path.append(os.path.join(os.path.dirname(__file__), '../lambda'))

# 3. Import the function code
import lambda_function

def test_lambda_handler_success():
    """
    Test that the lambda function returns 200 and the correct summary
    when Wikipedia successfully finds a topic.
    """
    
    # SETUP: Define what our "Fake" Wikipedia should return
    with patch('lambda_function.wikipedia.summary') as mock_wiki, \
         patch('lambda_function.boto3.client') as mock_s3:
        
        # Tell the fake wikipedia to return "Fake Summary" when called
        mock_wiki.return_value = "This is a fake summary about DevOps."
        
        # Create a fake event (simulating a URL visit)
        event = {"queryStringParameters": {"topic": "DevOps"}}
        
        # EXECUTE: Run the function
        response = lambda_function.lambda_handler(event, None)
        
        # VERIFY: Did it return success?
        assert response['statusCode'] == 200
        
        # VERIFY: Did the body contain our fake summary?
        body_data = json.loads(response['body'])
        assert "Fake Summary" in body_data
        
        # VERIFY: Did it try to upload to S3?
        mock_s3.return_value.put_object.assert_called_once()

def test_lambda_handler_no_topic():
    """
    Test that the function fails gracefully if no topic is provided.
    """
    event = {"queryStringParameters": {}} # Empty query
    
    response = lambda_function.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    assert "Missing 'topic'" in response['body']
