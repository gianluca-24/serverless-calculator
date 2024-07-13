import json
import boto3
import sympy
from sympy import solve_univariate_inequality, solve, Symbol, sympify, Eq, And
import re
import datetime


def to_dynamo(id, equation, solution=None):
  """Writes the equation and solution to a DynamoDB table.

  Args:
      equation: The equation string.
      solution: The solved equation (optional).
  """
  try:
      
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('equation-solver')

    # Create timestamp
    timestamp = datetime.datetime.now().isoformat()

    item = {
        'equation_id': id,  # Generate unique ID
        'equation': equation,
        'timestamp': timestamp,
    }

    if solution:
        if type(solution) == sympy.And:
            item['solution'] = str(solution)
        else:
            # item['solution'] = decimal.Decimal(float(solution[0]))
            item['solution'] = ",".join(map(str, solution))
    # Write data to DynamoDB
    table.put_item(Item=item)

    print(f"Equation and solution written to DynamoDB at {timestamp}")
    return
  except Exception as e:
      print(f"An error occurred: {e}")
      return

def process_image(bucket_name, object_key, rekognition_client):
    """Processes an image from S3 using Rekognition and logs results."""
    s3_client = boto3.client('s3')

    try:
        s3_response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        image_data = s3_response['Body'].read()

        # Use Rekognition Text Detection
        response = rekognition_client.detect_text(Image={'Bytes': image_data})
        # Extract and format detected text
        detected_text = ""
        for text_detection in response['TextDetections']:
            if text_detection['Type'] == 'LINE':
                detected_text += text_detection['DetectedText']
        if not detected_text:
            detected_text = "No text detected in the image." 
        return detected_text.lower()


    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def solve_equation(equation):
  """
  This function detects the number of variables and solves the equation accordingly.

  Args:
      equation: The equation to be solved (SymPy expression).

  Returns:
      A set of solutions (solveset) or a list of solutions (solve) depending on the number of variables.
  """
  try:
    expr = re.sub(r'(\d)\s*([a-zA-Z])', r'\1*\2', equation)
    if '=' in expr:
        left, right = expr.split('=')
        eq =  Eq(sympify(left.strip()), sympify(right.strip()))
        return solve(eq,Symbol('x'))
    else:
        solution = solve_univariate_inequality(sympify(expr),Symbol('x'), relational=True)
        return solution
  except Exception as e:
      print('Error: ' + str(e))
      return None

def lambda_handler(event, context):
    """
    This function is triggered by S3 events (image uploads) and sends image details to an SQS queue.
    """
    rekognition_client = boto3.client('rekognition')
    s3_client = boto3.client('s3')
    
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        
        try:
        
            # retrieve the equation through rekognition
            equation = process_image(bucket_name, object_key, rekognition_client)
            print(equation)
            if equation:
                print(f"Output of image processing: {equation}")
                sol = solve_equation(str(equation))
                if sol:
                    print(f"Solution: {sol}")
                    to_dynamo(object_key,equation,sol)
                # if there is no text, not solve it
                else:
                    print(f"No solution found.")
            # if there is no text, not solve it
            else:
                print(f"Image processing for {object_key} failed.")
            
        except Exception as e:
            print(str(e))
        break
