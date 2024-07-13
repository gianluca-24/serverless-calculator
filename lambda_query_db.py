import json
import boto3
import time

def lambda_handler(event, context):
  time.sleep(0.5)
  equation = event.get("queryStringParameters", {}).get("equation")
 
  if not equation:
    return {
        "statusCode": 400,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        "body": json.dumps({"message": "Missing required parameter: equation"})
    }

  # Configure DynamoDB
  dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

  # Define the table name and attribute names 
  table_name = 'equation-solver'
  equation_attribute = 'equation_id'
  solution_attribute = 'solution'

  try:
    table = dynamodb.Table(table_name)
    response = table.query(
        KeyConditionExpression=f"#{equation_attribute} = :equationVal",
        ExpressionAttributeNames={"#" + equation_attribute: equation_attribute},
        ExpressionAttributeValues={":equationVal": equation}
    )
  except Exception as e:
    print(f"Error querying DynamoDB: {e}")
    return {
        "statusCode": 500,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        "body": json.dumps({"message": "Internal server error"})
    }

  items = response.get('Items', [])

  if not items:
    return {
        "statusCode": 404,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        "body": json.dumps({"message": "Solution not found for equation"})
    }
    
  solution = items[0][solution_attribute]
  print('Solution: ' +solution)
  return {
      "statusCode": 200,
      'headers': {
            'Access-Control-Allow-Origin': '*', 
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
      "body": json.dumps({"solution": solution})
  }

