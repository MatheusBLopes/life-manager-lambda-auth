import json

class Login():
    def __init__(self, boto_client, payload, cognito_client_id):
        self.boto_client = boto_client
        self.payload = payload
        self.cognito_client_id = cognito_client_id
    
    def login(self):
        try:
            username = self.payload['username']
            password = self.payload['password']
        except KeyError as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Please, provide username and password correctly'})
            }

        try:
            response = self.boto_client.initiate_auth(
                ClientId=self.cognito_client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            return {
                'statusCode': 200,
                'body': json.dumps(response['AuthenticationResult'])
            }
        except self.boto_client.exceptions.NotAuthorizedException:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Invalid username or password'})
            }
        except self.boto_client.exceptions.UserNotFoundException:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'User not found'})
            }
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': str(e)})
            }
