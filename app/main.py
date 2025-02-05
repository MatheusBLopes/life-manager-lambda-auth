import json
import os
import boto3
from routes.login import Login

from aws_lambda_powertools import Logger

logger = Logger(service="LifeManagerLambdaAuth")

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    try:
        client_id = os.environ["CLIENT_ID"]

        resource = event.get('resource', '')
        http_method = event.get('httpMethod', '')
        body = event.get('body', "")

        logger.info(f"Received event with resource: {resource}, method: {http_method}")

        if body:
            body = json.loads(body)
            logger.debug(f"Request body: {body}")
    except Exception as e:
        logger.error(f"Error reading environment variables: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal Server Error'})
        }

    try:

        client = boto3.client('cognito-idp')

        if resource == '/login':
            logger.info("Iniciando fluxo de login")
            login_route = Login(client, body, client_id)
            result = login_route.login()
            return result

        logger.warning(f"Resource {resource} not found")
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Not Found'})
        }

    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal Server Error'})
        }
