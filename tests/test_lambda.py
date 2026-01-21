import sys
import os
import json
from unittest.mock import MagicMock, patch

# 1. Mock libraries BEFORE importing the lambda function
sys.modules["boto3"] = MagicMock()
sys.modules["wikipedia"] = MagicMock()

# 2. Add the lambda folder to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../lambda'))

# 3. Import the function code
import lambda_function

def test_lambda_handler_success():
    """
    Test that the lambda returns 200 and a success message.
    """
    with patch('lambda_function.wikipedia.summary') as mock_wiki, \
         patch('lambda_function.boto3.client') as mock_s3:
        
        # Setup the fake wikipedia response (used for the email)
        mock_wiki.return_value = "This is a fake summary."
        
        # Setup the fake input event
        event = {"queryStringParameters": {"topic": "DevOps"}}
        
        # Run the function
        response = lambda_function.lambda_handler(event, None)
        
        # VERIFY: Status is 200 OK
        assert response['statusCode'] == 200
        
        # VERIFY: The browser gets the success message (NOT the summary)
        body_data = json.loads(response['body'])
        assert "Successfully added" in body_data
        
        # VERIFY: S3 upload was triggered
        mock_s3.return_value.put_object.assert_called_once()

def test_lambda_handler_no_topic():
    """
    Test that the function returns an error (500) if no topic is sent.
    """
    # Empty query parameters
    event = {"queryStringParameters": {}} 
    
    response = lambda_function.lambda_handler(event, None)
    
    # Your current code catches the error and returns 500
    assert response['statusCode'] == 500
