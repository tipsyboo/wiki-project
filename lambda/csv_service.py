import json
import base64
import io
import pandas as pd

def lambda_handler(event, context):
    try:
        # 1. Get the HTTP Method
        method = event.get('requestContext', {}).get('http', {}).get('method')
        
        # Handle CORS Preflight (Browser asking "Can I post here?")
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': ''
            }

        # 2. Parse the Body (The CSV Data)
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body).decode('utf-8')

        if not body:
            return {'statusCode': 400, 'body': 'No CSV data found'}

        # 3. Convert CSV to DataFrame
        # We use io.StringIO to treat the string like a file
        df = pd.read_csv(io.StringIO(body))

        # 4. Convert DataFrame to Excel
        # We use io.BytesIO to hold the binary excel file in memory
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        # 5. Encode binary to Base64 for transport
        excel_base64 = base64.b64encode(excel_buffer.getvalue()).decode('utf-8')

        # 6. Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'Content-Disposition': 'attachment; filename="converted_data.xlsx"',
                'Access-Control-Allow-Origin': '*'
            },
            'isBase64Encoded': True,
            'body': excel_base64
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}"),
            'headers': {'Access-Control-Allow-Origin': '*'}
        }
