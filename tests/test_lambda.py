import sys
import os
import json
from unittest.mock import MagicMock, patch

# 1. Setup the main Boto3 mock BEFORE import
mock_boto3 = MagicMock()
sys.modules["boto3"] = mock_boto3
sys.modules["wikipedia"] = MagicMock()

# 2. Add path and import
sys.path.append(os.path.join(os.path.dirname(__file__), '../lambda'))
import lambda_function

def test_lambda_handler_success():
    """
    Test that the lambda returns 200 and a success message.
    """
    # We only patch wikipedia here. 
    # For S3, we rely on the global 'mock_boto3' we created above.
    with patch('lambda_function.wikipedia.summary') as mock_wiki:
        
        # Setup fake wiki response
        mock_wiki.return_value = "This is a fake summary."
        
        # Setup fake event
        event = {"queryStringParameters": {"topic": "DevOps"}}
        
        # Run function
        response = lambda_function.lambda_handler(event, None)
        
        # VERIFY: Status 200
        assert response['statusCode'] == 200
        
        # VERIFY: Success message
        body_data = json.loads(response['body'])
        assert "Successfully added" in body_data
        
        # VERIFY: S3 upload was triggered
        # We check the global mock. .client() returns the mock client, 
        # and we check if .put_object() was called on it.
        mock_boto3.client.return_value.put_object.assert_called()

def test_lambda_handler_no_topic():
    """
    Test that the function returns an error (500) if no topic is sent.
    """
    event = {"queryStringParameters": {}} 
    response = lambda_function.lambda_handler(event, None)
    
    # Expect 500 because your code catches the KeyError/IndexError
    assert response['statusCode'] == 500
